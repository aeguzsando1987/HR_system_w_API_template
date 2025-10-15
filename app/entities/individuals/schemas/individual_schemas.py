"""
Individual Schemas - Validación y serialización con Pydantic
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date, datetime
from app.entities.individuals.models.individual import DocumentTypeEnum, GenderEnum, MaritalStatusEnum


class IndividualBase(BaseModel):
    """Schema base para Individual"""
    first_name: str = Field(..., max_length=100, description="Nombre(s)")
    last_name: str = Field(..., max_length=100, description="Apellido(s)")
    email: EmailStr = Field(..., description="Email único")
    phone: str = Field(..., max_length=20, description="Teléfono principal (requerido)")
    mobile: Optional[str] = Field(None, max_length=20, description="Teléfono celular")

    document_type: Optional[DocumentTypeEnum] = Field(None, description="Tipo de documento")
    document_number: Optional[str] = Field(None, max_length=50, description="Número de documento")
    curp: Optional[str] = Field(None, max_length=18, description="CURP (18 caracteres)")

    birth_date: Optional[date] = Field(None, description="Fecha de nacimiento")
    gender: Optional[GenderEnum] = Field(None, description="Género")
    address: Optional[str] = Field(None, max_length=500, description="Dirección completa")
    photo_url: Optional[str] = Field(None, max_length=500, description="URL de foto de perfil")

    country_id: Optional[int] = Field(None, description="ID del país")
    state_id: Optional[int] = Field(None, description="ID del estado/provincia")

    # Campos recomendados
    payroll_number: Optional[str] = Field(None, max_length=50, description="Número de nómina")
    marital_status: Optional[MaritalStatusEnum] = Field(None, description="Estado civil")
    emergency_contact_name: Optional[str] = Field(None, max_length=200, description="Nombre del contacto de emergencia")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Teléfono del contacto de emergencia")
    emergency_contact_relation: Optional[str] = Field(None, max_length=50, description="Relación con el contacto de emergencia")

    @validator('curp')
    def validate_curp_format(cls, v):
        """Validar formato CURP (18 caracteres)"""
        if v and len(v) != 18:
            raise ValueError('CURP debe tener exactamente 18 caracteres')
        return v.upper() if v else v

    @validator('birth_date')
    def validate_birth_date(cls, v):
        """Validar que fecha de nacimiento no sea futura y edad mínima 16 años"""
        if v:
            today = date.today()
            if v > today:
                raise ValueError('La fecha de nacimiento no puede ser futura')

            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 16:
                raise ValueError('La edad mínima es 16 años')

        return v

    @validator('phone', 'mobile', 'emergency_contact_phone')
    def validate_phone_format(cls, v):
        """Validación básica de formato telefónico"""
        if v:
            # Eliminar espacios y caracteres comunes
            cleaned = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
            if not cleaned.isdigit():
                raise ValueError('El teléfono debe contener solo números, espacios, guiones o paréntesis')
            if len(cleaned) < 7 or len(cleaned) > 15:
                raise ValueError('El teléfono debe tener entre 7 y 15 dígitos')
        return v

    class Config:
        from_attributes = True


class IndividualCreate(IndividualBase):
    """Schema para crear Individual (sin user)"""
    pass


class IndividualCreateWithUser(BaseModel):
    """
    Schema para crear Individual + User en una transacción atómica.
    Este es el endpoint principal para registrar nuevas personas con acceso al sistema.
    """
    # Individual fields (REQUIRED)
    first_name: str = Field(..., max_length=100, description="Nombre(s)")
    last_name: str = Field(..., max_length=100, description="Apellido(s)")
    email: EmailStr = Field(..., description="Email del Individual")
    phone: str = Field(..., max_length=20, description="Teléfono principal")

    # Individual fields (OPTIONAL)
    mobile: Optional[str] = Field(None, max_length=20, description="Teléfono celular")
    document_type: Optional[DocumentTypeEnum] = Field(None, description="Tipo de documento")
    document_number: Optional[str] = Field(None, max_length=50, description="Número de documento")
    curp: Optional[str] = Field(None, max_length=18, description="CURP (18 caracteres)")
    birth_date: Optional[date] = Field(None, description="Fecha de nacimiento")
    gender: Optional[GenderEnum] = Field(None, description="Género")
    address: Optional[str] = Field(None, max_length=500, description="Dirección completa")
    photo_url: Optional[str] = Field(None, max_length=500, description="URL de foto")
    country_id: Optional[int] = Field(None, description="ID del país")
    state_id: Optional[int] = Field(None, description="ID del estado")
    payroll_number: Optional[str] = Field(None, max_length=50, description="Número de nómina")
    marital_status: Optional[MaritalStatusEnum] = Field(None, description="Estado civil")
    emergency_contact_name: Optional[str] = Field(None, max_length=200, description="Contacto de emergencia")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Teléfono de emergencia")
    emergency_contact_relation: Optional[str] = Field(None, max_length=50, description="Relación")

    # User fields (REQUIRED for with-user)
    user_email: EmailStr = Field(..., description="Email para la cuenta de usuario (puede ser diferente del Individual.email)")
    user_password: str = Field(..., min_length=8, description="Contraseña del usuario (mínimo 8 caracteres)")
    user_role: int = Field(..., ge=1, le=4, description="Rol: 1=Admin, 2=Manager, 3=Collaborator, 4=Reader")

    @validator('curp')
    def validate_curp_format(cls, v):
        """Validar formato CURP"""
        if v and len(v) != 18:
            raise ValueError('CURP debe tener exactamente 18 caracteres')
        return v.upper() if v else v

    @validator('birth_date')
    def validate_birth_date(cls, v):
        """Validar fecha de nacimiento"""
        if v:
            today = date.today()
            if v > today:
                raise ValueError('La fecha de nacimiento no puede ser futura')
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 16:
                raise ValueError('La edad mínima es 16 años')
        return v

    @validator('phone', 'mobile', 'emergency_contact_phone')
    def validate_phone_format(cls, v):
        """Validación de formato telefónico"""
        if v:
            cleaned = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
            if not cleaned.isdigit():
                raise ValueError('El teléfono debe contener solo números y caracteres de formato')
            if len(cleaned) < 7 or len(cleaned) > 15:
                raise ValueError('El teléfono debe tener entre 7 y 15 dígitos')
        return v

    class Config:
        from_attributes = True


class IndividualUpdate(BaseModel):
    """Schema para actualizar Individual (todos los campos opcionales)"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)

    document_type: Optional[DocumentTypeEnum] = None
    document_number: Optional[str] = Field(None, max_length=50)
    curp: Optional[str] = Field(None, max_length=18)

    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = Field(None, max_length=500)

    country_id: Optional[int] = None
    state_id: Optional[int] = None

    payroll_number: Optional[str] = Field(None, max_length=50)
    marital_status: Optional[MaritalStatusEnum] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relation: Optional[str] = Field(None, max_length=50)

    @validator('curp')
    def validate_curp_format(cls, v):
        if v and len(v) != 18:
            raise ValueError('CURP debe tener exactamente 18 caracteres')
        return v.upper() if v else v

    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v:
            today = date.today()
            if v > today:
                raise ValueError('La fecha de nacimiento no puede ser futura')
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 16:
                raise ValueError('La edad mínima es 16 años')
        return v

    class Config:
        from_attributes = True


class IndividualResponse(IndividualBase):
    """Schema para respuestas de Individual"""
    id: int
    user_id: Optional[int] = None
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True