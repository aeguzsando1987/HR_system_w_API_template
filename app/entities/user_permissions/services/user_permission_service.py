"""
Service para UserPermission

Implementa la lógica de negocio y validaciones para permisos granulares.
Valida que endpoints existan y métodos HTTP sean válidos.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.entities.user_permissions.repositories.user_permission_repository import UserPermissionRepository
from app.entities.user_permissions.models.user_permission import UserPermission
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    BusinessRuleError
)


class UserPermissionService:
    """Service para lógica de negocio de UserPermission."""

    VALID_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserPermissionRepository(db)

    def _validate_permission_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos de un permiso.

        Validaciones:
        1. user_id es requerido
        2. endpoint es requerido y comienza con /api/
        3. method es requerido y válido (GET, POST, PUT, DELETE, PATCH)
        4. allowed es boolean

        Args:
            data: Diccionario con datos del permiso

        Raises:
            EntityValidationError: Si hay errores de validación
        """
        errors = {}

        # Validación 1: user_id requerido
        if "user_id" not in data or data["user_id"] is None:
            errors["user_id"] = "user_id es requerido"

        # Validación 2: endpoint requerido y formato válido
        if "endpoint" not in data or not data["endpoint"]:
            errors["endpoint"] = "endpoint es requerido"
        elif not data["endpoint"].startswith("/api/"):
            errors["endpoint"] = "endpoint debe comenzar con /api/"

        # Validación 3: method requerido y válido
        if "method" not in data or not data["method"]:
            errors["method"] = "method es requerido"
        elif data["method"] not in self.VALID_METHODS:
            errors["method"] = f"method debe ser uno de: {', '.join(self.VALID_METHODS)}"

        # Validación 4: allowed es boolean
        if "allowed" in data and not isinstance(data["allowed"], bool):
            errors["allowed"] = "allowed debe ser boolean (true/false)"

        if errors:
            raise EntityValidationError("UserPermission", errors)

    def create_permission(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> UserPermission:
        """
        Crea un nuevo permiso con validaciones.

        Args:
            data: Datos del permiso
            created_by: ID del usuario que crea

        Returns:
            UserPermission creado

        Raises:
            EntityValidationError: Si hay errores de validación
            EntityAlreadyExistsError: Si ya existe el permiso
        """
        # Validar datos
        self._validate_permission_data(data)

        # Verificar que no exista permiso duplicado
        if self.repository.permission_exists(
            data["user_id"],
            data["endpoint"],
            data["method"]
        ):
            raise EntityAlreadyExistsError(
                "UserPermission",
                "permiso",
                f"user_id={data['user_id']}, endpoint={data['endpoint']}, method={data['method']}"
            )

        # Agregar campo de auditoría
        if created_by:
            data["created_by"] = created_by

        # Crear permiso
        return self.repository.create(data)

    def update_permission(
        self,
        permission_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> UserPermission:
        """
        Actualiza un permiso existente.

        Solo permite actualizar el campo 'allowed' (true/false).

        Args:
            permission_id: ID del permiso a actualizar
            data: Datos a actualizar (solo 'allowed')
            updated_by: ID del usuario que actualiza

        Returns:
            UserPermission actualizado

        Raises:
            EntityNotFoundError: Si el permiso no existe
        """
        permission = self.repository.get_by_id(permission_id)
        if not permission:
            raise EntityNotFoundError("UserPermission", permission_id)

        # Validar que solo se actualice 'allowed'
        if "allowed" in data and not isinstance(data["allowed"], bool):
            raise EntityValidationError("UserPermission", {
                "allowed": "allowed debe ser boolean (true/false)"
            })

        # Agregar campo de auditoría
        if updated_by:
            data["updated_by"] = updated_by

        return self.repository.update(permission_id, data)

    def delete_permission(
        self,
        permission_id: int,
        deleted_by: Optional[int] = None
    ) -> UserPermission:
        """
        Elimina (soft delete) un permiso.

        Args:
            permission_id: ID del permiso a eliminar
            deleted_by: ID del usuario que elimina

        Returns:
            UserPermission eliminado

        Raises:
            EntityNotFoundError: Si el permiso no existe
        """
        permission = self.repository.get_by_id(permission_id)
        if not permission:
            raise EntityNotFoundError("UserPermission", permission_id)

        return self.repository.soft_delete(permission_id, deleted_by)

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
        permission = self.repository.get_by_id(permission_id)
        if not permission:
            raise EntityNotFoundError("UserPermission", permission_id)
        return permission

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
        return self.repository.get_by_user_id(user_id, active_only)

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
        return self.repository.get_all(skip, limit, active_only)

    def bulk_update_user_permissions(
        self,
        user_id: int,
        permissions: Dict[str, Dict[str, bool]],
        updated_by: int
    ) -> bool:
        """
        Actualización masiva de permisos de un usuario desde app móvil.

        Proceso:
        1. Valida estructura del JSON
        2. Elimina (soft delete) permisos existentes
        3. Crea nuevos permisos

        Args:
            user_id: ID del usuario
            permissions: Diccionario con estructura:
                {
                    "/api/v1/employees": {"GET": true, "POST": true},
                    "/api/v1/individuals/with-user": {"POST": true}
                }
            updated_by: ID del usuario que actualiza (Admin)

        Returns:
            True si exitoso

        Raises:
            EntityValidationError: Si estructura es inválida
            BusinessRuleError: Si ocurre error en transacción
        """
        # Validar estructura
        errors = {}
        for endpoint, methods in permissions.items():
            if not endpoint.startswith("/api/"):
                errors[endpoint] = "Endpoint debe comenzar con /api/"

            for method, allowed in methods.items():
                if method not in self.VALID_METHODS:
                    errors[f"{endpoint}.{method}"] = f"Método '{method}' no es válido"
                if not isinstance(allowed, bool):
                    errors[f"{endpoint}.{method}"] = "Valor debe ser boolean"

        if errors:
            raise EntityValidationError("BulkPermissionUpdate", errors)

        try:
            # 1. Limpiar permisos existentes
            self.repository.bulk_delete_by_user(user_id, deleted_by=updated_by)
            self.repository.db.flush()  # Forzar aplicación de cambios

            # 2. Crear nuevos permisos
            permissions_to_create = []
            for endpoint, methods in permissions.items():
                for method, allowed in methods.items():
                    permissions_to_create.append({
                        "user_id": user_id,
                        "endpoint": endpoint,
                        "method": method,
                        "allowed": allowed
                    })

            if permissions_to_create:
                self.repository.bulk_create(permissions_to_create, created_by=updated_by)

            return True

        except Exception as e:
            self.db.rollback()
            raise BusinessRuleError(f"Error en bulk update: {str(e)}")
