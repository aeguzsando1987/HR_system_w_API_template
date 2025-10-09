"""
Controller para UserScope

Maneja las excepciones y coordina entre Router y Service.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.entities.user_scopes.services.user_scope_service import UserScopeService
from app.entities.user_scopes.models.user_scope import UserScope
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    BusinessRuleError
)


class UserScopeController:
    """Controller para coordinar operaciones de UserScope."""

    def __init__(self, db: Session):
        self.db = db
        self.service = UserScopeService(db)

    def create_user_scope(
        self,
        data: Dict[str, Any],
        user_role: int,
        created_by: Optional[int] = None
    ) -> UserScope:
        """
        Crea un nuevo UserScope.

        Args:
            data: Datos del UserScope
            user_role: Rol del usuario que recibe el scope
            created_by: ID del usuario que crea

        Returns:
            UserScope creado

        Raises:
            EntityValidationError: Si hay errores de validación
            EntityAlreadyExistsError: Si ya existe un scope idéntico
            BusinessRuleError: Si se viola una regla de negocio
        """
        try:
            return self.service.create_user_scope(data, user_role, created_by)
        except (EntityValidationError, EntityAlreadyExistsError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al crear UserScope: {str(e)}")

    def update_user_scope(
        self,
        user_scope_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> UserScope:
        """
        Actualiza un UserScope existente.

        Args:
            user_scope_id: ID del UserScope
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            UserScope actualizado

        Raises:
            EntityNotFoundError: Si el UserScope no existe
        """
        try:
            return self.service.update_user_scope(user_scope_id, data, updated_by)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al actualizar UserScope: {str(e)}")

    def delete_user_scope(
        self,
        user_scope_id: int,
        deleted_by: Optional[int] = None
    ) -> UserScope:
        """
        Elimina (soft delete) un UserScope.

        Args:
            user_scope_id: ID del UserScope
            deleted_by: ID del usuario que elimina

        Returns:
            UserScope eliminado

        Raises:
            EntityNotFoundError: Si el UserScope no existe
        """
        try:
            return self.service.delete_user_scope(user_scope_id, deleted_by)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al eliminar UserScope: {str(e)}")

    def get_user_scope(self, user_scope_id: int) -> UserScope:
        """
        Obtiene un UserScope por ID.

        Args:
            user_scope_id: ID del UserScope

        Returns:
            UserScope encontrado

        Raises:
            EntityNotFoundError: Si el UserScope no existe
        """
        try:
            return self.service.get_user_scope(user_scope_id)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al obtener UserScope: {str(e)}")

    def get_scopes_by_user(self, user_id: int, active_only: bool = True) -> List[UserScope]:
        """
        Obtiene todos los scopes de un usuario.

        Args:
            user_id: ID del usuario
            active_only: Si True, solo retorna scopes activos

        Returns:
            Lista de UserScopes
        """
        try:
            return self.service.get_scopes_by_user(user_id, active_only)
        except Exception as e:
            raise Exception(f"Error al obtener scopes del usuario: {str(e)}")

    def get_all_user_scopes(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[UserScope]:
        """
        Obtiene todos los UserScopes con paginación.

        Args:
            skip: Registros a saltar
            limit: Máximo de registros
            active_only: Si True, solo retorna activos

        Returns:
            Lista de UserScopes
        """
        try:
            return self.service.get_all_user_scopes(skip, limit, active_only)
        except Exception as e:
            raise Exception(f"Error al obtener UserScopes: {str(e)}")
