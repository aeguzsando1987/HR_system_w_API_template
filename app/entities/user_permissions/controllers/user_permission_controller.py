"""
Controller para UserPermission

Maneja las excepciones y coordina entre Router y Service.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.entities.user_permissions.services.user_permission_service import UserPermissionService
from app.entities.user_permissions.models.user_permission import UserPermission
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    BusinessRuleError
)


class UserPermissionController:
    """Controller para coordinar operaciones de UserPermission."""

    def __init__(self, db: Session):
        self.db = db
        self.service = UserPermissionService(db)

    def create_permission(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> UserPermission:
        """
        Crea un nuevo permiso.

        Args:
            data: Datos del permiso
            created_by: ID del usuario que crea

        Returns:
            UserPermission creado

        Raises:
            EntityValidationError: Si hay errores de validación
            EntityAlreadyExistsError: Si ya existe el permiso
        """
        try:
            return self.service.create_permission(data, created_by)
        except (EntityValidationError, EntityAlreadyExistsError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al crear permiso: {str(e)}")

    def update_permission(
        self,
        permission_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> UserPermission:
        """
        Actualiza un permiso existente.

        Args:
            permission_id: ID del permiso
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            UserPermission actualizado

        Raises:
            EntityNotFoundError: Si el permiso no existe
            EntityValidationError: Si hay errores de validación
        """
        try:
            return self.service.update_permission(permission_id, data, updated_by)
        except (EntityNotFoundError, EntityValidationError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al actualizar permiso: {str(e)}")

    def delete_permission(
        self,
        permission_id: int,
        deleted_by: Optional[int] = None
    ) -> UserPermission:
        """
        Elimina (soft delete) un permiso.

        Args:
            permission_id: ID del permiso
            deleted_by: ID del usuario que elimina

        Returns:
            UserPermission eliminado

        Raises:
            EntityNotFoundError: Si el permiso no existe
        """
        try:
            return self.service.delete_permission(permission_id, deleted_by)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al eliminar permiso: {str(e)}")

    def get_permission(self, permission_id: int) -> UserPermission:
        """
        Obtiene un permiso por ID.

        Args:
            permission_id: ID del permiso

        Returns:
            UserPermission encontrado

        Raises:
            EntityNotFoundError: Si el permiso no existe
        """
        try:
            return self.service.get_permission(permission_id)
        except EntityNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al obtener permiso: {str(e)}")

    def get_permissions_by_user(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[UserPermission]:
        """
        Obtiene todos los permisos de un usuario.

        Args:
            user_id: ID del usuario
            active_only: Si True, solo permisos activos

        Returns:
            Lista de permisos
        """
        try:
            return self.service.get_permissions_by_user(user_id, active_only)
        except Exception as e:
            raise Exception(f"Error al obtener permisos del usuario: {str(e)}")

    def get_all_permissions(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[UserPermission]:
        """
        Obtiene todos los permisos con paginación.

        Args:
            skip: Registros a saltar
            limit: Máximo de registros
            active_only: Si True, solo permisos activos

        Returns:
            Lista de permisos
        """
        try:
            return self.service.get_all_permissions(skip, limit, active_only)
        except Exception as e:
            raise Exception(f"Error al obtener permisos: {str(e)}")

    def bulk_update_user_permissions(
        self,
        user_id: int,
        permissions: Dict[str, Dict[str, bool]],
        updated_by: int
    ) -> bool:
        """
        Actualización masiva de permisos de un usuario.

        Usado por app móvil para actualizar todos los permisos.

        Args:
            user_id: ID del usuario
            permissions: Diccionario con permisos
            updated_by: ID del usuario que actualiza (Admin)

        Returns:
            True si exitoso

        Raises:
            EntityValidationError: Si estructura es inválida
            BusinessRuleError: Si ocurre error en transacción
        """
        try:
            return self.service.bulk_update_user_permissions(
                user_id,
                permissions,
                updated_by
            )
        except (EntityValidationError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise Exception(f"Error en bulk update: {str(e)}")
