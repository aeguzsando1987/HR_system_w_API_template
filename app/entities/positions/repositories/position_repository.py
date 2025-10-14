"""
Repository: Position

Operaciones de base de datos para Position.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.entities.positions.models.position import Position


class PositionRepository(BaseRepository[Position]):
    """Repositorio para operaciones de Position."""

    def __init__(self, db: Session):
        """Inicializa el repositorio."""
        super().__init__(Position, db)

    # ==================== CUSTOM QUERIES ====================

    def get_by_company(self, company_id: int, active_only: bool = True) -> List[Position]:
        """
        Obtiene todas las positions de una company especifica.
        Ordenadas por hierarchy_weight ascendente (menor peso = mayor jerarquia).

        Args:
            company_id: ID de la company
            active_only: Si True, solo retorna activos

        Returns:
            Lista de positions
        """
        query = self.db.query(Position).filter(Position.company_id == company_id)

        if active_only:
            query = query.filter(
                Position.is_active == True,
                Position.is_deleted == False
            )

        return query.order_by(Position.hierarchy_weight.asc()).all()

    def search(self, query_text: str, limit: int = 50) -> List[Position]:
        """
        Busca positions por title (case-insensitive).

        Args:
            query_text: Texto a buscar en title
            limit: Numero maximo de resultados

        Returns:
            Lista de positions que coinciden
        """
        return self.db.query(Position).filter(
            Position.title.ilike(f"%{query_text}%"),
            Position.is_active == True,
            Position.is_deleted == False
        ).order_by(Position.hierarchy_weight.asc()).limit(limit).all()

    def has_active_employees(self, position_id: int) -> bool:
        """
        Verifica si position tiene employees activos asociados.

        Args:
            position_id: ID de la position

        Returns:
            True si tiene employees activos, False en caso contrario

        Note:
            TODO: Implementar cuando Employee entity exista.
            Por ahora retorna False para permitir eliminaciones.
        """
        # TODO: Implementar cuando Employee exista
        # from app.entities.employees.models.employee import Employee
        # count = self.db.query(Employee).filter(
        #     Employee.position_id == position_id,
        #     Employee.is_active == True,
        #     Employee.is_deleted == False
        # ).count()
        # return count > 0
        return False

    def get_by_hierarchy_level(self, hierarchy_level: str, company_id: Optional[int] = None) -> List[Position]:
        """
        Obtiene positions por nivel jerarquico.

        Args:
            hierarchy_level: Nivel jerarquico (ej: "Manager", "Director")
            company_id: ID de company (opcional, para filtrar por empresa)

        Returns:
            Lista de positions del nivel especificado
        """
        query = self.db.query(Position).filter(
            Position.hierarchy_level == hierarchy_level,
            Position.is_active == True,
            Position.is_deleted == False
        )

        if company_id:
            query = query.filter(Position.company_id == company_id)

        return query.order_by(Position.hierarchy_weight.asc()).all()