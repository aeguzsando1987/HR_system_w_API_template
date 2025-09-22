from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Configuración PostgreSQL
DATABASE_URL = "postgresql://postgres:root@localhost:5432/pt_test"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo User
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)

    # Sistema de roles (1=Admin, 2=Gerente, 3=Colaborador, 4=Lector, 5=Guest)
    role = Column(Integer, default=4)

    # Gestión de estado
    is_active = Column(Boolean, default=True)  # Para activar/desactivar
    is_deleted = Column(Boolean, default=False)  # Para soft delete

    # Campos de auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relación con entities (opcional) - especificando foreign_keys para evitar ambigüedad
    entities = relationship("ExampleEntity", back_populates="user", foreign_keys="ExampleEntity.user_id")

    # Relación de auditoría (usuario que actualizó)
    updated_by_user = relationship("User", remote_side=[id], foreign_keys=[updated_by])

# Modelo ExampleEntity (plantilla para replicar)
class ExampleEntity(Base):
    __tablename__ = "example_entities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # FK opcional
    code = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="active")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con User (opcional) - especificando foreign_keys para claridad
    user = relationship("User", back_populates="entities", foreign_keys=[user_id])

# Función para crear tablas
def create_tables():
    Base.metadata.create_all(bind=engine)

# Función para obtener sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()