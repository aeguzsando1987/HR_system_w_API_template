"""
Modelo UserScope

Define los scopes (ámbitos de acceso) que puede tener un usuario.
Permite control granular de permisos a nivel de BusinessGroup, Company, Branch o Department.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from app.entities.user_scopes.schemas.enums import ScopeTypeEnum


class UserScope(Base):
    """
    UserScope: Define el ámbito de acceso de un usuario en la organización.

    Un usuario puede tener múltiples scopes para diferentes niveles organizacionales.
    Por ejemplo, un Gerente puede tener acceso a 2 Companies diferentes.

    Reglas de negocio:
    - Admin (role=1): Puede tener scope GLOBAL o cualquier otro (opcional)
    - Gerente (role=2): Debe tener scope BUSINESS_GROUP, COMPANY o BRANCH
    - Gestor (role=3): Debe tener scope DEPARTMENT
    - Colaborador (role=4): No puede tener scope (acceso solo a su propio perfil)
    - Guest (role=5): No puede tener scope
    """

    __tablename__ = "user_scopes"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Scope Type
    scope_type = Column(SQLEnum(ScopeTypeEnum), nullable=False, index=True)

    # Scope Entity IDs (solo uno debe estar poblado según scope_type)
    business_group_id = Column(Integer, ForeignKey("business_groups.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id = Column(Integer, nullable=True, index=True)  # FK pendiente (Company no existe aún)
    branch_id = Column(Integer, nullable=True, index=True)   # FK pendiente (Branch no existe aún)
    department_id = Column(Integer, nullable=True, index=True)  # FK pendiente (Department no existe aún)

    # Audit Fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_scopes")
    business_group = relationship("BusinessGroup", foreign_keys=[business_group_id])

    # Audit relationships
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    deleter = relationship("User", foreign_keys=[deleted_by])

    def __repr__(self):
        return f"<UserScope(id={self.id}, user_id={self.user_id}, scope_type={self.scope_type})>"
