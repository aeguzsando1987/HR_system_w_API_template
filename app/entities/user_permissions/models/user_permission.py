"""
Modelo UserPermission

Define los permisos granulares por endpoint que puede tener un usuario.
Permite control específico de acciones (GET, POST, PUT, DELETE) por endpoint.

Sistema Híbrido de 3 Capas:
1. ROLE → Perfil general (Admin, Gerente, Colaborador)
2. SCOPE → Ámbito organizacional (GLOBAL, COMPANY, DEPARTMENT)
3. PERMISSION → Acciones específicas (GET /employees: true)

Validación Híbrida:
- Primero busca permiso ESPECÍFICO (POST /individuals/with-user)
- Si no existe, busca permiso BASE (POST /individuals)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class UserPermission(Base):
    """
    UserPermission: Define permisos granulares por endpoint para un usuario.

    Permite que un Admin configure desde app móvil qué endpoints y métodos HTTP
    puede acceder cada usuario (true/false).

    Ejemplo:
        Usuario: Ana (Gerente)
        Permissions:
          - GET /api/v1/employees → allowed=True
          - POST /api/v1/employees → allowed=True
          - DELETE /api/v1/employees → allowed=False

    Auto-Discovery:
        Los endpoints se auto-descubren desde FastAPI.
        NO requiere editar código al agregar nuevas entidades.

    Validación Híbrida:
        1. Busca permiso específico: POST /api/v1/individuals/with-user
        2. Si no existe, busca base: POST /api/v1/individuals
    """

    __tablename__ = "user_permissions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Permission Fields
    endpoint = Column(String(255), nullable=False, index=True)  # "/api/v1/employees" o "/api/v1/individuals/with-user"
    method = Column(String(10), nullable=False, index=True)     # GET, POST, PUT, DELETE, PATCH
    allowed = Column(Boolean, default=False, nullable=False)    # true/false

    # Audit Fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Constraints
    __table_args__ = (
        # Un usuario no puede tener permisos duplicados para el mismo endpoint+method
        UniqueConstraint('user_id', 'endpoint', 'method', name='uq_user_endpoint_method'),
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="permissions")

    # Audit relationships
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    deleter = relationship("User", foreign_keys=[deleted_by])

    def __repr__(self):
        return f"<UserPermission(id={self.id}, user_id={self.user_id}, {self.method} {self.endpoint}: {self.allowed})>"
