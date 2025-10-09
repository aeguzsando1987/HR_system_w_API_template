"""
Modelo: Company (Empresa)

Representa una empresa dentro de un BusinessGroup.
Una Company puede tener múltiples Branches, Departments, Positions y Employees.

Relaciones:
- N Company → 1 BusinessGroup
- 1 Company → N Branch
- 1 Company → N Department
- 1 Company → N Position
- 1 Company → N Employee
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Company(Base):
    """Modelo de Company - Empresa dentro de un grupo empresarial."""

    __tablename__ = "companies"

    # ==================== PRIMARY KEY ====================
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="ID único de la empresa"
    )

    # ==================== FOREIGN KEYS ====================
    business_group_id = Column(
        Integer,
        ForeignKey("business_groups.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID del BusinessGroup al que pertenece la empresa"
    )

    # ==================== BUSINESS FIELDS ====================
    code = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Código único de la empresa"
    )

    name = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Nombre comercial de la empresa"
    )

    legal_name = Column(
        String(200),
        nullable=True,
        comment="Razón social completa"
    )

    tax_id = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="Identificación fiscal (RFC/RUT/NIT) - único globalmente"
    )

    industry = Column(
        String(100),
        nullable=True,
        comment="Industria o sector (Tecnología, Retail, Servicios, etc.)"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Descripción de la empresa"
    )

    # ==================== AUDIT FIELDS ====================
    # Gestión de estado
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Estado activo/inactivo (soft delete)"
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft delete flag"
    )

    # Timestamps automáticos
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha y hora de creación del registro"
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Fecha y hora de última actualización"
    )

    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Fecha y hora de eliminación lógica (soft delete)"
    )

    # Usuario que realizó las acciones
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="Usuario que creó el registro"
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="Usuario que actualizó el registro por última vez"
    )

    deleted_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="Usuario que eliminó el registro (soft delete)"
    )

    # ==================== RELATIONSHIPS ====================
    # Relación con BusinessGroup (N → 1)
    business_group = relationship(
        "BusinessGroup",
        foreign_keys=[business_group_id]
    )

    # Relaciones de auditoría con Usuario
    creator = relationship(
        "User",
        foreign_keys=[created_by]
    )

    updater = relationship(
        "User",
        foreign_keys=[updated_by]
    )

    deleter = relationship(
        "User",
        foreign_keys=[deleted_by]
    )

    # Nota: Las relaciones con Branch, Department, Position, Employee
    # se definen desde esas entidades para evitar imports circulares

    def __repr__(self):
        return f"<Company(id={self.id}, code='{self.code}', name='{self.name}', business_group_id={self.business_group_id})>"

    def __str__(self):
        return f"{self.name} ({self.code})"