"""
Repository: Branch

Operaciones de base de datos para Branch.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.shared.base_repository import BaseRepository
from app.entities.branches.models.branch import Branch


class BranchRepository(BaseRepository[Branch]):
    """Repository para operaciones CRUD de Branch."""

    def __init__(self, db: Session):
        super().__init__(Branch, db)

    def get_by_company(self, company_id: int, active_only: bool = True) -> List[Branch]:
        """Obtiene todas las sucursales de una empresa."""
        query = self.db.query(Branch).filter(Branch.company_id == company_id)

        if active_only:
            query = query.filter(Branch.is_active == True, Branch.is_deleted == False)

        return query.all()

    def get_by_country(self, country_id: int, active_only: bool = True) -> List[Branch]:
        """Obtiene todas las sucursales de un país."""
        query = self.db.query(Branch).filter(Branch.country_id == country_id)

        if active_only:
            query = query.filter(Branch.is_active == True, Branch.is_deleted == False)

        return query.all()

    def get_by_code(self, company_id: int, code: str) -> Optional[Branch]:
        """
        Obtiene una sucursal por código dentro de una empresa.
        Usado para validar unicidad de código por empresa.
        """
        return self.db.query(Branch).filter(
            Branch.company_id == company_id,
            Branch.code == code,
            Branch.is_deleted == False
        ).first()

    def has_active_departments(self, branch_id: int) -> bool:
        """
        Verifica si la sucursal tiene departamentos activos.
        TODO: Implementar cuando se cree la entidad Department.
        """
        # Placeholder - implementar cuando exista Department
        return False

    def has_active_employees(self, branch_id: int) -> bool:
        """
        Verifica si la sucursal tiene empleados activos.
        TODO: Implementar cuando se cree la entidad Employee.
        """
        # Placeholder - implementar cuando exista Employee
        return False

    def search(self, query: str, limit: int = 50) -> List[Branch]:
        """Busca sucursales por nombre, código o ciudad."""
        search_pattern = f"%{query}%"
        return self.db.query(Branch).filter(
            (Branch.name.ilike(search_pattern)) |
            (Branch.code.ilike(search_pattern)) |
            (Branch.city.ilike(search_pattern)),
            Branch.is_deleted == False
        ).limit(limit).all()
