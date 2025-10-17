"""
Employee Controller - Request/Response handling for Employee entity
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.entities.employees.services.employee_service import EmployeeService
from app.entities.employees.models.employee import Employee


class EmployeeController:
    """Controller for Employee entity"""

    def __init__(self, db: Session):
        self.service = EmployeeService(db)

    def create_employee(self, data: Dict[str, Any], current_user_id: Optional[int] = None) -> Employee:
        """
        Crea un Employee (requiere Individual existente).

        Args:
            data: Datos del Employee
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            Employee creado
        """
        return self.service.create_employee(data, created_by=current_user_id)

    def create_employee_with_user(self, data: Dict[str, Any], current_user_id: Optional[int] = None) -> Employee:
        """
        Crea Employee + Individual + User en transacción atómica.

        Args:
            data: Datos de Individual, User (opcional), y Employee
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            Employee creado
        """
        return self.service.create_employee_with_user(data, created_by=current_user_id)

    def get_employee(self, employee_id: int) -> Employee:
        """Obtiene un Employee por ID"""
        return self.service.get_employee(employee_id)

    def update_employee(self, employee_id: int, data: Dict[str, Any], current_user_id: Optional[int] = None) -> Employee:
        """Actualiza un Employee"""
        return self.service.update_employee(employee_id, data, updated_by=current_user_id)

    def delete_employee(self, employee_id: int, current_user_id: Optional[int] = None) -> None:
        """Elimina un Employee (soft delete)"""
        self.service.delete_employee(employee_id, deleted_by=current_user_id)

    def search_employees(self, query_text: str, company_id: Optional[int] = None, limit: int = 50):
        """Busca employees por código, nombre, email"""
        return self.service.repository.search(query_text, company_id, limit)

    def get_by_company(self, company_id: int, active_only: bool = True):
        """Obtiene employees por company"""
        return self.service.repository.get_by_company(company_id, active_only)

    def get_by_supervisor(self, supervisor_id: int, active_only: bool = True):
        """Obtiene subordinados de un supervisor"""
        return self.service.repository.get_by_supervisor(supervisor_id, active_only)
