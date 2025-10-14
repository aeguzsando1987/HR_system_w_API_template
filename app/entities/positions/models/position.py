"""
Model: Position

Catálogo de puestos de trabajo por empresa.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class HierarchyLevelEnum(str, enum.Enum):
    """Enum para niveles jerárquicos de puestos."""
    C_LEVEL = "C-Level"
    DIRECTOR = "Director"
    MANAGER = "Manager"
    COORDINATOR = "Coordinator"
    SPECIALIST = "Specialist"
    SENIOR = "Senior"
    INTERMEDIATE = "Intermediate"
    JUNIOR = "Junior"
    TRAINEE = "Trainee"


class Position(Base):
    """
    Position: Puesto/Cargo en una empresa.

    Representa un puesto de trabajo (ej: "Gerente de Ventas", "Desarrollador Senior").
    La relación con Department se establece a nivel de Employee.
    """
    __tablename__ = "positions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Campos principales
    title = Column(String(200), nullable=False, comment="Título del puesto")
    level = Column(String(50), nullable=True, comment="Nivel legacy (junior, senior, etc.)")
    hierarchy_level = Column(
        SQLEnum(HierarchyLevelEnum),
        nullable=False,
        comment="Nivel jerárquico general para categorización"
    )
    hierarchy_weight = Column(
        Integer,
        nullable=False,
        default=50,
        comment="Peso para ordenamiento en organigramas (0=más alto, 100=más bajo)"
    )
    description = Column(Text, nullable=True, comment="Descripción del puesto")

    # Gestión de estado
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Auditoría
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relaciones
    company = relationship("Company", back_populates="positions", foreign_keys=[company_id])

    # Relación con Employee (pendiente implementación)
    # employees = relationship("Employee", back_populates="position")

    # Relaciones de auditoría
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    deleter = relationship("User", foreign_keys=[deleted_by])

    def __repr__(self):
        return f"<Position(id={self.id}, title='{self.title}', hierarchy_level='{self.hierarchy_level}', weight={self.hierarchy_weight}, company_id={self.company_id})>"
