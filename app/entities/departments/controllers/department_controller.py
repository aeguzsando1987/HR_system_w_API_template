"""
Controller: Department

Manejo de requests y responses para Department.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.entities.departments.services.department_service import DepartmentService
from app.entities.departments.models.department import Department
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)


class DepartmentController:
    """Controller para Department."""

    def __init__(self, db: Session):
        """Inicializa el controller con el servicio."""
        self.service = DepartmentService(db)

    def create_department(
        self,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Department:
        """Crea un nuevo Department."""
        try:
            return self.service.create_department(data, created_by=current_user_id)
        except (EntityValidationError, EntityAlreadyExistsError, EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al crear department: {str(e)}")

    def get_department(self, department_id: int) -> Department:
        """Obtiene un Department por ID."""
        try:
            return self.service.get_department_by_id(department_id)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al obtener department: {str(e)}")

    def get_all_departments(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ):
        """Obtiene todos los Departments."""
        try:
            return self.service.get_all_departments(skip, limit, active_only)
        except Exception as e:
            raise Exception(f"Error al listar departments: {str(e)}")

    def update_department(
        self,
        department_id: int,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Department:
        """Actualiza un Department."""
        try:
            return self.service.update_department(department_id, data, updated_by=current_user_id)
        except (EntityValidationError, EntityAlreadyExistsError, EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al actualizar department: {str(e)}")

    def delete_department(
        self,
        department_id: int,
        current_user_id: Optional[int] = None
    ) -> bool:
        """Elimina un Department (soft delete)."""
        try:
            return self.service.delete_department(department_id, deleted_by=current_user_id)
        except (EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al eliminar department: {str(e)}")

    def search_departments(self, query: str, limit: int = 50):
        """Busca Departments por nombre o código."""
        try:
            return self.service.search_departments(query, limit)
        except Exception as e:
            raise Exception(f"Error al buscar departments: {str(e)}")

    def get_departments_by_company(self, company_id: int, active_only: bool = True):
        """Obtiene Departments por Company."""
        try:
            return self.service.get_departments_by_company(company_id, active_only)
        except Exception as e:
            raise Exception(f"Error al obtener departments por company: {str(e)}")

    def get_departments_by_branch(self, branch_id: int, active_only: bool = True):
        """Obtiene Departments por Branch."""
        try:
            return self.service.get_departments_by_branch(branch_id, active_only)
        except Exception as e:
            raise Exception(f"Error al obtener departments por branch: {str(e)}")

    def paginate_departments(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ):
        """Obtiene Departments paginados."""
        try:
            return self.service.paginate_departments(page, per_page)
        except Exception as e:
            raise Exception(f"Error al paginar departments: {str(e)}")
