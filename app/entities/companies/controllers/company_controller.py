"""
Controller: Company

Manejo de requests y responses para Company.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.entities.companies.services.company_service import CompanyService
from app.entities.companies.models.company import Company
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)


class CompanyController:
    """Controller para Company."""

    def __init__(self, db: Session):
        """Inicializa el controller con el servicio."""
        self.service = CompanyService(db)

    def create_company(
        self,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Company:
        """Crea una nueva Company."""
        try:
            return self.service.create_company(data, created_by=current_user_id)
        except (EntityValidationError, EntityAlreadyExistsError, EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al crear company: {str(e)}")

    def get_company(self, company_id: int) -> Company:
        """Obtiene una Company por ID."""
        try:
            return self.service.get_company_by_id(company_id)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al obtener company: {str(e)}")

    def get_all_companies(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ):
        """Obtiene todas las Companies."""
        try:
            return self.service.get_all_companies(skip, limit, active_only)
        except Exception as e:
            raise Exception(f"Error al listar companies: {str(e)}")

    def update_company(
        self,
        company_id: int,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Company:
        """Actualiza una Company."""
        try:
            return self.service.update_company(company_id, data, updated_by=current_user_id)
        except (EntityValidationError, EntityAlreadyExistsError, EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al actualizar company: {str(e)}")

    def delete_company(
        self,
        company_id: int,
        current_user_id: Optional[int] = None
    ) -> bool:
        """Elimina una Company (soft delete)."""
        try:
            return self.service.delete_company(company_id, deleted_by=current_user_id)
        except (EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al eliminar company: {str(e)}")

    def search_companies(self, name: str, limit: int = 50):
        """Busca Companies por nombre."""
        try:
            return self.service.search_companies(name, limit)
        except Exception as e:
            raise Exception(f"Error al buscar companies: {str(e)}")

    def paginate_companies(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ):
        """Obtiene Companies paginadas."""
        try:
            return self.service.paginate_companies(page, per_page, filters)
        except Exception as e:
            raise Exception(f"Error al paginar companies: {str(e)}")
