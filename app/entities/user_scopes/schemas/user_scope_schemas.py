"""
Schemas Pydantic para UserScope

Define los esquemas de validación y serialización para los UserScopes.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from app.entities.user_scopes.schemas.enums import ScopeTypeEnum


class UserScopeBase(BaseModel):
    """Schema base con campos comunes."""
    user_id: int = Field(..., description="ID del usuario al que pertenece este scope")
    scope_type: ScopeTypeEnum = Field(..., description="Tipo de scope (GLOBAL, BUSINESS_GROUP, etc.)")
    business_group_id: Optional[int] = Field(None, description="ID del BusinessGroup (si scope_type=BUSINESS_GROUP)")
    company_id: Optional[int] = Field(None, description="ID de la Company (si scope_type=COMPANY)")
    branch_id: Optional[int] = Field(None, description="ID del Branch (si scope_type=BRANCH)")
    department_id: Optional[int] = Field(None, description="ID del Department (si scope_type=DEPARTMENT)")


class UserScopeCreate(UserScopeBase):
    """
    Schema para crear un UserScope (POST).

    Validaciones:
    - Exactamente UNO de los IDs debe estar poblado según scope_type
    - GLOBAL: ningún ID debe estar poblado
    - BUSINESS_GROUP: solo business_group_id
    - COMPANY: solo company_id
    - BRANCH: solo branch_id
    - DEPARTMENT: solo department_id
    """
    pass


class UserScopeUpdate(BaseModel):
    """
    Schema para actualizar un UserScope (PUT/PATCH).

    Solo permite actualizar el estado activo y los IDs de scope.
    No permite cambiar user_id ni scope_type después de creado.
    """
    business_group_id: Optional[int] = None
    company_id: Optional[int] = None
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserScopeResponse(UserScopeBase):
    """Schema para respuesta de UserScope (GET)."""
    id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]
    deleted_by: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class UserScopeListResponse(BaseModel):
    """Schema para respuesta de lista de UserScopes."""
    total: int
    items: list[UserScopeResponse]

    model_config = ConfigDict(from_attributes=True)
