"""
Modelo: BusinessGroup (Grupo Empresarial/Holding)

Entidad raíz de la jerarquía organizacional.
Representa matrices o holdings que contienen múltiples empresas.

Relaciones:
- 1 BusinessGroup → N Company
- 1 BusinessGroup → N Employee (tracking global)
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class BusinessGroup(Base):
    """Modelo de Grupo Empresarial - Contenedor de múltiples empresas."""

    __tablename__ = "business_groups"

    # ==================== PRIMARY KEY ====================
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="ID único del grupo empresarial"
    )

    # ==================== BUSINESS FIELDS ====================
    name = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Nombre del grupo empresarial"
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
        comment="Identificación fiscal (RFC/RUT/NIT)"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Descripción del grupo empresarial"
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

    # Relaciones con entidades hijas
    companies = relationship("Company", back_populates="business_group", foreign_keys="Company.business_group_id")
    employees = relationship("Employee", back_populates="business_group", foreign_keys="Employee.business_group_id")

    def __repr__(self):
        return f"<BusinessGroup(id={self.id}, name='{self.name}', tax_id='{self.tax_id}')>"

    def __str__(self):
        return self.name
