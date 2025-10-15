"""
Individual Controller - Manejo de excepciones y orquestación
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.entities.individuals.services.individual_service import IndividualService
from app.entities.individuals.models.individual import Individual
from app.shared.exceptions import EntityNotFoundError, EntityValidationError, BusinessRuleError, EntityAlreadyExistsError


class IndividualController:
    """Controller para orquestar operaciones de Individual"""

    def __init__(self, db: Session):
        self.service = IndividualService(db)

    def create_individual(
        self,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Individual:
        """Crea un nuevo Individual (sin User)."""
        try:
            return self.service.create_individual(data, created_by=current_user_id)
        except (EntityNotFoundError, EntityValidationError, BusinessRuleError, EntityAlreadyExistsError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al crear individual: {str(e)}")

    def create_individual_with_user(
        self,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Individual:
        """Crea un Individual + User en transacción atómica."""
        try:
            return self.service.create_individual_with_user(data, created_by=current_user_id)
        except (EntityNotFoundError, EntityValidationError, BusinessRuleError, EntityAlreadyExistsError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al crear individual con usuario: {str(e)}")

    def get_individual(self, individual_id: int) -> Individual:
        """Obtiene un Individual por ID."""
        try:
            return self.service.get_individual_by_id(individual_id)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al obtener individual: {str(e)}")

    def update_individual(
        self,
        individual_id: int,
        data: Dict[str, Any],
        current_user_id: Optional[int] = None
    ) -> Individual:
        """Actualiza un Individual."""
        try:
            return self.service.update_individual(individual_id, data, updated_by=current_user_id)
        except (EntityNotFoundError, EntityValidationError, BusinessRuleError, EntityAlreadyExistsError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al actualizar individual: {str(e)}")

    def delete_individual(
        self,
        individual_id: int,
        current_user_id: Optional[int] = None
    ) -> bool:
        """Elimina un Individual (soft delete)."""
        try:
            return self.service.delete_individual(individual_id, deleted_by=current_user_id)
        except (EntityNotFoundError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al eliminar individual: {str(e)}")

    def search_individuals(self, query: str, limit: int = 50) -> List[Individual]:
        """Busca Individuals por nombre, apellido o email."""
        try:
            return self.service.search_individuals(query, limit)
        except Exception as e:
            raise Exception(f"Error al buscar individuals: {str(e)}")

    def get_individual_by_document(self, document_number: str) -> Optional[Individual]:
        """Obtiene Individual por número de documento."""
        try:
            return self.service.get_individual_by_document(document_number)
        except Exception as e:
            raise Exception(f"Error al buscar individual por documento: {str(e)}")

    def get_individual_by_curp(self, curp: str) -> Optional[Individual]:
        """Obtiene Individual por CURP."""
        try:
            return self.service.get_individual_by_curp(curp)
        except Exception as e:
            raise Exception(f"Error al buscar individual por CURP: {str(e)}")