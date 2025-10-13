"""
Model: Department

Departamentos organizacionales con jerarquia auto-referenciada.
Pueden ser corporativos (sin branch) o de sucursal especifica.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Department(Base):
    """Modelo de departamentos organizacionales."""

    __tablename__ = "departments"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True)  # NULL para corporativos
    parent_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True, index=True)  # Self-referencing

    # Business Fields
    code = Column(String(50), nullable=False, index=True)  # Unico por empresa
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_corporate = Column(Boolean, default=False, nullable=False, index=True)  # True = aplica a toda la empresa

    # Audit Fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    company = relationship("Company", back_populates="departments", foreign_keys=[company_id])
    branch = relationship("Branch", back_populates="departments", foreign_keys=[branch_id])

    # Self-referencing: parent and children
    parent = relationship("Department", remote_side=[id], back_populates="children", foreign_keys=[parent_id])
    children = relationship("Department", back_populates="parent", foreign_keys=[parent_id])

    # Constraints
    __table_args__ = (
        # Codigo unico por empresa
        UniqueConstraint('company_id', 'code', name='uq_company_department_code'),

        # No puede ser su propio padre
        CheckConstraint('id != parent_id', name='check_no_self_parent'),

        # Logica corporativa: is_corporate=true → branch_id=NULL, is_corporate=false → branch_id NOT NULL
        CheckConstraint(
            '(is_corporate = false AND branch_id IS NOT NULL) OR '
            '(is_corporate = true AND branch_id IS NULL)',
            name='check_corporate_branch_logic'
        ),
    )

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}', company_id={self.company_id}, parent_id={self.parent_id})>"
