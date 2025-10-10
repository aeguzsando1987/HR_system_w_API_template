"""
Service: Branch

Lógica de negocio y validaciones para Branch.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
from math import ceil

from app.entities.branches.repositories.branch_repository import BranchRepository
from app.entities.branches.models.branch import Branch
from app.entities.companies.repositories.company_repository import CompanyRepository
from app.entities.countries.repositories.country_repository import CountryRepository
from app.entities.states.repositories.state_repository import StateRepository
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)


class BranchService:
    """Servicio para lógica de negocio de Branch."""

    def __init__(self, db: Session):
        """Inicializa el servicio con el repositorio."""
        self.db = db
        self.repository = BranchRepository(db)
        self.company_repository = CompanyRepository(db)
        self.country_repository = CountryRepository(db)
        self.state_repository = StateRepository(db)

    # ==================== OPERACIONES CRUD ====================

    def create_branch(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> Branch:
        """
        Crea una nueva Branch con validaciones de negocio.

        Args:
            data: Datos de la Branch
            created_by: ID del usuario que crea el registro

        Returns:
            Branch creada

        Raises:
            EntityValidationError: Si los datos no son válidos
            EntityAlreadyExistsError: Si code ya existe para la company
            EntityNotFoundError: Si company_id, country_id o state_id no existen
            BusinessRuleError: Si company no está activo o state no pertenece al country
        """
        # Validar datos de entrada
        self._validate_branch_data(data)

        # Validar que company_id existe y está activo
        company = self.company_repository.get_by_id(data["company_id"])
        if not company:
            raise EntityNotFoundError("Company", data["company_id"])

        if not company.is_active or company.is_deleted:
            raise BusinessRuleError(
                f"La Company {data['company_id']} no está activa",
                details={"company_id": data["company_id"]}
            )

        # Validar que country_id existe
        country = self.country_repository.get_by_id(data["country_id"])
        if not country:
            raise EntityNotFoundError("Country", data["country_id"])

        # Validar que state_id existe y pertenece al country_id
        state = self.state_repository.get_by_id(data["state_id"])
        if not state:
            raise EntityNotFoundError("State", data["state_id"])

        if state.country_id != data["country_id"]:
            raise BusinessRuleError(
                f"El State {data['state_id']} no pertenece al Country {data['country_id']}",
                details={
                    "state_id": data["state_id"],
                    "country_id": data["country_id"],
                    "state_country_id": state.country_id
                }
            )

        # Validar que code sea único por company
        existing_branch = self.repository.get_by_code(data["company_id"], data["code"])
        if existing_branch:
            raise EntityAlreadyExistsError(
                "Branch",
                "code",
                data["code"],
                f"El código '{data['code']}' ya existe para esta empresa"
            )

        # Agregar auditoría
        if created_by:
            data["created_by"] = created_by

        # Crear el registro
        return self.repository.create(data)

    def get_branch_by_id(self, branch_id: int) -> Branch:
        """
        Obtiene una Branch por ID.

        Args:
            branch_id: ID de la Branch

        Returns:
            Branch encontrada

        Raises:
            EntityNotFoundError: Si no se encuentra la Branch
        """
        branch = self.repository.get_by_id(branch_id)
        if not branch:
            raise EntityNotFoundError("Branch", branch_id)
        return branch

    def get_all_branches(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Branch]:
        """
        Obtiene todas las Branches con paginación.

        Args:
            skip: Registros a saltar
            limit: Máximo de registros
            active_only: Solo activas

        Returns:
            Lista de Branches
        """
        return self.repository.get_all(skip, limit, active_only)

    def get_branches_by_company(
        self,
        company_id: int,
        active_only: bool = True
    ) -> List[Branch]:
        """
        Obtiene todas las Branches de una Company.

        Args:
            company_id: ID de la Company
            active_only: Solo activas

        Returns:
            Lista de Branches
        """
        return self.repository.get_by_company(company_id, active_only)

    def update_branch(
        self,
        branch_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> Branch:
        """
        Actualiza una Branch existente.

        Args:
            branch_id: ID de la Branch
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            Branch actualizada

        Raises:
            EntityNotFoundError: Si no se encuentra la Branch, Company, Country o State
            EntityAlreadyExistsError: Si code ya existe para la company
            EntityValidationError: Si los datos no son válidos
            BusinessRuleError: Si company no está activo o state no pertenece al country
        """
        # Verificar que existe
        branch = self.get_branch_by_id(branch_id)

        # Validar datos de entrada
        self._validate_branch_data(data, is_update=True)

        # Si se actualiza company_id, validar que existe y está activo
        if "company_id" in data:
            company = self.company_repository.get_by_id(data["company_id"])
            if not company:
                raise EntityNotFoundError("Company", data["company_id"])

            if not company.is_active or company.is_deleted:
                raise BusinessRuleError(
                    f"La Company {data['company_id']} no está activa",
                    details={"company_id": data["company_id"]}
                )

        # Si se actualiza country_id, validar que existe
        if "country_id" in data:
            country = self.country_repository.get_by_id(data["country_id"])
            if not country:
                raise EntityNotFoundError("Country", data["country_id"])

        # Si se actualiza state_id, validar que existe y pertenece al country
        if "state_id" in data:
            state = self.state_repository.get_by_id(data["state_id"])
            if not state:
                raise EntityNotFoundError("State", data["state_id"])

            # Determinar el country_id a validar (nuevo o actual)
            country_id = data.get("country_id", branch.country_id)
            if state.country_id != country_id:
                raise BusinessRuleError(
                    f"El State {data['state_id']} no pertenece al Country {country_id}",
                    details={
                        "state_id": data["state_id"],
                        "country_id": country_id,
                        "state_country_id": state.country_id
                    }
                )

        # Validar code único por company si se está actualizando
        if "code" in data:
            # Determinar el company_id a validar (nuevo o actual)
            company_id = data.get("company_id", branch.company_id)
            existing_branch = self.repository.get_by_code(company_id, data["code"])
            if existing_branch and existing_branch.id != branch_id:
                raise EntityAlreadyExistsError(
                    "Branch",
                    "code",
                    data["code"],
                    f"El código '{data['code']}' ya existe para esta empresa"
                )

        # Agregar auditoría
        if updated_by:
            data["updated_by"] = updated_by

        # Actualizar
        return self.repository.update(branch_id, data)

    def delete_branch(
        self,
        branch_id: int,
        deleted_by: Optional[int] = None,
        soft_delete: bool = True
    ) -> bool:
        """
        Elimina una Branch (soft delete por defecto).

        Args:
            branch_id: ID de la Branch
            deleted_by: ID del usuario que elimina
            soft_delete: Si True, marca como inactivo

        Returns:
            True si se eliminó correctamente

        Raises:
            EntityNotFoundError: Si no se encuentra la Branch
            BusinessRuleError: Si tiene dependencias activas
        """
        # Verificar que existe
        branch = self.get_branch_by_id(branch_id)

        # Validar que no tenga dependencias activas
        if self.repository.has_active_departments(branch_id):
            raise BusinessRuleError(
                "No se puede eliminar una Branch con departments activos asociados",
                details={"branch_id": branch_id}
            )

        if self.repository.has_active_employees(branch_id):
            raise BusinessRuleError(
                "No se puede eliminar una Branch con employees activos asociados",
                details={"branch_id": branch_id}
            )

        # Si es soft delete, marcar deleted_by
        if soft_delete and deleted_by:
            self.repository.update(branch_id, {
                "is_active": False,
                "is_deleted": True,
                "deleted_by": deleted_by
            })
            return True

        return self.repository.delete(branch_id, soft_delete)

    # ==================== OPERACIONES AVANZADAS ====================

    def search_branches(self, query: str, limit: int = 50) -> List[Branch]:
        """
        Busca Branches por nombre, código o ciudad (case-insensitive).

        Args:
            query: Término de búsqueda
            limit: Máximo de resultados

        Returns:
            Lista de Branches que coinciden
        """
        return self.repository.search(query, limit)

    def paginate_branches(
        self,
        page: int = 1,
        per_page: int = 20,
        active_only: bool = True,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> Dict[str, Any]:
        """
        Obtiene Branches paginadas.

        Args:
            page: Número de página
            per_page: Registros por página
            active_only: Solo activas
            order_by: Campo de ordenamiento
            order_direction: Dirección de ordenamiento

        Returns:
            Diccionario con items paginados y metadatos
        """
        filters = {}
        if active_only:
            filters["is_active"] = True
            filters["is_deleted"] = False

        return self.repository.paginate(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by=order_by,
            order_direction=order_direction
        )

    # ==================== VALIDACIONES ====================

    def _validate_branch_data(
        self,
        data: Dict[str, Any],
        is_update: bool = False
    ) -> None:
        """
        Valida los datos de una Branch.

        Args:
            data: Datos a validar
            is_update: Si es una actualización (campos opcionales)

        Raises:
            EntityValidationError: Si hay errores de validación
        """
        errors = {}

        # Validar company_id (obligatorio en creación)
        if not is_update or "company_id" in data:
            company_id = data.get("company_id")
            if not company_id:
                errors["company_id"] = "El company_id es obligatorio"
            elif not isinstance(company_id, int) or company_id <= 0:
                errors["company_id"] = "El company_id debe ser un entero positivo"

        # Validar country_id (obligatorio en creación)
        if not is_update or "country_id" in data:
            country_id = data.get("country_id")
            if not country_id:
                errors["country_id"] = "El country_id es obligatorio"
            elif not isinstance(country_id, int) or country_id <= 0:
                errors["country_id"] = "El country_id debe ser un entero positivo"

        # Validar state_id (obligatorio en creación)
        if not is_update or "state_id" in data:
            state_id = data.get("state_id")
            if not state_id:
                errors["state_id"] = "El state_id es obligatorio"
            elif not isinstance(state_id, int) or state_id <= 0:
                errors["state_id"] = "El state_id debe ser un entero positivo"

        # Validar code (obligatorio en creación)
        if not is_update or "code" in data:
            code = data.get("code", "").strip()
            if not code:
                errors["code"] = "El código es obligatorio"
            elif len(code) > 50:
                errors["code"] = "El código no puede exceder 50 caracteres"

        # Validar name (obligatorio en creación)
        if not is_update or "name" in data:
            name = data.get("name", "").strip()
            if not name:
                errors["name"] = "El nombre es obligatorio"
            elif len(name) < 2:
                errors["name"] = "El nombre debe tener al menos 2 caracteres"
            elif len(name) > 200:
                errors["name"] = "El nombre no puede exceder 200 caracteres"

        # Validar address si se proporciona
        if "address" in data and data["address"]:
            if len(data["address"]) > 300:
                errors["address"] = "La dirección no puede exceder 300 caracteres"

        # Validar city si se proporciona
        if "city" in data and data["city"]:
            city = data["city"].strip()
            if len(city) < 2:
                errors["city"] = "La ciudad debe tener al menos 2 caracteres"
            elif len(city) > 100:
                errors["city"] = "La ciudad no puede exceder 100 caracteres"

        # Validar postal_code si se proporciona
        if "postal_code" in data and data["postal_code"]:
            postal_code = data["postal_code"].strip()
            if len(postal_code) > 20:
                errors["postal_code"] = "El código postal no puede exceder 20 caracteres"

        # Validar phone si se proporciona
        if "phone" in data and data["phone"]:
            phone = data["phone"].strip()
            if len(phone) > 50:
                errors["phone"] = "El teléfono no puede exceder 50 caracteres"

        # Validar email si se proporciona
        if "email" in data and data["email"]:
            email = data["email"].strip()
            if len(email) > 100:
                errors["email"] = "El email no puede exceder 100 caracteres"
            elif "@" not in email or "." not in email:
                errors["email"] = "El email no tiene un formato válido"

        if errors:
            raise EntityValidationError("Branch", errors)
