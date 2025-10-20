"""
Employee Repository - Database operations for Employee entity
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.shared.base_repository import BaseRepository
from app.entities.employees.models.employee import Employee


class EmployeeRepository(BaseRepository[Employee]):
    """Repository for Employee entity with custom queries"""

    def __init__(self, db: Session):
        super().__init__(Employee, db)

    def get_by_employee_code(self, company_id: int, employee_code: str) -> Optional[Employee]:
        """
        Obtiene un Employee por código dentro de una empresa específica.

        Args:
            company_id: ID de la empresa
            employee_code: Código del empleado

        Returns:
            Employee si existe, None si no
        """
        return self.db.query(Employee).filter(
            Employee.company_id == company_id,
            Employee.employee_code == employee_code,
            Employee.is_deleted == False
        ).first()

    def get_by_individual_id(self, individual_id: int) -> Optional[Employee]:
        """
        Obtiene un Employee por su Individual ID.

        Args:
            individual_id: ID del Individual

        Returns:
            Employee si existe, None si no
        """
        return self.db.query(Employee).filter(
            Employee.individual_id == individual_id,
            Employee.is_deleted == False
        ).first()

    def get_by_company(self, company_id: int, active_only: bool = True) -> List[Employee]:
        """
        Obtiene todos los employees de una empresa.

        Args:
            company_id: ID de la empresa
            active_only: Si True, solo employees activos

        Returns:
            Lista de Employees
        """
        from app.entities.individuals.models.individual import Individual

        query = self.db.query(Employee).join(Individual).filter(
            Employee.company_id == company_id,
            Employee.is_deleted == False
        )

        if active_only:
            query = query.filter(Employee.is_active == True)

        return query.order_by(Individual.last_name, Individual.first_name).all()

    def get_by_branch(self, branch_id: int, active_only: bool = True) -> List[Employee]:
        """
        Obtiene todos los employees de una sucursal.

        Args:
            branch_id: ID de la sucursal
            active_only: Si True, solo employees activos

        Returns:
            Lista de Employees
        """
        from app.entities.individuals.models.individual import Individual

        query = self.db.query(Employee).join(Individual).filter(
            Employee.branch_id == branch_id,
            Employee.is_deleted == False
        )

        if active_only:
            query = query.filter(Employee.is_active == True)

        return query.order_by(Individual.last_name, Individual.first_name).all()

    def get_by_department(self, department_id: int, active_only: bool = True) -> List[Employee]:
        """
        Obtiene todos los employees de un departamento.

        Args:
            department_id: ID del departamento
            active_only: Si True, solo employees activos

        Returns:
            Lista de Employees
        """
        from app.entities.individuals.models.individual import Individual

        query = self.db.query(Employee).join(Individual).filter(
            Employee.department_id == department_id,
            Employee.is_deleted == False
        )

        if active_only:
            query = query.filter(Employee.is_active == True)

        return query.order_by(Individual.last_name, Individual.first_name).all()

    def get_by_supervisor(self, supervisor_id: int, active_only: bool = True) -> List[Employee]:
        """
        Obtiene todos los subordinados de un supervisor.

        Args:
            supervisor_id: ID del supervisor
            active_only: Si True, solo employees activos

        Returns:
            Lista de Employees subordinados
        """
        from app.entities.individuals.models.individual import Individual

        query = self.db.query(Employee).join(Individual).filter(
            Employee.supervisor_id == supervisor_id,
            Employee.is_deleted == False
        )

        if active_only:
            query = query.filter(Employee.is_active == True)

        return query.order_by(Individual.last_name, Individual.first_name).all()

    def get_by_business_group(self, business_group_id: int, active_only: bool = True) -> List[Employee]:
        """
        Obtiene todos los employees de un grupo empresarial.

        Args:
            business_group_id: ID del grupo empresarial
            active_only: Si True, solo employees activos

        Returns:
            Lista de Employees
        """
        from app.entities.individuals.models.individual import Individual

        query = self.db.query(Employee).join(Individual).filter(
            Employee.business_group_id == business_group_id,
            Employee.is_deleted == False
        )

        if active_only:
            query = query.filter(Employee.is_active == True)

        return query.order_by(Individual.last_name, Individual.first_name).all()

    def get_by_employment_status(self, status: str, company_id: Optional[int] = None) -> List[Employee]:
        """
        Obtiene employees por estado laboral.

        Args:
            status: Estado laboral (activo, inactivo, etc)
            company_id: ID de empresa (opcional, para filtrar por empresa)

        Returns:
            Lista de Employees
        """
        from app.entities.individuals.models.individual import Individual

        query = self.db.query(Employee).join(Individual).filter(
            Employee.employment_status == status,
            Employee.is_deleted == False
        )

        if company_id:
            query = query.filter(Employee.company_id == company_id)

        return query.order_by(Individual.last_name, Individual.first_name).all()

    def search(self, query_text: str, company_id: Optional[int] = None, limit: int = 50) -> List[Employee]:
        """
        Busca employees por código o datos del Individual (nombre, email).
        Búsqueda case-insensitive.

        Args:
            query_text: Texto a buscar
            company_id: ID de empresa (opcional, para filtrar por empresa)
            limit: Límite de resultados

        Returns:
            Lista de Employees que coinciden
        """
        from app.entities.individuals.models.individual import Individual

        search_pattern = f"%{query_text}%"

        query = self.db.query(Employee).join(Individual).filter(
            Employee.is_deleted == False,
            or_(
                Employee.employee_code.ilike(search_pattern),
                Individual.first_name.ilike(search_pattern),
                Individual.last_name.ilike(search_pattern),
                Individual.email.ilike(search_pattern)
            )
        )

        if company_id:
            query = query.filter(Employee.company_id == company_id)

        return query.order_by(Individual.last_name, Individual.first_name).limit(limit).all()

    def has_active_subordinates(self, supervisor_id: int) -> bool:
        """
        Verifica si un supervisor tiene subordinados activos.

        Args:
            supervisor_id: ID del supervisor

        Returns:
            True si tiene subordinados activos, False si no
        """
        count = self.db.query(Employee).filter(
            Employee.supervisor_id == supervisor_id,
            Employee.is_active == True,
            Employee.is_deleted == False
        ).count()

        return count > 0