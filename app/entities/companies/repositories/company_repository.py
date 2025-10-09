"""
Repository: Company

Operaciones de base de datos para Company.
Hereda de BaseRepository para operaciones CRUD estándar.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.shared.base_repository import BaseRepository
from app.entities.companies.models.company import Company


class CompanyRepository(BaseRepository[Company]):
    """
    Repositorio para Company.

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
        """Inicializa el repositorio con el modelo Company."""
        super().__init__(Company, db)

    # ==================== MÉTODOS PERSONALIZADOS ====================

    def get_by_business_group(self, business_group_id: int, active_only: bool = True) -> List[Company]:
        """
        Obtiene todas las Companies de un BusinessGroup.

        Args:
            business_group_id: ID del BusinessGroup
            active_only: Si True, solo retorna companies activas

        Returns:
            Lista de Companies del BusinessGroup
        """
        query = self.db.query(Company).filter(
            Company.business_group_id == business_group_id,
            Company.is_deleted == False
        )

        if active_only:
            query = query.filter(Company.is_active == True)

        return query.all()

    def get_by_tax_id(self, tax_id: str) -> Optional[Company]:
        """
        Busca una Company por su tax_id (RFC/RUT/NIT).

        Args:
            tax_id: Identificación fiscal a buscar

        Returns:
            Company encontrada o None
        """
        return self.db.query(Company).filter(
            Company.tax_id == tax_id
        ).first()

    def get_by_code(self, code: str) -> Optional[Company]:
        """
        Busca una Company por su código.

        Args:
            code: Código de la company

        Returns:
            Company encontrada o None
        """
        return self.db.query(Company).filter(
            Company.code == code
        ).first()

    def search_by_name(self, name: str, limit: int = 50) -> List[Company]:
        """
        Busca Companies por nombre (case-insensitive).

        Args:
            name: Término a buscar en el nombre
            limit: Máximo de resultados

        Returns:
            Lista de Companies que coinciden
        """
        return self.search(
            search_term=name,
            search_fields=["name", "legal_name", "code"],
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

        query = self.db.query(Company).filter(Company.tax_id == tax_id)

        if exclude_id:
            query = query.filter(Company.id != exclude_id)

        return query.first() is not None

    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un código ya está en uso.

        Args:
            code: Código a verificar
            exclude_id: ID a excluir de la búsqueda (útil para updates)

        Returns:
            True si el código ya existe, False si no
        """
        query = self.db.query(Company).filter(Company.code == code)

        if exclude_id:
            query = query.filter(Company.id != exclude_id)

        return query.first() is not None

    # ==================== MÉTODOS PARA VALIDACIÓN DE DEPENDENCIAS ====================

    def has_active_branches(self, company_id: int) -> bool:
        """
        Verifica si la Company tiene Branches activas.

        Args:
            company_id: ID de la Company

        Returns:
            True si tiene branches activas, False si no
        """
        # TODO: Implementar cuando exista la entidad Branch
        # from app.entities.branches.models.branch import Branch
        # return self.db.query(Branch).filter(
        #     Branch.company_id == company_id,
        #     Branch.is_active == True,
        #     Branch.is_deleted == False
        # ).first() is not None
        return False

    def has_active_departments(self, company_id: int) -> bool:
        """
        Verifica si la Company tiene Departments activos.

        Args:
            company_id: ID de la Company

        Returns:
            True si tiene departments activos, False si no
        """
        # TODO: Implementar cuando exista la entidad Department
        # from app.entities.departments.models.department import Department
        # return self.db.query(Department).filter(
        #     Department.company_id == company_id,
        #     Department.is_active == True,
        #     Department.is_deleted == False
        # ).first() is not None
        return False

    def has_active_positions(self, company_id: int) -> bool:
        """
        Verifica si la Company tiene Positions activas.

        Args:
            company_id: ID de la Company

        Returns:
            True si tiene positions activas, False si no
        """
        # TODO: Implementar cuando exista la entidad Position
        # from app.entities.positions.models.position import Position
        # return self.db.query(Position).filter(
        #     Position.company_id == company_id,
        #     Position.is_active == True,
        #     Position.is_deleted == False
        # ).first() is not None
        return False

    def has_active_employees(self, company_id: int) -> bool:
        """
        Verifica si la Company tiene Employees activos.

        Args:
            company_id: ID de la Company

        Returns:
            True si tiene employees activos, False si no
        """
        # TODO: Implementar cuando exista la entidad Employee
        # from app.entities.employees.models.employee import Employee
        # return self.db.query(Employee).filter(
        #     Employee.company_id == company_id,
        #     Employee.is_active == True,
        #     Employee.is_deleted == False
        # ).first() is not None
        return False
