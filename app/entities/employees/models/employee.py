"""
Employee Model - Empleados del sistema HR
"""
import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import Boolean, DateTime


class EmploymentStatusEnum(str, enum.Enum):
    """Estado laboral del empleado"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    INCAPACIDAD = "incapacidad"
    EN_LIQUIDACION = "en_liquidacion"
    TERMINADO = "terminado"


class EmploymentTypeEnum(str, enum.Enum):
    """Tipo de contratación"""
    TIEMPO_COMPLETO = "tiempo_completo"
    TIEMPO_PARCIAL = "tiempo_parcial"
    CONTRATO = "contrato"
    BECARIO = "becario"


class Employee(Base):
    """
    Modelo para Employees (Empleados).

    Representa empleados en el sistema HR. Cada empleado DEBE tener un Individual asociado (1:1).
    Los datos personales (nombre, email, documentos) se acceden via employee.individual.*
    """
    __tablename__ = "employees"

    # ==================== RELACIONES / FOREIGN KEYS ====================
    individual_id = Column(Integer, ForeignKey("individuals.id"), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    business_group_id = Column(Integer, ForeignKey("business_groups.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True, index=True)
    supervisor_id = Column(Integer, ForeignKey("employees.id"), nullable=True, index=True)  # Auto-referencia

    # ==================== INFORMACIÓN LABORAL ====================
    employee_code = Column(String(50), nullable=False, index=True)  # Único por company
    hire_date = Column(Date, nullable=False)
    employment_status = Column(String(20), nullable=False, default='activo', index=True)
    employment_type = Column(String(20), nullable=True)
    base_salary = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(10), nullable=True, default='USD')

    # ==================== CAMPOS DE AUDITORÍA COMPLETA ====================
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # ==================== RELACIONES ====================
    individual = relationship("Individual", back_populates="employees", foreign_keys=[individual_id])
    user = relationship("User", foreign_keys=[user_id])
    business_group = relationship("BusinessGroup", back_populates="employees", foreign_keys=[business_group_id])
    company = relationship("Company", back_populates="employees", foreign_keys=[company_id])
    branch = relationship("Branch", back_populates="employees", foreign_keys=[branch_id])
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    position = relationship("Position", back_populates="employees", foreign_keys=[position_id])

    # Auto-referencia para jerarquía de supervisión
    supervisor = relationship("Employee", remote_side=[id], foreign_keys=[supervisor_id], back_populates="subordinates")
    subordinates = relationship("Employee", back_populates="supervisor", foreign_keys=[supervisor_id])

    # Relaciones de auditoría
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    deleter = relationship("User", foreign_keys=[deleted_by])

    # ==================== CONSTRAINTS ====================
    __table_args__ = (
        # employee_code único por company
        UniqueConstraint('company_id', 'employee_code', name='uq_employee_code_per_company'),

        # No auto-supervisión
        CheckConstraint('id != supervisor_id', name='check_no_self_supervision'),

        # hire_date no puede ser futura
        CheckConstraint('hire_date <= CURRENT_DATE', name='check_hire_date_not_future'),
    )

    def __repr__(self):
        return f"<Employee(id={self.id}, code='{self.employee_code}', individual_id={self.individual_id})>"

    @property
    def full_name(self):
        """Retorna el nombre completo del empleado via Individual"""
        return self.individual.full_name if self.individual else "N/A"

    @property
    def email(self):
        """Retorna el email del empleado via Individual"""
        return self.individual.email if self.individual else "N/A"
