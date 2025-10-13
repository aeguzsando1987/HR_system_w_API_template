"""
Repository: Department

Operaciones de base de datos para Department.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.shared.base_repository import BaseRepository
from app.entities.departments.models.department import Department


class DepartmentRepository(BaseRepository[Department]):
    """Repository para operaciones CRUD de Department."""

    def __init__(self, db: Session):
        super().__init__(Department, db)

    def get_by_company(self, company_id: int, active_only: bool = True) -> List[Department]:
        """Obtiene todos los departamentos de una empresa."""
        query = self.db.query(Department).filter(Department.company_id == company_id)

        if active_only:
            query = query.filter(Department.is_active == True, Department.is_deleted == False)

        return query.all()

    def get_by_branch(self, branch_id: int, active_only: bool = True) -> List[Department]:
        """
        Obtiene departamentos de una sucursal específica.
        Excluye departamentos corporativos (is_corporate=True).
        """
        query = self.db.query(Department).filter(
            Department.branch_id == branch_id,
            Department.is_corporate == False
        )

        if active_only:
            query = query.filter(Department.is_active == True, Department.is_deleted == False)

        return query.all()

    def get_corporate_by_company(self, company_id: int, active_only: bool = True) -> List[Department]:
        """
        Obtiene SOLO departamentos corporativos de una empresa.
        Departamentos corporativos: is_corporate=True, branch_id=NULL
        """
        query = self.db.query(Department).filter(
            Department.company_id == company_id,
            Department.is_corporate == True,
            Department.branch_id == None
        )

        if active_only:
            query = query.filter(Department.is_active == True, Department.is_deleted == False)

        return query.all()

    def get_by_code(self, company_id: int, code: str) -> Optional[Department]:
        """
        Obtiene un departamento por código dentro de una empresa.
        Usado para validar unicidad de código por empresa.
        """
        return self.db.query(Department).filter(
            Department.company_id == company_id,
            Department.code == code,
            Department.is_deleted == False
        ).first()

    def get_children(self, parent_id: int) -> List[Department]:
        """
        Obtiene los subdepartamentos directos de un departamento padre.
        """
        return self.db.query(Department).filter(
            Department.parent_id == parent_id,
            Department.is_deleted == False
        ).all()

    def has_active_children(self, department_id: int) -> bool:
        """
        Verifica si el departamento tiene subdepartamentos activos.
        """
        count = self.db.query(Department).filter(
            Department.parent_id == department_id,
            Department.is_active == True,
            Department.is_deleted == False
        ).count()
        return count > 0

    def has_active_employees(self, department_id: int) -> bool:
        """
        Verifica si el departamento tiene empleados activos.
        TODO: Implementar cuando se cree la entidad Employee.
        """
        # Placeholder - implementar cuando exista Employee
        return False

    def search(self, query: str, limit: int = 50) -> List[Department]:
        """Busca departamentos por nombre o código."""
        search_pattern = f"%{query}%"
        return self.db.query(Department).filter(
            (Department.name.ilike(search_pattern)) |
            (Department.code.ilike(search_pattern)),
            Department.is_deleted == False
        ).limit(limit).all()
