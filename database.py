from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Importar configuración híbrida
from app.config import settings

# Configuración de la base de datos usando el sistema híbrido
DATABASE_URL = settings.get_database_url()

# Crear engine con configuración del pool desde settings
engine = create_engine(
    DATABASE_URL,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    echo=settings.db_echo_sql,  # Mostrar queries SQL en logs si está habilitado
    connect_args={"client_encoding": "utf8"}  # Fix para Windows + psycopg2
)

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
    deleted_at = Column(DateTime, nullable=True)  # Timestamp de eliminación lógica
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relación con entities (opcional) - especificando foreign_keys para evitar ambigüedad
    entities = relationship("ExampleEntity", back_populates="user", foreign_keys="ExampleEntity.user_id")

    # NOTA: La relación con Person de la nueva arquitectura se define solo desde Person.user
    # para evitar conflictos con el modelo Person antiguo en modules/persons/models.py
    # La relación unidireccional es suficiente para nuestros casos de uso

    # Relación con Individual (1:1) - Definida desde ambos lados para uso bidireccional
    individual = relationship("Individual", back_populates="user", uselist=False, foreign_keys="Individual.user_id")

    # Relación de auditoría (usuario que actualizó)
    updated_by_user = relationship("User", remote_side=[id], foreign_keys=[updated_by])
    # Relación de auditoría (usuario que eliminó)
    deleted_by_user = relationship("User", remote_side=[id], foreign_keys=[deleted_by])

    # Relación con UserScope (scopes asignados al usuario)
    user_scopes = relationship("UserScope", back_populates="user", foreign_keys="UserScope.user_id")

    # Relación con UserPermission (permisos granulares por endpoint)
    permissions = relationship("UserPermission", back_populates="user", foreign_keys="UserPermission.user_id")

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