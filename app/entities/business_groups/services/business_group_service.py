"""
Service: BusinessGroup

Lógica de negocio y validaciones para BusinessGroup.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.entities.business_groups.repositories.business_group_repository import BusinessGroupRepository
from app.entities.business_groups.models.business_group import BusinessGroup
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)


class BusinessGroupService:
    """Servicio para lógica de negocio de BusinessGroup."""

    def __init__(self, db: Session):
        """Inicializa el servicio con el repositorio."""
        self.db = db
        self.repository = BusinessGroupRepository(db)

    # ==================== OPERACIONES CRUD ====================

    def create_business_group(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> BusinessGroup:
        """
        Crea un nuevo BusinessGroup con validaciones de negocio.

        Args:
            data: Datos del BusinessGroup
            created_by: ID del usuario que crea el registro

        Returns:
            BusinessGroup creado

        Raises:
            EntityValidationError: Si los datos no son válidos
            EntityAlreadyExistsError: Si el tax_id ya existe
        """
        # Validar datos de entrada
        self._validate_business_group_data(data)

        # Validar que tax_id sea único si se proporciona
        if data.get("tax_id"):
            if self.repository.tax_id_exists(data["tax_id"]):
                raise EntityAlreadyExistsError(
                    "BusinessGroup",
                    "tax_id",
                    data["tax_id"]
                )

        # Agregar auditoría
        if created_by:
            data["created_by"] = created_by

        # Crear el registro
        return self.repository.create(data)

    def get_business_group_by_id(self, business_group_id: int) -> BusinessGroup:
        """
        Obtiene un BusinessGroup por ID.

        Args:
            business_group_id: ID del BusinessGroup

        Returns:
            BusinessGroup encontrado

        Raises:
            EntityNotFoundError: Si no se encuentra el BusinessGroup
        """
        business_group = self.repository.get_by_id(business_group_id)
        if not business_group:
            raise EntityNotFoundError("BusinessGroup", business_group_id)
        return business_group

    def get_all_business_groups(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[BusinessGroup]:
        """
        Obtiene todos los BusinessGroups con paginación.

        Args:
            skip: Registros a saltar
            limit: Máximo de registros
            active_only: Solo activos

        Returns:
            Lista de BusinessGroups
        """
        return self.repository.get_all(skip, limit, active_only)

    def update_business_group(
        self,
        business_group_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> BusinessGroup:
        """
        Actualiza un BusinessGroup existente.

        Args:
            business_group_id: ID del BusinessGroup
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            BusinessGroup actualizado

        Raises:
            EntityNotFoundError: Si no se encuentra el BusinessGroup
            EntityAlreadyExistsError: Si el tax_id ya existe
            EntityValidationError: Si los datos no son válidos
        """
        # Verificar que existe
        business_group = self.get_business_group_by_id(business_group_id)

        # Validar datos de entrada
        self._validate_business_group_data(data, is_update=True)

        # Validar tax_id único si se está actualizando
        if "tax_id" in data and data["tax_id"]:
            if self.repository.tax_id_exists(data["tax_id"], exclude_id=business_group_id):
                raise EntityAlreadyExistsError(
                    "BusinessGroup",
                    "tax_id",
                    data["tax_id"]
                )

        # Agregar auditoría
        if updated_by:
            data["updated_by"] = updated_by

        # Actualizar
        return self.repository.update(business_group_id, data)

    def delete_business_group(
        self,
        business_group_id: int,
        deleted_by: Optional[int] = None,
        soft_delete: bool = True
    ) -> bool:
        """
        Elimina un BusinessGroup (soft delete por defecto).

        Args:
            business_group_id: ID del BusinessGroup
            deleted_by: ID del usuario que elimina
            soft_delete: Si True, marca como inactivo

        Returns:
            True si se eliminó correctamente

        Raises:
            EntityNotFoundError: Si no se encuentra el BusinessGroup
            BusinessRuleError: Si tiene empresas activas asociadas
        """
        # Verificar que existe
        business_group = self.get_business_group_by_id(business_group_id)

        # Validar que no tenga empresas activas asociadas
        if self.repository.has_active_companies(business_group_id):
            raise BusinessRuleError(
                "No se puede eliminar un BusinessGroup con empresas activas asociadas",
                details={"business_group_id": business_group_id}
            )

        # Si es soft delete, marcar deleted_by
        if soft_delete and deleted_by:
            self.repository.update(business_group_id, {
                "is_active": False,
                "is_deleted": True,
                "deleted_by": deleted_by
            })
            return True

        return self.repository.delete(business_group_id, soft_delete)

    # ==================== OPERACIONES AVANZADAS ====================

    def search_business_groups(self, name: str, limit: int = 50) -> List[BusinessGroup]:
        """
        Busca BusinessGroups por nombre (case-insensitive).

        Args:
            name: Término de búsqueda
            limit: Máximo de resultados

        Returns:
            Lista de BusinessGroups que coinciden
        """
        return self.repository.search_by_name(name, limit)

    def get_business_group_by_tax_id(self, tax_id: str) -> Optional[BusinessGroup]:
        """
        Obtiene un BusinessGroup por tax_id.

        Args:
            tax_id: Identificación fiscal

        Returns:
            BusinessGroup o None
        """
        return self.repository.get_by_tax_id(tax_id)

    def paginate_business_groups(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> Dict[str, Any]:
        """
        Obtiene BusinessGroups paginados.

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

    def _validate_business_group_data(
        self,
        data: Dict[str, Any],
        is_update: bool = False
    ) -> None:
        """
        Valida los datos de un BusinessGroup.

        Args:
            data: Datos a validar
            is_update: Si es una actualización (campos opcionales)

        Raises:
            EntityValidationError: Si hay errores de validación
        """
        errors = {}

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

        if errors:
            raise EntityValidationError("BusinessGroup", errors)
