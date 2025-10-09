"""
Schemas: BusinessGroup

Schemas Pydantic v2 para validación de datos de entrada/salida.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


class BusinessGroupBase(BaseModel):
    """Schema base para BusinessGroup."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre del grupo empresarial"
    )
    legal_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Razón social completa"
    )
    tax_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Identificación fiscal (RFC/RUT/NIT)"
    )
    description: Optional[str] = Field(
        None,
        description="Descripción del grupo empresarial"
    )


class BusinessGroupCreate(BusinessGroupBase):
    """Schema para crear un BusinessGroup (POST)."""
    pass


class BusinessGroupUpdate(BaseModel):
    """Schema para actualizar un BusinessGroup (PUT/PATCH)."""
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        description="Nombre del grupo empresarial"
    )
    legal_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Razón social completa"
    )
    tax_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Identificación fiscal (RFC/RUT/NIT)"
    )
    description: Optional[str] = Field(
        None,
        description="Descripción del grupo empresarial"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Estado activo/inactivo"
    )


class BusinessGroupResponse(BusinessGroupBase):
    """Schema para respuesta de BusinessGroup (GET)."""
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


class BusinessGroupListResponse(BaseModel):
    """Schema para lista paginada de BusinessGroups."""
    items: List[BusinessGroupResponse]
    total: int
    page: int
    per_page: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
