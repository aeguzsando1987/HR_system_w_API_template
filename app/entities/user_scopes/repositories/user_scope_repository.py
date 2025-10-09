"""
Repository para UserScope

Maneja las operaciones de base de datos para UserScopes.
Extiende BaseRepository con consultas específicas.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.shared.base_repository import BaseRepository
from app.entities.user_scopes.models.user_scope import UserScope
from app.entities.user_scopes.schemas.enums import ScopeTypeEnum


class UserScopeRepository(BaseRepository[UserScope]):
    """Repository para operaciones de UserScope."""

    def __init__(self, db: Session):
        super().__init__(UserScope, db)

    def get_by_user_id(self, user_id: int, active_only: bool = True) -> List[UserScope]:
        """
        Obtiene todos los scopes de un usuario.

        Args:
            user_id: ID del usuario
            active_only: Si True, solo retorna scopes activos

        Returns:
            Lista de UserScopes del usuario
        """
        query = self.db.query(UserScope).filter(
            UserScope.user_id == user_id,
            UserScope.is_deleted == False
        )

        if active_only:
            query = query.filter(UserScope.is_active == True)

        return query.all()

    def get_by_user_and_type(
        self,
        user_id: int,
        scope_type: ScopeTypeEnum,
        active_only: bool = True
    ) -> List[UserScope]:
        """
        Obtiene todos los scopes de un usuario de un tipo específico.

        Args:
            user_id: ID del usuario
            scope_type: Tipo de scope
            active_only: Si True, solo retorna scopes activos

        Returns:
            Lista de UserScopes del usuario filtrados por tipo
        """
        query = self.db.query(UserScope).filter(
            UserScope.user_id == user_id,
            UserScope.scope_type == scope_type,
            UserScope.is_deleted == False
        )

        if active_only:
            query = query.filter(UserScope.is_active == True)

        return query.all()

    def user_has_scope(
        self,
        user_id: int,
        scope_type: ScopeTypeEnum,
        entity_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si un usuario tiene un scope específico.

        Args:
            user_id: ID del usuario
            scope_type: Tipo de scope
            entity_id: ID de la entidad (opcional, solo para scopes no-GLOBAL)

        Returns:
            True si el usuario tiene el scope, False en caso contrario
        """
        query = self.db.query(UserScope).filter(
            UserScope.user_id == user_id,
            UserScope.scope_type == scope_type,
            UserScope.is_active == True,
            UserScope.is_deleted == False
        )

        # Filtrar por entity_id según el tipo de scope
        if scope_type == ScopeTypeEnum.BUSINESS_GROUP and entity_id:
            query = query.filter(UserScope.business_group_id == entity_id)
        elif scope_type == ScopeTypeEnum.COMPANY and entity_id:
            query = query.filter(UserScope.company_id == entity_id)
        elif scope_type == ScopeTypeEnum.BRANCH and entity_id:
            query = query.filter(UserScope.branch_id == entity_id)
        elif scope_type == ScopeTypeEnum.DEPARTMENT and entity_id:
            query = query.filter(UserScope.department_id == entity_id)

        return query.first() is not None

    def get_business_group_ids_for_user(self, user_id: int) -> List[int]:
        """
        Obtiene todos los IDs de BusinessGroups a los que tiene acceso un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de IDs de BusinessGroups
        """
        scopes = self.db.query(UserScope).filter(
            UserScope.user_id == user_id,
            UserScope.scope_type == ScopeTypeEnum.BUSINESS_GROUP,
            UserScope.business_group_id.isnot(None),
            UserScope.is_active == True,
            UserScope.is_deleted == False
        ).all()

        return [scope.business_group_id for scope in scopes if scope.business_group_id]

    def scope_exists(
        self,
        user_id: int,
        scope_type: ScopeTypeEnum,
        entity_id: Optional[int] = None,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si ya existe un scope idéntico (evitar duplicados).

        Args:
            user_id: ID del usuario
            scope_type: Tipo de scope
            entity_id: ID de la entidad
            exclude_id: ID del scope a excluir (para validación en UPDATE)

        Returns:
            True si existe, False en caso contrario
        """
        query = self.db.query(UserScope).filter(
            UserScope.user_id == user_id,
            UserScope.scope_type == scope_type,
            UserScope.is_deleted == False
        )

        # Filtrar por entity_id según tipo
        if scope_type == ScopeTypeEnum.BUSINESS_GROUP:
            query = query.filter(UserScope.business_group_id == entity_id)
        elif scope_type == ScopeTypeEnum.COMPANY:
            query = query.filter(UserScope.company_id == entity_id)
        elif scope_type == ScopeTypeEnum.BRANCH:
            query = query.filter(UserScope.branch_id == entity_id)
        elif scope_type == ScopeTypeEnum.DEPARTMENT:
            query = query.filter(UserScope.department_id == entity_id)

        if exclude_id:
            query = query.filter(UserScope.id != exclude_id)

        return query.first() is not None
