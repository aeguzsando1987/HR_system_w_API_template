"""
Controller: Position

Manejo de requests y responses para Position.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.entities.positions.services.position_service import PositionService
from app.entities.positions.models.position import Position
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    BusinessRuleError
)


class PositionController:
    """Controller para Position."""

    def __init__(self, db: Session):
        """Inicializa el controller con el servicio."""
        self.service = PositionService(db)

    def create_position(
        self,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Position:
        """Crea un nuevo Position."""
        try:
            return self.service.create_position(data, created_by=current_user_id)
        except (EntityValidationError, EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al crear position: {str(e)}")

    def get_position(self, position_id: int) -> Position:
        """Obtiene un Position por ID."""
        try:
            return self.service.get_position_by_id(position_id)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al obtener position: {str(e)}")

    def get_all_positions(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ):
        """Obtiene todos los Positions."""
        try:
            return self.service.get_all_positions(skip, limit, active_only)
        except Exception as e:
            raise Exception(f"Error al listar positions: {str(e)}")

    def update_position(
        self,
        position_id: int,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Position:
        """Actualiza un Position."""
        try:
            return self.service.update_position(position_id, data, updated_by=current_user_id)
        except (EntityValidationError, EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al actualizar position: {str(e)}")

    def delete_position(
        self,
        position_id: int,
        current_user_id: Optional[int] = None
    ) -> bool:
        """Elimina un Position (soft delete)."""
        try:
            return self.service.delete_position(position_id, deleted_by=current_user_id)
        except (EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al eliminar position: {str(e)}")

    def search_positions(self, query: str, limit: int = 50):
        """Busca Positions por title."""
        try:
            return self.service.search_positions(query, limit)
        except Exception as e:
            raise Exception(f"Error al buscar positions: {str(e)}")

    def get_positions_by_company(self, company_id: int, active_only: bool = True):
        """Obtiene Positions por Company."""
        try:
            return self.service.get_positions_by_company(company_id, active_only)
        except Exception as e:
            raise Exception(f"Error al obtener positions por company: {str(e)}")

    def paginate_positions(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ):
        """Obtiene Positions paginados."""
        try:
            return self.service.paginate_positions(page, per_page)
        except Exception as e:
            raise Exception(f"Error al paginar positions: {str(e)}")