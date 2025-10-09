"""
Repository para UserPermission

Maneja las operaciones de base de datos para permisos granulares.
Extiende BaseRepository con consultas específicas para validación híbrida.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.shared.base_repository import BaseRepository
from app.entities.user_permissions.models.user_permission import UserPermission


class UserPermissionRepository(BaseRepository[UserPermission]):
    """Repository para operaciones de UserPermission."""

    def __init__(self, db: Session):
        super().__init__(UserPermission, db)

    def get_by_user_id(self, user_id: int, active_only: bool = True) -> List[UserPermission]:
        """
        Obtiene todos los permisos de un usuario.

        Args:
            user_id: ID del usuario
            active_only: Si True, solo retorna permisos activos

        Returns:
            Lista de permisos del usuario
        """
        query = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.is_deleted == False
        )

        if active_only:
            query = query.filter(UserPermission.is_active == True)

        return query.all()

    def get_permission(
        self,
        user_id: int,
        endpoint: str,
        method: str,
        active_only: bool = True
    ) -> Optional[UserPermission]:
        """
        Obtiene un permiso específico de un usuario.

        Usado en validación híbrida:
        1. Buscar permiso específico (ej: POST /individuals/with-user)
        2. Si no existe, buscar base (POST /individuals)

        Args:
            user_id: ID del usuario
            endpoint: Ruta del endpoint
            method: Método HTTP (GET, POST, etc.)
            active_only: Si True, solo considera permisos activos

        Returns:
            UserPermission si existe, None si no

        Ejemplo:
            # Buscar permiso específico
            perm = repo.get_permission(2, "/api/v1/individuals/with-user", "POST")
        """
        query = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.endpoint == endpoint,
            UserPermission.method == method,
            UserPermission.is_deleted == False
        )

        if active_only:
            query = query.filter(UserPermission.is_active == True)

        return query.first()

    def permission_exists(
        self,
        user_id: int,
        endpoint: str,
        method: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si ya existe un permiso (evita duplicados).

        Args:
            user_id: ID del usuario
            endpoint: Ruta del endpoint
            method: Método HTTP
            exclude_id: ID a excluir (para validación en UPDATE)

        Returns:
            True si existe, False si no
        """
        query = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.endpoint == endpoint,
            UserPermission.method == method,
            UserPermission.is_deleted == False
        )

        if exclude_id:
            query = query.filter(UserPermission.id != exclude_id)

        return query.first() is not None

    def get_permissions_by_endpoint(
        self,
        user_id: int,
        endpoint: str,
        active_only: bool = True
    ) -> List[UserPermission]:
        """
        Obtiene todos los permisos de un usuario para un endpoint.

        Útil para obtener todos los métodos permitidos (GET, POST, PUT, DELETE).

        Args:
            user_id: ID del usuario
            endpoint: Ruta del endpoint
            active_only: Si True, solo permisos activos

        Returns:
            Lista de permisos para ese endpoint

        Ejemplo:
            perms = repo.get_permissions_by_endpoint(2, "/api/v1/employees")
            # Retorna: [GET: true, POST: true, DELETE: false]
        """
        query = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.endpoint == endpoint,
            UserPermission.is_deleted == False
        )

        if active_only:
            query = query.filter(UserPermission.is_active == True)

        return query.all()

    def bulk_create(
        self,
        permissions: List[dict],
        created_by: Optional[int] = None
    ) -> List[UserPermission]:
        """
        Crea múltiples permisos en una transacción.

        Usado cuando Admin actualiza permisos desde app móvil.

        Args:
            permissions: Lista de diccionarios con datos de permisos
            created_by: ID del usuario que crea

        Returns:
            Lista de permisos creados

        Ejemplo:
            perms_data = [
                {"user_id": 2, "endpoint": "/api/v1/employees", "method": "GET", "allowed": True},
                {"user_id": 2, "endpoint": "/api/v1/employees", "method": "POST", "allowed": True}
            ]
            repo.bulk_create(perms_data, created_by=1)
        """
        created_permissions = []

        for perm_data in permissions:
            if created_by:
                perm_data["created_by"] = created_by

            permission = UserPermission(**perm_data)
            self.db.add(permission)
            created_permissions.append(permission)

        self.db.commit()

        # Refresh todos los permisos
        for perm in created_permissions:
            self.db.refresh(perm)

        return created_permissions

    def bulk_delete_by_user(
        self,
        user_id: int,
        deleted_by: Optional[int] = None
    ) -> int:
        """
        Elimina (soft delete) todos los permisos de un usuario.

        Usado antes de bulk update para limpiar permisos existentes.

        Args:
            user_id: ID del usuario
            deleted_by: ID del usuario que elimina

        Returns:
            Número de permisos eliminados

        Ejemplo:
            # Admin actualiza permisos de Ana
            repo.bulk_delete_by_user(2, deleted_by=1)  # Limpiar permisos existentes
            repo.bulk_create(new_permissions, created_by=1)  # Crear nuevos
        """
        from datetime import datetime

        permissions = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.is_deleted == False
        ).all()

        count = 0
        for perm in permissions:
            perm.is_deleted = True
            perm.is_active = False
            perm.deleted_at = datetime.utcnow()
            if deleted_by:
                perm.deleted_by = deleted_by
            count += 1

        self.db.commit()
        return count

    def get_allowed_endpoints(
        self,
        user_id: int,
        method: Optional[str] = None
    ) -> List[str]:
        """
        Obtiene lista de endpoints permitidos para un usuario.

        Útil para generar lista de recursos accesibles.

        Args:
            user_id: ID del usuario
            method: Filtrar por método (opcional)

        Returns:
            Lista de endpoints donde allowed=True

        Ejemplo:
            endpoints = repo.get_allowed_endpoints(2, method="GET")
            # ["/api/v1/employees", "/api/v1/business-groups"]
        """
        query = self.db.query(UserPermission.endpoint).filter(
            UserPermission.user_id == user_id,
            UserPermission.allowed == True,
            UserPermission.is_active == True,
            UserPermission.is_deleted == False
        )

        if method:
            query = query.filter(UserPermission.method == method)

        results = query.distinct().all()
        return [result[0] for result in results]

    def count_permissions_by_user(self, user_id: int) -> int:
        """
        Cuenta total de permisos activos de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Número de permisos activos
        """
        return self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.is_active == True,
            UserPermission.is_deleted == False
        ).count()
