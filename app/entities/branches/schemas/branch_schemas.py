"""
Schemas: Branch

Pydantic schemas para validación y serialización de Branch.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class BranchBase(BaseModel):
    """Schema base de Branch con campos comunes."""

    company_id: int = Field(..., description="ID de la empresa a la que pertenece")
    country_id: int = Field(..., description="ID del país")
    state_id: int = Field(..., description="ID del estado/provincia")
    code: str = Field(..., min_length=1, max_length=50, description="Código de la sucursal (único por empresa)")
    name: str = Field(..., min_length=1, max_length=200, description="Nombre de la sucursal")
    address: Optional[str] = Field(None, description="Dirección física")
    city: Optional[str] = Field(None, max_length=100, description="Ciudad")
    postal_code: Optional[str] = Field(None, max_length=20, description="Código postal")
    phone: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    email: Optional[str] = Field(None, max_length=100, description="Email de contacto")
    description: Optional[str] = Field(None, description="Descripción de la sucursal")


class BranchCreate(BranchBase):
    """Schema para crear Branch (POST)."""
    pass


class BranchUpdate(BaseModel):
    """Schema para actualizar Branch (PUT/PATCH)."""

    country_id: Optional[int] = Field(None, description="ID del país")
    state_id: Optional[int] = Field(None, description="ID del estado/provincia")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="Código de la sucursal")
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Nombre de la sucursal")
    address: Optional[str] = Field(None, description="Dirección física")
    city: Optional[str] = Field(None, max_length=100, description="Ciudad")
    postal_code: Optional[str] = Field(None, max_length=20, description="Código postal")
    phone: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    email: Optional[str] = Field(None, max_length=100, description="Email de contacto")
    description: Optional[str] = Field(None, description="Descripción de la sucursal")


class BranchResponse(BranchBase):
    """Schema de respuesta de Branch (incluye campos de auditoría)."""

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


class BranchListResponse(BaseModel):
    """Schema de respuesta para lista paginada de Branches."""

    items: list[BranchResponse]
    total: int
    page: int
    per_page: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
