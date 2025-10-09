"""
Service: Company

Lógica de negocio y validaciones para Company.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.entities.companies.repositories.company_repository import CompanyRepository
from app.entities.companies.models.company import Company
from app.entities.business_groups.repositories.business_group_repository import BusinessGroupRepository
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)


class CompanyService:
    """Servicio para lógica de negocio de Company."""

    def __init__(self, db: Session):
        """Inicializa el servicio con el repositorio."""
        self.db = db
        self.repository = CompanyRepository(db)
        self.business_group_repository = BusinessGroupRepository(db)

    # ==================== OPERACIONES CRUD ====================

    def create_company(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> Company:
        """
        Crea una nueva Company con validaciones de negocio.

        Args:
            data: Datos de la Company
            created_by: ID del usuario que crea el registro

        Returns:
            Company creada

        Raises:
            EntityValidationError: Si los datos no son válidos
            EntityAlreadyExistsError: Si tax_id o code ya existen
            EntityNotFoundError: Si business_group_id no existe
            BusinessRuleError: Si business_group no está activo
        """
        # Validar datos de entrada
        self._validate_company_data(data)

        # Validar que business_group_id existe y está activo
        business_group = self.business_group_repository.get_by_id(data["business_group_id"])
        if not business_group:
            raise EntityNotFoundError("BusinessGroup", data["business_group_id"])

        if not business_group.is_active or business_group.is_deleted:
            raise BusinessRuleError(
                f"El BusinessGroup {data['business_group_id']} no está activo",
                details={"business_group_id": data["business_group_id"]}
            )

        # Validar que tax_id sea único si se proporciona
        if data.get("tax_id"):
            if self.repository.tax_id_exists(data["tax_id"]):
                raise EntityAlreadyExistsError(
                    "Company",
                    "tax_id",
                    data["tax_id"]
                )

        # Validar que code sea único
        if self.repository.code_exists(data["code"]):
            raise EntityAlreadyExistsError(
                "Company",
                "code",
                data["code"]
            )

        # Agregar auditoría
        if created_by:
            data["created_by"] = created_by

        # Crear el registro
        return self.repository.create(data)

    def get_company_by_id(self, company_id: int) -> Company:
        """
        Obtiene una Company por ID.

        Args:
            company_id: ID de la Company

        Returns:
            Company encontrada

        Raises:
            EntityNotFoundError: Si no se encuentra la Company
        """
        company = self.repository.get_by_id(company_id)
        if not company:
            raise EntityNotFoundError("Company", company_id)
        return company

    def get_all_companies(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Company]:
        """
        Obtiene todas las Companies con paginación.

        Args:
            skip: Registros a saltar
            limit: Máximo de registros
            active_only: Solo activas

        Returns:
            Lista de Companies
        """
        return self.repository.get_all(skip, limit, active_only)

    def get_companies_by_business_group(
        self,
        business_group_id: int,
        active_only: bool = True
    ) -> List[Company]:
        """
        Obtiene todas las Companies de un BusinessGroup.

        Args:
            business_group_id: ID del BusinessGroup
            active_only: Solo activas

        Returns:
            Lista de Companies
        """
        return self.repository.get_by_business_group(business_group_id, active_only)

    def update_company(
        self,
        company_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> Company:
        """
        Actualiza una Company existente.

        Args:
            company_id: ID de la Company
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            Company actualizada

        Raises:
            EntityNotFoundError: Si no se encuentra la Company o BusinessGroup
            EntityAlreadyExistsError: Si tax_id o code ya existen
            EntityValidationError: Si los datos no son válidos
            BusinessRuleError: Si business_group no está activo
        """
        # Verificar que existe
        company = self.get_company_by_id(company_id)

        # Validar datos de entrada
        self._validate_company_data(data, is_update=True)

        # Si se actualiza business_group_id, validar que existe y está activo
        if "business_group_id" in data:
            business_group = self.business_group_repository.get_by_id(data["business_group_id"])
            if not business_group:
                raise EntityNotFoundError("BusinessGroup", data["business_group_id"])

            if not business_group.is_active or business_group.is_deleted:
                raise BusinessRuleError(
                    f"El BusinessGroup {data['business_group_id']} no está activo",
                    details={"business_group_id": data["business_group_id"]}
                )

        # Validar tax_id único si se está actualizando
        if "tax_id" in data and data["tax_id"]:
            if self.repository.tax_id_exists(data["tax_id"], exclude_id=company_id):
                raise EntityAlreadyExistsError(
                    "Company",
                    "tax_id",
                    data["tax_id"]
                )

        # Validar code único si se está actualizando
        if "code" in data:
            if self.repository.code_exists(data["code"], exclude_id=company_id):
                raise EntityAlreadyExistsError(
                    "Company",
                    "code",
                    data["code"]
                )

        # Agregar auditoría
        if updated_by:
            data["updated_by"] = updated_by

        # Actualizar
        return self.repository.update(company_id, data)

    def delete_company(
        self,
        company_id: int,
        deleted_by: Optional[int] = None,
        soft_delete: bool = True
    ) -> bool:
        """
        Elimina una Company (soft delete por defecto).

        Args:
            company_id: ID de la Company
            deleted_by: ID del usuario que elimina
            soft_delete: Si True, marca como inactivo

        Returns:
            True si se eliminó correctamente

        Raises:
            EntityNotFoundError: Si no se encuentra la Company
            BusinessRuleError: Si tiene dependencias activas
        """
        # Verificar que existe
        company = self.get_company_by_id(company_id)

        # Validar que no tenga dependencias activas
        if self.repository.has_active_branches(company_id):
            raise BusinessRuleError(
                "No se puede eliminar una Company con branches activas asociadas",
                details={"company_id": company_id}
            )

        if self.repository.has_active_departments(company_id):
            raise BusinessRuleError(
                "No se puede eliminar una Company con departments activos asociados",
                details={"company_id": company_id}
            )

        if self.repository.has_active_positions(company_id):
            raise BusinessRuleError(
                "No se puede eliminar una Company con positions activas asociadas",
                details={"company_id": company_id}
            )

        if self.repository.has_active_employees(company_id):
            raise BusinessRuleError(
                "No se puede eliminar una Company con employees activos asociados",
                details={"company_id": company_id}
            )

        # Si es soft delete, marcar deleted_by
        if soft_delete and deleted_by:
            self.repository.update(company_id, {
                "is_active": False,
                "is_deleted": True,
                "deleted_by": deleted_by
            })
            return True

        return self.repository.delete(company_id, soft_delete)

    # ==================== OPERACIONES AVANZADAS ====================

    def search_companies(self, name: str, limit: int = 50) -> List[Company]:
        """
        Busca Companies por nombre (case-insensitive).

        Args:
            name: Término de búsqueda
            limit: Máximo de resultados

        Returns:
            Lista de Companies que coinciden
        """
        return self.repository.search_by_name(name, limit)

    def get_company_by_tax_id(self, tax_id: str) -> Optional[Company]:
        """
        Obtiene una Company por tax_id.

        Args:
            tax_id: Identificación fiscal

        Returns:
            Company o None
        """
        return self.repository.get_by_tax_id(tax_id)

    def get_company_by_code(self, code: str) -> Optional[Company]:
        """
        Obtiene una Company por código.

        Args:
            code: Código de la company

        Returns:
            Company o None
        """
        return self.repository.get_by_code(code)

    def paginate_companies(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> Dict[str, Any]:
        """
        Obtiene Companies paginadas.

        Args:
            page: Número de página
            per_page: Registros por página
            filters: Filtros a aplicar
            order_by: Campo de ordenamiento
            order_direction: Dirección de ordenamiento

        Returns:
            Diccionario con items paginados y metadatos
        """
        return self.repository.paginate(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by=order_by,
            order_direction=order_direction
        )

    # ==================== VALIDACIONES ====================

    def _validate_company_data(
        self,
        data: Dict[str, Any],
        is_update: bool = False
    ) -> None:
        """
        Valida los datos de una Company.

        Args:
            data: Datos a validar
            is_update: Si es una actualización (campos opcionales)

        Raises:
            EntityValidationError: Si hay errores de validación
        """
        errors = {}

        # Validar business_group_id (obligatorio en creación)
        if not is_update or "business_group_id" in data:
            business_group_id = data.get("business_group_id")
            if not business_group_id:
                errors["business_group_id"] = "El business_group_id es obligatorio"
            elif not isinstance(business_group_id, int) or business_group_id <= 0:
                errors["business_group_id"] = "El business_group_id debe ser un entero positivo"

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

        # Validar legal_name si se proporciona
        if "legal_name" in data and data["legal_name"]:
            if len(data["legal_name"]) > 200:
                errors["legal_name"] = "La razón social no puede exceder 200 caracteres"

        # Validar tax_id si se proporciona
        if "tax_id" in data and data["tax_id"]:
            tax_id = data["tax_id"].strip()
            if len(tax_id) < 3:
                errors["tax_id"] = "El tax_id debe tener al menos 3 caracteres"
            elif len(tax_id) > 50:
                errors["tax_id"] = "El tax_id no puede exceder 50 caracteres"

        # Validar industry si se proporciona
        if "industry" in data and data["industry"]:
            if len(data["industry"]) > 100:
                errors["industry"] = "La industria no puede exceder 100 caracteres"

        if errors:
            raise EntityValidationError("Company", errors)
