"""
Service: Position

Logica de negocio y validaciones para Position.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
from math import ceil

from app.entities.positions.repositories.position_repository import PositionRepository
from app.entities.positions.models.position import Position
from app.entities.positions.schemas.position_schemas import HIERARCHY_WEIGHTS_DEFAULT
from app.entities.companies.repositories.company_repository import CompanyRepository
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    BusinessRuleError
)


class PositionService:
    """Servicio para logica de negocio de Position."""

    def __init__(self, db: Session):
        """Inicializa el servicio con el repositorio."""
        self.db = db
        self.repository = PositionRepository(db)
        self.company_repository = CompanyRepository(db)

    # ==================== OPERACIONES CRUD ====================

    def create_position(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> Position:
        """
        Crea un nuevo Position con validaciones de negocio.

        Args:
            data: Datos del Position
            created_by: ID del usuario que crea el registro

        Returns:
            Position creado

        Raises:
            EntityValidationError: Si los datos no son validos
            EntityNotFoundError: Si company_id no existe
            BusinessRuleError: Si hay violaciones de reglas de negocio
        """
        # Validar datos de entrada
        self._validate_position_data(data)

        # Validar que company_id existe y esta activo
        company = self.company_repository.get_by_id(data["company_id"])
        if not company:
            raise EntityNotFoundError("Company", data["company_id"])

        if not company.is_active or company.is_deleted:
            raise BusinessRuleError(
                f"La Company {data['company_id']} no esta activa",
                details={"company_id": data["company_id"]}
            )

        # Si no se provee hierarchy_weight, asignarlo segun hierarchy_level
        if "hierarchy_weight" not in data or data["hierarchy_weight"] is None:
            hierarchy_level = data.get("hierarchy_level")
            if hierarchy_level:
                data["hierarchy_weight"] = HIERARCHY_WEIGHTS_DEFAULT.get(hierarchy_level, 50)

        # Validar hierarchy_weight (0-100)
        if "hierarchy_weight" in data:
            weight = data["hierarchy_weight"]
            if weight < 0 or weight > 100:
                raise EntityValidationError(
                    "Position",
                    {"hierarchy_weight": "Debe estar entre 0 y 100"}
                )

        # Agregar auditoria
        if created_by:
            data["created_by"] = created_by

        # Crear el registro
        return self.repository.create(data)

    def get_position_by_id(self, position_id: int) -> Position:
        """
        Obtiene un Position por ID.

        Args:
            position_id: ID del Position

        Returns:
            Position encontrado

        Raises:
            EntityNotFoundError: Si no se encuentra el Position
        """
        position = self.repository.get_by_id(position_id)
        if not position:
            raise EntityNotFoundError("Position", position_id)
        return position

    def get_all_positions(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Position]:
        """
        Obtiene todos los Positions con paginacion.

        Args:
            skip: Numero de registros a omitir
            limit: Numero maximo de registros a retornar
            active_only: Si True, solo retorna activos

        Returns:
            Lista de Positions
        """
        return self.repository.get_all(skip=skip, limit=limit, active_only=active_only)

    def update_position(
        self,
        position_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> Position:
        """
        Actualiza un Position existente.

        Args:
            position_id: ID del Position a actualizar
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            Position actualizado

        Raises:
            EntityNotFoundError: Si no se encuentra el Position
            EntityValidationError: Si los datos no son validos
            BusinessRuleError: Si hay violaciones de reglas de negocio
        """
        # Validar que el position existe
        position = self.get_position_by_id(position_id)

        # Validar datos de entrada
        self._validate_position_data(data, is_update=True)

        # Si se actualiza company_id, validarlo
        if "company_id" in data and data["company_id"] != position.company_id:
            company = self.company_repository.get_by_id(data["company_id"])
            if not company:
                raise EntityNotFoundError("Company", data["company_id"])
            if not company.is_active or company.is_deleted:
                raise BusinessRuleError(
                    f"La Company {data['company_id']} no esta activa",
                    details={"company_id": data["company_id"]}
                )

        # Si se actualiza hierarchy_level pero no hierarchy_weight, recalcular peso
        if "hierarchy_level" in data and "hierarchy_weight" not in data:
            data["hierarchy_weight"] = HIERARCHY_WEIGHTS_DEFAULT.get(data["hierarchy_level"], 50)

        # Validar hierarchy_weight si se provee
        if "hierarchy_weight" in data:
            weight = data["hierarchy_weight"]
            if weight < 0 or weight > 100:
                raise EntityValidationError(
                    "Position",
                    {"hierarchy_weight": "Debe estar entre 0 y 100"}
                )

        # Agregar auditoria
        if updated_by:
            data["updated_by"] = updated_by

        # Actualizar
        return self.repository.update(position_id, data)

    def delete_position(
        self,
        position_id: int,
        deleted_by: Optional[int] = None
    ) -> bool:
        """
        Elimina un Position (soft delete).

        Args:
            position_id: ID del Position a eliminar
            deleted_by: ID del usuario que elimina

        Returns:
            True si se elimino correctamente

        Raises:
            EntityNotFoundError: Si no se encuentra el Position
            BusinessRuleError: Si tiene employees activos asociados
        """
        # Validar que el position existe
        position = self.get_position_by_id(position_id)

        # Validar que no tiene employees activos
        if self.repository.has_active_employees(position_id):
            raise BusinessRuleError(
                "No se puede eliminar una Position con empleados activos asociados",
                details={"position_id": position_id}
            )

        # Soft delete: marcar deleted_by
        if deleted_by:
            self.repository.update(position_id, {
                "is_active": False,
                "is_deleted": True,
                "deleted_by": deleted_by,
                "deleted_at": datetime.utcnow()
            })
        else:
            self.repository.delete(position_id, soft_delete=True)

        return True

    # ==================== OPERACIONES ADICIONALES ====================

    def get_positions_by_company(self, company_id: int, active_only: bool = True) -> List[Position]:
        """
        Obtiene todas las positions de una company.

        Args:
            company_id: ID de la company
            active_only: Si True, solo retorna activos

        Returns:
            Lista de positions ordenadas por hierarchy_weight
        """
        return self.repository.get_by_company(company_id, active_only)

    def search_positions(self, query: str, limit: int = 50) -> List[Position]:
        """
        Busca positions por title.

        Args:
            query: Texto a buscar
            limit: Numero maximo de resultados

        Returns:
            Lista de positions que coinciden
        """
        return self.repository.search(query, limit)

    def paginate_positions(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Obtiene positions paginados.

        Args:
            page: Numero de pagina (inicia en 1)
            per_page: Cantidad de registros por pagina

        Returns:
            Diccionario con items, total, page, per_page, pages
        """
        skip = (page - 1) * per_page
        positions = self.repository.get_all(skip=skip, limit=per_page, active_only=True)
        total = self.repository.count(active_only=True)
        pages = ceil(total / per_page)

        return {
            "items": positions,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages
        }

    # ==================== VALIDACIONES PRIVADAS ====================

    def _validate_position_data(self, data: Dict[str, Any], is_update: bool = False) -> None:
        """
        Valida datos de Position.

        Args:
            data: Datos a validar
            is_update: True si es actualizacion

        Raises:
            EntityValidationError: Si hay errores de validacion
        """
        errors = {}

        # Validar title (obligatorio en creacion)
        if not is_update and "title" not in data:
            errors["title"] = "El titulo es obligatorio"
        elif "title" in data and (not data["title"] or len(data["title"]) == 0):
            errors["title"] = "El titulo no puede estar vacio"

        # Validar company_id (obligatorio en creacion)
        if not is_update and "company_id" not in data:
            errors["company_id"] = "El company_id es obligatorio"

        # Validar hierarchy_level (obligatorio en creacion)
        if not is_update and "hierarchy_level" not in data:
            errors["hierarchy_level"] = "El hierarchy_level es obligatorio"

        if errors:
            raise EntityValidationError("Position", errors)