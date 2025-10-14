"""
Schemas: Position

Schemas Pydantic para validacion de Position.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class HierarchyLevelEnum(str, Enum):
    """Enum para niveles jerarquicos de puestos."""
    C_LEVEL = "C-Level"
    DIRECTOR = "Director"
    MANAGER = "Manager"
    COORDINATOR = "Coordinator"
    SPECIALIST = "Specialist"
    SENIOR = "Senior"
    INTERMEDIATE = "Intermediate"
    JUNIOR = "Junior"
    TRAINEE = "Trainee"


# Mapeo de pesos por defecto para cada nivel jerarquico
HIERARCHY_WEIGHTS_DEFAULT = {
    HierarchyLevelEnum.C_LEVEL: 5,
    HierarchyLevelEnum.DIRECTOR: 15,
    HierarchyLevelEnum.MANAGER: 30,
    HierarchyLevelEnum.COORDINATOR: 45,
    HierarchyLevelEnum.SPECIALIST: 55,
    HierarchyLevelEnum.SENIOR: 65,
    HierarchyLevelEnum.INTERMEDIATE: 75,
    HierarchyLevelEnum.JUNIOR: 85,
    HierarchyLevelEnum.TRAINEE: 95,
}


class PositionBase(BaseModel):
    """Schema base de Position con campos comunes."""
    company_id: int = Field(..., description="ID de la empresa")
    title: str = Field(..., min_length=1, max_length=200, description="Titulo del puesto")
    level: Optional[str] = Field(None, max_length=50, description="Nivel legacy (junior, senior, etc.)")
    hierarchy_level: HierarchyLevelEnum = Field(..., description="Nivel jerarquico general")
    hierarchy_weight: Optional[int] = Field(None, ge=0, le=100, description="Peso para ordenamiento (0=mas alto, 100=mas bajo). Si no se provee, se asigna automaticamente segun hierarchy_level")
    description: Optional[str] = Field(None, description="Descripcion del puesto")


class PositionCreate(PositionBase):
    """Schema para crear Position (POST)."""
    pass


class PositionUpdate(BaseModel):
    """Schema para actualizar Position (PUT/PATCH)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    level: Optional[str] = Field(None, max_length=50)
    hierarchy_level: Optional[HierarchyLevelEnum] = None
    hierarchy_weight: Optional[int] = Field(None, ge=0, le=100)
    description: Optional[str] = None


class PositionResponse(PositionBase):
    """Schema de respuesta de Position (incluye campos de auditoria)."""
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


class PositionListResponse(BaseModel):
    """Schema de respuesta para lista paginada de Positions."""
    items: List[PositionResponse]
    total: int
    page: int
    per_page: int
    pages: int

    model_config = ConfigDict(from_attributes=True)