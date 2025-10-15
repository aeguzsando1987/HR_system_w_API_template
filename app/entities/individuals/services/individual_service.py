"""
Individual Service - Lógica de negocio
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.entities.individuals.repositories.individual_repository import IndividualRepository
from app.entities.individuals.models.individual import Individual
from app.shared.exceptions import EntityNotFoundError, EntityValidationError, BusinessRuleError, EntityAlreadyExistsError
from app.shared.base_repository import BaseRepository
from database import User
from auth import hash_password


class IndividualService:
    """Service para lógica de negocio de Individuals"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = IndividualRepository(db)

        # Repositorios de otras entidades
        from app.entities.countries.repositories.country_repository import CountryRepository
        from app.entities.states.repositories.state_repository import StateRepository

        self.country_repository = CountryRepository(db)
        self.state_repository = StateRepository(db)
        self.user_repository = BaseRepository(User, db)

    # ==================== VALIDACIONES ====================

    def _validate_individual_data(self, data: Dict[str, Any], is_update: bool = False) -> None:
        """
        Valida los datos del Individual.

        Args:
            data: Datos a validar
            is_update: Si es actualización o creación

        Raises:
            EntityValidationError: Si los datos no son válidos
            EntityNotFoundError: Si una FK no existe
            BusinessRuleError: Si hay violaciones de reglas de negocio
        """
        # Validar country_id si se provee
        if "country_id" in data and data["country_id"] is not None:
            country = self.country_repository.get_by_id(data["country_id"])
            if not country:
                raise EntityNotFoundError("Country", data["country_id"])
            if not country.is_active or country.is_deleted:
                raise BusinessRuleError(
                    f"El Country {data['country_id']} no está activo",
                    details={"country_id": data["country_id"]}
                )

        # Validar state_id si se provee
        if "state_id" in data and data["state_id"] is not None:
            state = self.state_repository.get_by_id(data["state_id"])
            if not state:
                raise EntityNotFoundError("State", data["state_id"])
            if not state.is_active or state.is_deleted:
                raise BusinessRuleError(
                    f"El State {data['state_id']} no está activo",
                    details={"state_id": data["state_id"]}
                )

        # Validar user_id si se provee (solo en update)
        if is_update and "user_id" in data and data["user_id"] is not None:
            user = self.user_repository.get_by_id(data["user_id"])
            if not user:
                raise EntityNotFoundError("User", data["user_id"])

            # Verificar que el user no esté asociado a otro Individual
            existing_individual = self.repository.get_by_user_id(data["user_id"])
            if existing_individual:
                raise BusinessRuleError(
                    f"El User {data['user_id']} ya está asociado a otro Individual",
                    details={"user_id": data["user_id"], "individual_id": existing_individual.id}
                )

    def _check_unique_constraints(
        self,
        data: Dict[str, Any],
        individual_id: Optional[int] = None
    ) -> None:
        """
        Verifica constraints de unicidad.

        Args:
            data: Datos a verificar
            individual_id: ID del Individual (None si es creación)

        Raises:
            EntityAlreadyExistsError: Si hay conflicto de unicidad
        """
        # Email único
        if "email" in data:
            existing = self.repository.get_by_email(data["email"])
            if existing and (not individual_id or existing.id != individual_id):
                raise EntityAlreadyExistsError("Individual", "email", data["email"])

        # Document number único
        if "document_number" in data and data["document_number"]:
            existing = self.repository.get_by_document(data["document_number"])
            if existing and (not individual_id or existing.id != individual_id):
                raise EntityAlreadyExistsError("Individual", "document_number", data["document_number"])

        # CURP único
        if "curp" in data and data["curp"]:
            existing = self.repository.get_by_curp(data["curp"])
            if existing and (not individual_id or existing.id != individual_id):
                raise EntityAlreadyExistsError("Individual", "curp", data["curp"])

        # Payroll number único
        if "payroll_number" in data and data["payroll_number"]:
            existing = self.repository.get_by_payroll_number(data["payroll_number"])
            if existing and (not individual_id or existing.id != individual_id):
                raise EntityAlreadyExistsError("Individual", "payroll_number", data["payroll_number"])

    # ==================== CRUD OPERATIONS ====================

    def get_individual_by_id(self, individual_id: int) -> Individual:
        """
        Obtiene un Individual por ID.

        Args:
            individual_id: ID del Individual

        Returns:
            Individual

        Raises:
            EntityNotFoundError: Si no se encuentra el Individual
        """
        individual = self.repository.get_by_id(individual_id)
        if not individual:
            raise EntityNotFoundError("Individual", individual_id)
        return individual

    def create_individual(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> Individual:
        """
        Crea un nuevo Individual (sin User asociado).

        Args:
            data: Datos del Individual
            created_by: ID del usuario que crea

        Returns:
            Individual creado

        Raises:
            EntityValidationError: Si los datos no son válidos
            EntityAlreadyExistsError: Si hay conflictos de unicidad
            BusinessRuleError: Si hay violaciones de reglas de negocio
        """
        # Validar datos
        self._validate_individual_data(data)

        # Verificar unicidad
        self._check_unique_constraints(data)

        # Agregar auditoría
        if created_by:
            data["created_by"] = created_by

        # Crear Individual
        return self.repository.create(data)

    def create_individual_with_user(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> Individual:
        """
        Crea un Individual + User en una transacción atómica.

        Este es el método principal para registrar personas con acceso al sistema.

        Args:
            data: Datos del Individual + User
            created_by: ID del usuario que crea

        Returns:
            Individual creado con User asociado

        Raises:
            EntityValidationError: Si los datos no son válidos
            EntityAlreadyExistsError: Si hay conflictos de unicidad
            BusinessRuleError: Si hay violaciones de reglas de negocio

        Example:
            data = {
                # Individual fields
                "first_name": "Juan",
                "last_name": "Pérez",
                "email": "juan.perez@empresa.com",
                "phone": "+52-555-1234",
                # User fields
                "user_email": "juan.perez@sistema.com",
                "user_password": "SecurePass123!",
                "user_role": 4
            }
        """
        try:
            # Extraer datos del User
            user_email = data.pop("user_email")
            user_password = data.pop("user_password")
            user_role = data.pop("user_role")

            # Validar datos del Individual
            self._validate_individual_data(data)

            # Verificar unicidad del Individual
            self._check_unique_constraints(data)

            # Verificar que user_email no exista
            existing_user = self.db.query(User).filter(User.email == user_email).first()
            if existing_user:
                raise EntityAlreadyExistsError("User", "email", user_email)

            # ==================== TRANSACCIÓN ATÓMICA ====================

            # 1. Crear User
            # User already imported at top
            user = User(
                email=user_email,
                password_hash=hash_password(user_password),
                role=user_role
            )
            self.db.add(user)
            self.db.flush()  # Obtener user.id sin hacer commit

            # 2. Crear Individual vinculado al User
            data["user_id"] = user.id
            if created_by:
                data["created_by"] = created_by

            individual = Individual(**data)
            self.db.add(individual)

            # 3. Commit de la transacción completa
            self.db.commit()
            self.db.refresh(individual)

            return individual

        except Exception as e:
            # Rollback si algo falla
            self.db.rollback()
            raise e

    def update_individual(
        self,
        individual_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> Individual:
        """
        Actualiza un Individual existente.

        Args:
            individual_id: ID del Individual a actualizar
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            Individual actualizado

        Raises:
            EntityNotFoundError: Si no se encuentra el Individual
            EntityValidationError: Si los datos no son válidos
            EntityAlreadyExistsError: Si hay conflictos de unicidad
            BusinessRuleError: Si hay violaciones de reglas de negocio
        """
        # Validar que el individual existe
        individual = self.get_individual_by_id(individual_id)

        # Validar datos de entrada
        self._validate_individual_data(data, is_update=True)

        # Verificar unicidad
        self._check_unique_constraints(data, individual_id)

        # Agregar auditoría
        if updated_by:
            data["updated_by"] = updated_by

        # Actualizar
        return self.repository.update(individual_id, data)

    def delete_individual(
        self,
        individual_id: int,
        deleted_by: Optional[int] = None
    ) -> bool:
        """
        Elimina un Individual (soft delete).

        Args:
            individual_id: ID del Individual a eliminar
            deleted_by: ID del usuario que elimina

        Returns:
            True si se eliminó correctamente

        Raises:
            EntityNotFoundError: Si no se encuentra el Individual
            BusinessRuleError: Si tiene employees activos asociados
        """
        # Validar que el individual existe
        individual = self.get_individual_by_id(individual_id)

        # Validar que no tiene employees activos
        if self.repository.has_active_employees(individual_id):
            raise BusinessRuleError(
                "No se puede eliminar un Individual con empleados activos asociados",
                details={"individual_id": individual_id}
            )

        # Soft delete: marcar deleted_by
        if deleted_by:
            self.repository.update(individual_id, {
                "is_active": False,
                "is_deleted": True,
                "deleted_by": deleted_by,
                "deleted_at": datetime.utcnow()
            })
        else:
            self.repository.delete(individual_id, soft_delete=True)

        return True

    # ==================== OPERACIONES ADICIONALES ====================

    def search_individuals(self, query: str, limit: int = 50) -> List[Individual]:
        """
        Busca individuals por nombre, apellido o email.

        Args:
            query: Texto a buscar
            limit: Número máximo de resultados

        Returns:
            Lista de individuals que coinciden con la búsqueda
        """
        return self.repository.search(query, limit)

    def get_individual_by_document(self, document_number: str) -> Optional[Individual]:
        """
        Obtiene un Individual por número de documento.

        Args:
            document_number: Número de documento

        Returns:
            Individual o None si no existe
        """
        return self.repository.get_by_document(document_number)

    def get_individual_by_curp(self, curp: str) -> Optional[Individual]:
        """
        Obtiene un Individual por CURP.

        Args:
            curp: CURP

        Returns:
            Individual o None si no existe
        """
        return self.repository.get_by_curp(curp)

    def get_individuals_by_country(self, country_id: int, active_only: bool = True) -> List[Individual]:
        """
        Obtiene todos los individuals de un país.

        Args:
            country_id: ID del país
            active_only: Si True, solo retorna activos

        Returns:
            Lista de individuals del país
        """
        return self.repository.get_by_country(country_id, active_only)

    def get_individuals_by_state(self, state_id: int, active_only: bool = True) -> List[Individual]:
        """
        Obtiene todos los individuals de un estado.

        Args:
            state_id: ID del estado
            active_only: Si True, solo retorna activos

        Returns:
            Lista of individuals del estado
        """
        return self.repository.get_by_state(state_id, active_only)