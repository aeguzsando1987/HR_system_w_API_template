"""
Schemas: Company

Schemas Pydantic v2 para validación de datos de entrada/salida de Company.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


class CompanyBase(BaseModel):
    """Schema base para Company."""
    business_group_id: int = Field(
        ...,
        gt=0,
        description="ID del BusinessGroup al que pertenece"
    )
    code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código único de la empresa"
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre comercial de la empresa"
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
    industry: Optional[str] = Field(
        None,
        max_length=100,
        description="Industria o sector"
    )
    description: Optional[str] = Field(
        None,
        description="Descripción de la empresa"
    )


class CompanyCreate(CompanyBase):
    """Schema para crear una Company (POST)."""
    pass


class CompanyUpdate(BaseModel):
    """Schema para actualizar una Company (PUT/PATCH)."""
    business_group_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID del BusinessGroup"
    )
    code: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Código único de la empresa"
    )
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        description="Nombre comercial"
    )
    legal_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Razón social completa"
    )
    tax_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Identificación fiscal"
    )
    industry: Optional[str] = Field(
        None,
        max_length=100,
        description="Industria o sector"
    )
    description: Optional[str] = Field(
        None,
        description="Descripción"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Estado activo/inactivo"
    )


class CompanyResponse(CompanyBase):
    """Schema para respuesta de Company (GET)."""
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


class CompanyListResponse(BaseModel):
    """Schema para lista paginada de Companies."""
    items: List[CompanyResponse]
    total: int
    page: int
    per_page: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class CompanySearchResponse(BaseModel):
    """Schema para búsqueda de Companies."""
    items: List[CompanyResponse]
    total: int
    query: str

    model_config = ConfigDict(from_attributes=True)
