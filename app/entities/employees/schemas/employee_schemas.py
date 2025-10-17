"""
Employee Schemas - Pydantic models for validation
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ==================== ENUMS ====================
class EmploymentStatusEnum(str, Enum):
    """Estado laboral"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    INCAPACIDAD = "incapacidad"
    EN_LIQUIDACION = "en_liquidacion"
    TERMINADO = "terminado"


class EmploymentTypeEnum(str, Enum):
    """Tipo de contratación"""
    TIEMPO_COMPLETO = "tiempo_completo"
    TIEMPO_PARCIAL = "tiempo_parcial"
    CONTRATO = "contrato"
    BECARIO = "becario"


# ==================== BASE SCHEMA ====================
class EmployeeBase(BaseModel):
    """Schema base para Employee"""
    # Relaciones (solo IDs)
    business_group_id: int = Field(..., description="ID del grupo empresarial")
    company_id: int = Field(..., description="ID de la empresa")
    branch_id: Optional[int] = Field(None, description="ID de la sucursal (opcional)")
    department_id: Optional[int] = Field(None, description="ID del departamento (opcional)")
    position_id: Optional[int] = Field(None, description="ID del puesto (opcional)")
    supervisor_id: Optional[int] = Field(None, description="ID del supervisor (opcional)")

    # Información laboral
    employee_code: str = Field(..., max_length=50, description="Código del empleado (único por empresa)")
    hire_date: date = Field(..., description="Fecha de contratación")
    employment_status: EmploymentStatusEnum = Field(default=EmploymentStatusEnum.ACTIVO, description="Estado laboral")
    employment_type: Optional[EmploymentTypeEnum] = Field(None, description="Tipo de contratación")
    base_salary: Optional[Decimal] = Field(None, ge=0, description="Salario base")
    currency: Optional[str] = Field("USD", max_length=10, description="Moneda del salario")

    @validator('hire_date')
    def validate_hire_date(cls, v):
        if v > date.today():
            raise ValueError('hire_date no puede ser futura')
        return v

    class Config:
        from_attributes = True


# ==================== CREATE SCHEMA ====================
class EmployeeCreate(EmployeeBase):
    """
    Schema para crear Employee (con Individual existente).

    Requiere que el Individual ya exista en la base de datos.
    """
    individual_id: int = Field(..., description="ID del Individual (debe existir)")
    user_id: Optional[int] = Field(None, description="ID del User (opcional)")


# ==================== CREATE WITH USER SCHEMA ====================
class EmployeeCreateWithUser(EmployeeBase):
    """
    Schema para crear Employee + Individual + User en transacción atómica.

    Este es el endpoint principal para registro completo de empleados.
    Crea Individual, User (si se provee), y Employee en una sola transacción.
    """
    # ===== DATOS DE INDIVIDUAL (REQUERIDOS) =====
    first_name: str = Field(..., max_length=100, description="Nombre(s)")
    last_name: str = Field(..., max_length=100, description="Apellido(s)")
    email: EmailStr = Field(..., description="Email del Individual")
    phone: str = Field(..., max_length=20, description="Teléfono (requerido)")

    # ===== DATOS DE INDIVIDUAL (OPCIONALES) =====
    mobile: Optional[str] = Field(None, max_length=20)
    document_type: Optional[str] = Field(None, max_length=50)
    document_number: Optional[str] = Field(None, max_length=50)
    curp: Optional[str] = Field(None, max_length=18)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = Field(None, max_length=500)
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    payroll_number: Optional[str] = Field(None, max_length=50)
    marital_status: Optional[str] = Field(None, max_length=20)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relation: Optional[str] = Field(None, max_length=50)

    # ===== DATOS DE USER (OPCIONALES - si se proveen, crea User) =====
    user_email: Optional[EmailStr] = Field(None, description="Email del usuario del sistema")
    user_password: Optional[str] = Field(None, min_length=8, description="Contraseña del usuario")
    user_role: Optional[int] = Field(None, ge=1, le=5, description="Rol del usuario (1-5)")

    @validator('curp')
    def validate_curp_format(cls, v):
        if v and len(v) != 18:
            raise ValueError('CURP debe tener exactamente 18 caracteres')
        return v.upper() if v else v

    @validator('user_role')
    def validate_user_complete(cls, v, values):
        """Si se provee user_role o user_password, ambos son requeridos"""
        has_password = values.get('user_password')
        has_email = values.get('user_email')

        if v or has_password:
            if not has_email:
                raise ValueError('user_email es requerido cuando se provee user_password o user_role')
            if not has_password:
                raise ValueError('user_password es requerido cuando se provee user_email o user_role')
        return v


# ==================== UPDATE SCHEMA ====================
class EmployeeUpdate(BaseModel):
    """Schema para actualizar Employee (campos opcionales)"""
    # Relaciones
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    supervisor_id: Optional[int] = None

    # Información laboral
    employee_code: Optional[str] = Field(None, max_length=50)
    employment_status: Optional[EmploymentStatusEnum] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    base_salary: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)

    @validator('base_salary')
    def validate_salary(cls, v):
        if v is not None and v < 0:
            raise ValueError('base_salary no puede ser negativo')
        return v

    class Config:
        from_attributes = True


# ==================== RESPONSE SCHEMA ====================
class EmployeeResponse(BaseModel):
    """Schema de respuesta para Employee"""
    # IDs y relaciones
    id: int
    individual_id: int
    user_id: Optional[int]
    business_group_id: int
    company_id: int
    branch_id: Optional[int]
    department_id: Optional[int]
    position_id: Optional[int]
    supervisor_id: Optional[int]

    # Información laboral
    employee_code: str
    hire_date: date
    employment_status: str
    employment_type: Optional[str]
    base_salary: Optional[Decimal]
    currency: Optional[str]

    # Auditoría
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]
    deleted_by: Optional[int]

    class Config:
        from_attributes = True
