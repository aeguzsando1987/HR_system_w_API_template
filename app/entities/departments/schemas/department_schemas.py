"""
Schemas: Department

Schemas Pydantic para validacion de Department.
"""
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime


class DepartmentBase(BaseModel):
    """Schema base de Department con campos comunes."""
    company_id: int = Field(..., description="ID de la empresa")
    parent_id: Optional[int] = Field(None, description="ID del departamento padre (NULL para raiz)")
    code: str = Field(..., min_length=1, max_length=50, description="Codigo del departamento")
    name: str = Field(..., min_length=1, max_length=200, description="Nombre del departamento")
    description: Optional[str] = Field(None, description="Descripcion del departamento")
    is_corporate: bool = Field(False, description="Si es departamento corporativo (sin sucursal)")
    branch_id: Optional[int] = Field(None, description="ID de la sucursal (NULL para corporativos)")

    @validator('branch_id')
    def validate_branch_corporate(cls, v, values):
        """
        Valida logica corporativa:
        - is_corporate=True → branch_id debe ser NULL
        - is_corporate=False → branch_id debe tener valor
        """
        is_corporate = values.get('is_corporate', False)
        if is_corporate and v is not None:
            raise ValueError("Departamentos corporativos no pueden tener branch_id asignado")
        if not is_corporate and v is None:
            raise ValueError("Departamentos de sucursal deben tener branch_id asignado")
        return v


class DepartmentCreate(DepartmentBase):
    """Schema para crear Department (POST)."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema para actualizar Department (PUT/PATCH)."""
    branch_id: Optional[int] = None
    parent_id: Optional[int] = None
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_corporate: Optional[bool] = None

    @validator('branch_id')
    def validate_branch_corporate(cls, v, values):
        """Valida logica corporativa en actualizacion."""
        is_corporate = values.get('is_corporate')
        if is_corporate is not None:
            if is_corporate and v is not None:
                raise ValueError("Departamentos corporativos no pueden tener branch_id asignado")
            if not is_corporate and v is None:
                raise ValueError("Departamentos de sucursal deben tener branch_id asignado")
        return v


class DepartmentResponse(DepartmentBase):
    """Schema de respuesta de Department (incluye campos de auditoria)."""
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


class DepartmentListResponse(BaseModel):
    """Schema de respuesta para lista paginada de Departments."""
    items: List[DepartmentResponse]
    total: int
    page: int
    per_page: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class DepartmentTreeNode(BaseModel):
    """Schema para nodo del arbol jerarquico de Department."""
    id: int
    code: str
    name: str
    company_id: int
    branch_id: Optional[int]
    parent_id: Optional[int]
    is_corporate: bool
    is_active: bool
    level: int
    children: List['DepartmentTreeNode'] = []

    model_config = ConfigDict(from_attributes=True)


# Necesario para self-referencing
DepartmentTreeNode.model_rebuild()