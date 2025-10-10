"""
Model: Branch

Sucursales/oficinas de empresas.
Depende de Company, Country y State.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Branch(Base):
    """Modelo de sucursales/oficinas."""

    __tablename__ = "branches"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="RESTRICT"), nullable=False, index=True)
    state_id = Column(Integer, ForeignKey("states.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Business Fields
    code = Column(String(50), nullable=False, index=True)  # Código de sucursal (único por empresa)
    name = Column(String(200), nullable=False, index=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

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
    company = relationship("Company", back_populates="branches", foreign_keys=[company_id])
    country = relationship("Country", foreign_keys=[country_id])
    state = relationship("State", foreign_keys=[state_id])

    # Unique Constraint: code debe ser único por empresa
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_company_branch_code'),
    )

    def __repr__(self):
        return f"<Branch(id={self.id}, name='{self.name}', code='{self.code}', company_id={self.company_id})>"
