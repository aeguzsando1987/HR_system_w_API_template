"""
Service para UserScope

Implementa la lógica de negocio y validaciones para UserScopes.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.entities.user_scopes.repositories.user_scope_repository import UserScopeRepository
from app.entities.user_scopes.models.user_scope import UserScope
from app.entities.user_scopes.schemas.enums import ScopeTypeEnum
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    BusinessRuleError,
    EntityAlreadyExistsError
)


class UserScopeService:
    """Service para lógica de negocio de UserScope."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserScopeRepository(db)

    def _validate_user_scope_data(self, data: Dict[str, Any], user_role: int) -> None:
        """
        Valida los datos de un UserScope según reglas de negocio.

        Reglas:
        1. user_id es requerido
        2. scope_type es requerido
        3. Admin (role=1): Puede tener cualquier scope
        4. Gerente (role=2): Solo puede tener BUSINESS_GROUP, COMPANY o BRANCH
        5. Gestor (role=3): Solo puede tener DEPARTMENT
        6. Colaborador (role=4) y Guest (role=5): NO pueden tener scopes
        7. Exactamente UNO de los IDs debe estar poblado según scope_type
        8. GLOBAL: ningún ID debe estar poblado
        9. BUSINESS_GROUP: solo business_group_id
        10. COMPANY: solo company_id
        11. BRANCH: solo branch_id
        12. DEPARTMENT: solo department_id

        Args:
            data: Diccionario con datos del UserScope
            user_role: Rol del usuario (1=Admin, 2=Gerente, 3=Gestor, 4=Colaborador, 5=Guest)

        Raises:
            EntityValidationError: Si hay errores de validación
        """
        errors = {}

        # Validación 1: user_id requerido
        if "user_id" not in data or data["user_id"] is None:
            errors["user_id"] = "user_id es requerido"

        # Validación 2: scope_type requerido
        if "scope_type" not in data or data["scope_type"] is None:
            errors["scope_type"] = "scope_type es requerido"

        if errors:
            raise EntityValidationError("UserScope", errors)

        scope_type = data["scope_type"]

        # Validaciones 3-6: Reglas por rol
        if user_role == 4 or user_role == 5:  # Colaborador o Guest
            raise BusinessRuleError(
                f"Los usuarios con rol {user_role} (Colaborador/Guest) no pueden tener scopes asignados"
            )

        if user_role == 3:  # Gestor
            if scope_type != ScopeTypeEnum.DEPARTMENT:
                errors["scope_type"] = "Los Gestores solo pueden tener scope DEPARTMENT"

        if user_role == 2:  # Gerente
            allowed_scopes = [ScopeTypeEnum.BUSINESS_GROUP, ScopeTypeEnum.COMPANY, ScopeTypeEnum.BRANCH]
            if scope_type not in allowed_scopes:
                errors["scope_type"] = "Los Gerentes solo pueden tener scopes BUSINESS_GROUP, COMPANY o BRANCH"

        # Validaciones 7-12: Coherencia entre scope_type y entity IDs
        business_group_id = data.get("business_group_id")
        company_id = data.get("company_id")
        branch_id = data.get("branch_id")
        department_id = data.get("department_id")

        if scope_type == ScopeTypeEnum.GLOBAL:
            # No debe tener ningún ID poblado
            if any([business_group_id, company_id, branch_id, department_id]):
                errors["scope_type"] = "GLOBAL no debe tener ningún entity_id asociado"

        elif scope_type == ScopeTypeEnum.BUSINESS_GROUP:
            # Solo business_group_id debe estar poblado
            if not business_group_id:
                errors["business_group_id"] = "business_group_id es requerido para scope BUSINESS_GROUP"
            if any([company_id, branch_id, department_id]):
                errors["scope_type"] = "BUSINESS_GROUP solo debe tener business_group_id poblado"

        elif scope_type == ScopeTypeEnum.COMPANY:
            # Solo company_id debe estar poblado
            if not company_id:
                errors["company_id"] = "company_id es requerido para scope COMPANY"
            if any([business_group_id, branch_id, department_id]):
                errors["scope_type"] = "COMPANY solo debe tener company_id poblado"

        elif scope_type == ScopeTypeEnum.BRANCH:
            # Solo branch_id debe estar poblado
            if not branch_id:
                errors["branch_id"] = "branch_id es requerido para scope BRANCH"
            if any([business_group_id, company_id, department_id]):
                errors["scope_type"] = "BRANCH solo debe tener branch_id poblado"

        elif scope_type == ScopeTypeEnum.DEPARTMENT:
            # Solo department_id debe estar poblado
            if not department_id:
                errors["department_id"] = "department_id es requerido para scope DEPARTMENT"
            if any([business_group_id, company_id, branch_id]):
                errors["scope_type"] = "DEPARTMENT solo debe tener department_id poblado"

        if errors:
            raise EntityValidationError("UserScope", errors)

    def create_user_scope(
        self,
        data: Dict[str, Any],
        user_role: int,
        created_by: Optional[int] = None
    ) -> UserScope:
        """
        Crea un nuevo UserScope con validaciones de negocio.

        Args:
            data: Datos del UserScope
            user_role: Rol del usuario que recibe el scope
            created_by: ID del usuario que crea el scope

        Returns:
            UserScope creado

        Raises:
            EntityValidationError: Si hay errores de validación
            EntityAlreadyExistsError: Si ya existe un scope idéntico
        """
        # Validar datos
        self._validate_user_scope_data(data, user_role)

        # Verificar que no exista un scope idéntico
        entity_id = None
        if data["scope_type"] == ScopeTypeEnum.BUSINESS_GROUP:
            entity_id = data.get("business_group_id")
        elif data["scope_type"] == ScopeTypeEnum.COMPANY:
            entity_id = data.get("company_id")
        elif data["scope_type"] == ScopeTypeEnum.BRANCH:
            entity_id = data.get("branch_id")
        elif data["scope_type"] == ScopeTypeEnum.DEPARTMENT:
            entity_id = data.get("department_id")

        if self.repository.scope_exists(data["user_id"], data["scope_type"], entity_id):
            raise EntityAlreadyExistsError(
                "UserScope",
                "scope",
                f"user_id={data['user_id']}, scope_type={data['scope_type']}, entity_id={entity_id}"
            )

        # Agregar campo de auditoría
        if created_by:
            data["created_by"] = created_by

        # Crear el scope
        return self.repository.create(data)

    def update_user_scope(
        self,
        user_scope_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> UserScope:
        """
        Actualiza un UserScope existente.

        Args:
            user_scope_id: ID del UserScope a actualizar
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            UserScope actualizado

        Raises:
            EntityNotFoundError: Si el UserScope no existe
        """
        user_scope = self.repository.get_by_id(user_scope_id)
        if not user_scope:
            raise EntityNotFoundError("UserScope", user_scope_id)

        # Agregar campo de auditoría
        if updated_by:
            data["updated_by"] = updated_by

        return self.repository.update(user_scope_id, data)

    def delete_user_scope(
        self,
        user_scope_id: int,
        deleted_by: Optional[int] = None
    ) -> UserScope:
        """
        Elimina (soft delete) un UserScope.

        Args:
            user_scope_id: ID del UserScope a eliminar
            deleted_by: ID del usuario que elimina

        Returns:
            UserScope eliminado

        Raises:
            EntityNotFoundError: Si el UserScope no existe
        """
        user_scope = self.repository.get_by_id(user_scope_id)
        if not user_scope:
            raise EntityNotFoundError("UserScope", user_scope_id)

        return self.repository.soft_delete(user_scope_id, deleted_by)

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
        user_scope = self.repository.get_by_id(user_scope_id)
        if not user_scope:
            raise EntityNotFoundError("UserScope", user_scope_id)
        return user_scope

    def get_scopes_by_user(self, user_id: int, active_only: bool = True) -> List[UserScope]:
        """
        Obtiene todos los scopes de un usuario.

        Args:
            user_id: ID del usuario
            active_only: Si True, solo retorna scopes activos

        Returns:
            Lista de UserScopes
        """
        return self.repository.get_by_user_id(user_id, active_only)

    def get_all_user_scopes(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[UserScope]:
        """
        Obtiene todos los UserScopes con paginación.

        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            active_only: Si True, solo retorna scopes activos

        Returns:
            Lista de UserScopes
        """
        return self.repository.get_all(skip, limit, active_only)
