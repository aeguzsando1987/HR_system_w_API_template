"""
Repository: BusinessGroup

Operaciones de base de datos para BusinessGroup.
Hereda de BaseRepository para operaciones CRUD estándar.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.shared.base_repository import BaseRepository
from app.entities.business_groups.models.business_group import BusinessGroup


class BusinessGroupRepository(BaseRepository[BusinessGroup]):
    """
    Repositorio para BusinessGroup.

    Hereda todas las operaciones CRUD de BaseRepository:
    - get_by_id(id)
    - get_all(skip, limit, active_only)
    - create(obj_data)
    - update(id, obj_data)
    - delete(id, soft_delete)
    - exists(id)
    - count(active_only)
    - find_by_field(field_name, value)
    - find_by_filters(filters)
    - search(search_term, search_fields, limit)
    - paginate(page, per_page, filters, order_by, order_direction)
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio con el modelo BusinessGroup."""
        super().__init__(BusinessGroup, db)

    # ==================== MÉTODOS PERSONALIZADOS ====================

    def get_by_tax_id(self, tax_id: str) -> Optional[BusinessGroup]:
        """
        Busca un BusinessGroup por su tax_id (RFC/RUT/NIT).

        Args:
            tax_id: Identificación fiscal a buscar

        Returns:
            BusinessGroup encontrado o None
        """
        return self.db.query(BusinessGroup).filter(
            BusinessGroup.tax_id == tax_id
        ).first()

    def search_by_name(self, name: str, limit: int = 50) -> List[BusinessGroup]:
        """
        Busca BusinessGroups por nombre (case-insensitive).

        Args:
            name: Término a buscar en el nombre
            limit: Máximo de resultados

        Returns:
            Lista de BusinessGroups que coinciden
        """
        return self.search(
            search_term=name,
            search_fields=["name", "legal_name"],
            limit=limit
        )

    def tax_id_exists(self, tax_id: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un tax_id ya está en uso.

        Args:
            tax_id: Tax ID a verificar
            exclude_id: ID a excluir de la búsqueda (útil para updates)

        Returns:
            True si el tax_id ya existe, False si no
        """
        if not tax_id:
            return False

        query = self.db.query(BusinessGroup).filter(
            BusinessGroup.tax_id == tax_id
        )

        if exclude_id:
            query = query.filter(BusinessGroup.id != exclude_id)

        return query.first() is not None

    def has_active_companies(self, business_group_id: int) -> bool:
        """
        Verifica si un BusinessGroup tiene empresas activas asociadas.

        Args:
            business_group_id: ID del BusinessGroup

        Returns:
            True si tiene empresas activas, False si no

        Nota:
            Este método se implementará completamente cuando exista la entidad Company.
            Por ahora retorna False.
        """
        # TODO: Implementar cuando exista la entidad Company
        # from app.entities.companies.models.company import Company
        # return self.db.query(Company).filter(
        #     Company.business_group_id == business_group_id,
        #     Company.is_active == True
        # ).count() > 0
        return False
