"""
Individual Model - Personas físicas en el sistema
"""
import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, CheckConstraint, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import Boolean, DateTime


class DocumentTypeEnum(str, enum.Enum):
    """Tipos de documento de identidad"""
    INE = "INE"
    PASSPORT = "Passport"
    CEDULA = "Cédula"
    DNI = "DNI"
    RUT = "RUT"
    CC = "CC"
    CE = "CE"
    TI = "TI"
    RFC = "RFC"
    NSS = "NSS"
    OTHER = "Other"


class GenderEnum(str, enum.Enum):
    """Género"""
    MALE = "M"
    FEMALE = "F"
    OTHER = "Other"
    PREFER_NOT_SAY = "Prefer not to say"


class MaritalStatusEnum(str, enum.Enum):
    """Estado civil"""
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    SEPARATED = "Separated"
    DOMESTIC_PARTNERSHIP = "Domestic Partnership"


class Individual(Base):
    """
    Modelo para Individuals (Personas Físicas).

    Representa personas físicas que pueden o no ser usuarios del sistema.
    Un Individual puede tener un User asociado (1:1) y múltiples Employees.
    """
    __tablename__ = "individuals"

    # ==================== IDENTIFICACIÓN PERSONAL ====================
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False)  # REQUERIDO
    mobile = Column(String(20), nullable=True)

    # ==================== DOCUMENTOS DE IDENTIDAD ====================
    document_type = Column(String(50), nullable=True)  # OPCIONAL
    document_number = Column(String(50), nullable=True, index=True)  # OPCIONAL, ÚNICO
    curp = Column(String(18), nullable=True, unique=True, index=True)  # OPCIONAL, ÚNICO (México)

    # ==================== INFORMACIÓN ADICIONAL ====================
    birth_date = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    photo_url = Column(String(500), nullable=True)

    # ==================== FOREIGN KEYS ====================
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True, index=True)

    # ==================== CAMPOS RECOMENDADOS ====================
    # Campo 1: Identificador de nómina
    payroll_number = Column(String(50), nullable=True, unique=True, index=True)

    # Campo 2: Estado civil
    marital_status = Column(String(20), nullable=True)

    # Campos 3-5: Contacto de emergencia
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)


    # Campos de auditoría
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # ==================== RELACIONES ====================
    country = relationship("Country", back_populates="individuals", foreign_keys=[country_id])
    state = relationship("State", back_populates="individuals", foreign_keys=[state_id])
    user = relationship("User", back_populates="individual", uselist=False, foreign_keys=[user_id])
    employees = relationship("Employee", back_populates="individual", uselist=False, foreign_keys="Employee.individual_id")

    # ==================== CONSTRAINTS ====================
    __table_args__ = (
        # Email formato válido
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", # aplicamos regex
            name='ck_individual_email_format'
        ),

        # Birth date no puede ser futura
        CheckConstraint(
            'birth_date IS NULL OR birth_date <= CURRENT_DATE',
            name='ck_individual_birth_date'
        ),

        # CURP formato válido (18 caracteres)
        CheckConstraint(
            "curp IS NULL OR LENGTH(curp) = 18",
            name='ck_individual_curp_length'
        ),

        # Phone no vacío
        CheckConstraint(
            "LENGTH(TRIM(phone)) > 0",
            name='ck_individual_phone_not_empty'
        ),

        # Document number único (si se provee)
        UniqueConstraint('document_number', name='uq_individual_document'),

        # Payroll number único (si se provee)
        UniqueConstraint('payroll_number', name='uq_individual_payroll'),
    )

    def __repr__(self):
        return f"<Individual(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"

    @property
    def full_name(self):
        """Retorna el nombre completo"""
        return f"{self.first_name} {self.last_name}"