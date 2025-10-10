"""
Controller: Branch

Manejo de requests y responses para Branch.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.entities.branches.services.branch_service import BranchService
from app.entities.branches.models.branch import Branch
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)


class BranchController:
    """Controller para Branch."""

    def __init__(self, db: Session):
        """Inicializa el controller con el servicio."""
        self.service = BranchService(db)

    def create_branch(
        self,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Branch:
        """Crea una nueva Branch."""
        try:
            return self.service.create_branch(data, created_by=current_user_id)
        except (EntityValidationError, EntityAlreadyExistsError, EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al crear branch: {str(e)}")

    def get_branch(self, branch_id: int) -> Branch:
        """Obtiene una Branch por ID."""
        try:
            return self.service.get_branch_by_id(branch_id)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al obtener branch: {str(e)}")

    def get_all_branches(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ):
        """Obtiene todas las Branches."""
        try:
            return self.service.get_all_branches(skip, limit, active_only)
        except Exception as e:
            raise Exception(f"Error al listar branches: {str(e)}")

    def update_branch(
        self,
        branch_id: int,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Branch:
        """Actualiza una Branch."""
        try:
            return self.service.update_branch(branch_id, data, updated_by=current_user_id)
        except (EntityValidationError, EntityAlreadyExistsError, EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al actualizar branch: {str(e)}")

    def delete_branch(
        self,
        branch_id: int,
        current_user_id: Optional[int] = None
    ) -> bool:
        """Elimina una Branch (soft delete)."""
        try:
            return self.service.delete_branch(branch_id, deleted_by=current_user_id)
        except (EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al eliminar branch: {str(e)}")

    def search_branches(self, name: str, limit: int = 50):
        """Busca Branches por nombre."""
        try:
            return self.service.search_branches(name, limit)
        except Exception as e:
            raise Exception(f"Error al buscar branches: {str(e)}")

    def get_branches_by_company(self, company_id: int, active_only: bool = True):
        """Obtiene Branches por Company."""
        try:
            return self.service.get_branches_by_company(company_id, active_only)
        except Exception as e:
            raise Exception(f"Error al obtener branches por company: {str(e)}")

    def paginate_branches(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ):
        """Obtiene Branches paginadas."""
        try:
            return self.service.paginate_branches(page, per_page)
        except Exception as e:
            raise Exception(f"Error al paginar branches: {str(e)}")
