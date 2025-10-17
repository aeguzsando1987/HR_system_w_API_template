"""
Employee Service - Business logic and validations for Employee entity
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.entities.employees.models.employee import Employee
from app.entities.employees.repositories.employee_repository import EmployeeRepository
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    BusinessRuleError,
    EntityAlreadyExistsError
)
from auth import hash_password


class EmployeeService:
    """Service layer for Employee with 13 critical business validations"""

    MAX_HIERARCHY_DEPTH = 10

    def __init__(self, db: Session):
        self.db = db
        self.repository = EmployeeRepository(db)

        # Repositorios de entidades relacionadas
        from app.entities.individuals.repositories.individual_repository import IndividualRepository
        from app.entities.individuals.services.individual_service import IndividualService
        from app.entities.business_groups.repositories.business_group_repository import BusinessGroupRepository
        from app.entities.companies.repositories.company_repository import CompanyRepository
        from app.entities.branches.repositories.branch_repository import BranchRepository
        from app.entities.departments.repositories.department_repository import DepartmentRepository
        from app.entities.positions.repositories.position_repository import PositionRepository
        from app.shared.base_repository import BaseRepository
        from database import User

        self.individual_repository = IndividualRepository(db)
        self.individual_service = IndividualService(db)
        self.business_group_repository = BusinessGroupRepository(db)
        self.company_repository = CompanyRepository(db)
        self.branch_repository = BranchRepository(db)
        self.department_repository = DepartmentRepository(db)
        self.position_repository = PositionRepository(db)
        self.user_repository = BaseRepository(User, db)

    # ==================== MÉTODOS PRINCIPALES ====================

    def create_employee(self, data: Dict[str, Any], created_by: Optional[int] = None) -> Employee:
        """
        Crea un Employee (requiere Individual existente).

        Validaciones aplicadas: Las 13 validaciones críticas.

        Args:
            data: Diccionario con datos del Employee
            created_by: ID del usuario que crea

        Returns:
            Employee creado

        Raises:
            EntityNotFoundError: Si alguna FK no existe
            BusinessRuleError: Si alguna validación de negocio falla
            EntityAlreadyExistsError: Si employee_code ya existe en la empresa
        """
        # Aplicar validaciones
        self._validate_all(data)

        # Agregar auditoría
        if created_by:
            data['created_by'] = created_by

        # Crear Employee
        employee = Employee(**data)
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

        return employee

    def create_employee_with_user(self, data: Dict[str, Any], created_by: Optional[int] = None) -> Employee:
        """
        Crea Employee + Individual + User (opcional) en transacción atómica.

        Este endpoint reutiliza IndividualService.create_individual_with_user()
        para crear Individual + User, luego crea el Employee vinculado.

        Args:
            data: Diccionario con datos de Individual, User (opcional), y Employee
            created_by: ID del usuario que crea

        Returns:
            Employee creado

        Raises:
            EntityNotFoundError: Si alguna FK no existe
            BusinessRuleError: Si alguna validación falla
            EntityAlreadyExistsError: Si emails/códigos ya existen
        """
        try:
            # 1. Separar datos de Individual/User vs Employee
            individual_data = {}
            employee_data = {}

            # Campos de Individual
            individual_fields = [
                'first_name', 'last_name', 'email', 'phone', 'mobile',
                'document_type', 'document_number', 'curp', 'birth_date', 'gender',
                'address', 'photo_url', 'country_id', 'state_id',
                'payroll_number', 'marital_status',
                'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation'
            ]

            # Campos de User (opcionales)
            user_fields = ['user_email', 'user_password', 'user_role']

            # Campos de Employee
            employee_fields = [
                'business_group_id', 'company_id', 'branch_id', 'department_id',
                'position_id', 'supervisor_id', 'employee_code', 'hire_date',
                'employment_status', 'employment_type', 'base_salary', 'currency'
            ]

            # Separar datos
            for key, value in data.items():
                if key in individual_fields or key in user_fields:
                    individual_data[key] = value
                elif key in employee_fields:
                    employee_data[key] = value

            # 2. Validar datos de Employee ANTES de crear Individual
            # (para fallar rápido si hay errores)
            self._validate_all(employee_data, skip_individual_check=True)

            # 3. Crear Individual + User (si se proveen datos de user)
            has_user_data = any(k in data for k in user_fields)

            if has_user_data:
                # Usa el servicio de Individual para crear con User
                individual = self.individual_service.create_individual_with_user(
                    individual_data,
                    created_by
                )
            else:
                # Crea solo Individual
                individual = self.individual_service.create_individual(
                    individual_data,
                    created_by
                )

            # 4. Crear Employee vinculado al Individual
            employee_data['individual_id'] = individual.id

            # Si el Individual tiene user_id, lo propagamos al Employee
            if individual.user_id:
                employee_data['user_id'] = individual.user_id

            if created_by:
                employee_data['created_by'] = created_by

            employee = Employee(**employee_data)
            self.db.add(employee)

            # 5. Commit de toda la transacción
            self.db.commit()
            self.db.refresh(employee)

            return employee

        except Exception as e:
            self.db.rollback()
            raise e

    def update_employee(self, employee_id: int, data: Dict[str, Any], updated_by: Optional[int] = None) -> Employee:
        """
        Actualiza un Employee existente.

        Args:
            employee_id: ID del Employee
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            Employee actualizado

        Raises:
            EntityNotFoundError: Si el Employee no existe
            BusinessRuleError: Si alguna validación falla
        """
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise EntityNotFoundError("Employee", employee_id)

        # Aplicar validaciones (pasando employee_id para validación circular)
        self._validate_all(data, employee_id=employee_id)

        # Actualizar campos
        for key, value in data.items():
            setattr(employee, key, value)

        # Auditoría
        employee.updated_at = datetime.utcnow()
        if updated_by:
            employee.updated_by = updated_by

        self.db.commit()
        self.db.refresh(employee)

        return employee

    def delete_employee(self, employee_id: int, deleted_by: Optional[int] = None) -> None:
        """
        Elimina un Employee (soft delete).

        Validación: No puede eliminar si tiene subordinados activos.

        Args:
            employee_id: ID del Employee
            deleted_by: ID del usuario que elimina

        Raises:
            EntityNotFoundError: Si el Employee no existe
            BusinessRuleError: Si tiene subordinados activos
        """
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise EntityNotFoundError("Employee", employee_id)

        # Validación 12: No puede eliminar si tiene subordinados activos
        if self.repository.has_active_subordinates(employee_id):
            raise BusinessRuleError(
                f"No se puede eliminar el Employee {employee_id} porque tiene subordinados activos. "
                "Primero reasigna o elimina a sus subordinados."
            )

        # Soft delete
        employee.is_active = False
        employee.is_deleted = True
        employee.deleted_at = datetime.utcnow()
        if deleted_by:
            employee.deleted_by = deleted_by

        self.db.commit()

    def get_employee(self, employee_id: int) -> Employee:
        """Obtiene un Employee por ID"""
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise EntityNotFoundError("Employee", employee_id)
        return employee

    # ==================== VALIDACIONES (13 CRÍTICAS) ====================

    def _validate_all(self, data: Dict[str, Any], employee_id: Optional[int] = None, skip_individual_check: bool = False) -> None:
        """
        Aplica todas las 13 validaciones críticas de negocio.

        Args:
            data: Datos del Employee
            employee_id: ID del Employee (para updates, para validación circular)
            skip_individual_check: Si True, omite validación 1 (para create_with_user)
        """
        # Validación 1: individual_id debe existir y estar activo
        if not skip_individual_check and 'individual_id' in data:
            self._validate_individual_exists(data['individual_id'])

        # Validación 2: business_group_id debe existir y estar activo
        if 'business_group_id' in data:
            self._validate_business_group_exists(data['business_group_id'])

        # Validación 3: company_id debe existir, estar activo Y pertenecer a business_group
        if 'company_id' in data:
            business_group_id = data.get('business_group_id')
            self._validate_company_exists_and_belongs_to_bg(data['company_id'], business_group_id)

        # Validación 4: branch_id debe existir, estar activo Y pertenecer a company
        if 'branch_id' in data and data['branch_id'] is not None:
            company_id = data.get('company_id')
            self._validate_branch_belongs_to_company(data['branch_id'], company_id)

        # Validación 5: department_id debe existir, estar activo Y pertenecer a company
        if 'department_id' in data and data['department_id'] is not None:
            company_id = data.get('company_id')
            self._validate_department_belongs_to_company(data['department_id'], company_id)

        # Validación 6: position_id debe existir, estar activo Y pertenecer a company
        if 'position_id' in data and data['position_id'] is not None:
            company_id = data.get('company_id')
            self._validate_position_belongs_to_company(data['position_id'], company_id)

        # Validación 7: supervisor_id debe ser employee de la MISMA company
        if 'supervisor_id' in data and data['supervisor_id'] is not None:
            company_id = data.get('company_id')
            self._validate_supervisor_same_company(data['supervisor_id'], company_id)

        # Validación 8: employee_code único dentro de company
        if 'employee_code' in data and 'company_id' in data:
            self._validate_employee_code_unique(
                data['company_id'],
                data['employee_code'],
                employee_id
            )

        # Validación 9 y 10: No circular reference en supervisor_id
        if 'supervisor_id' in data and data['supervisor_id'] is not None:
            self._validate_no_circular_supervisor(employee_id, data['supervisor_id'])

        # Validación 11: Si user_id, verificar User.individual_id == Employee.individual_id
        if 'user_id' in data and data['user_id'] is not None and 'individual_id' in data:
            self._validate_user_individual_match(data['user_id'], data['individual_id'])

        # Validación 13: UNIQUE(company_id, employee_code) - cubierta por validación 8

    def _validate_individual_exists(self, individual_id: int) -> None:
        """Validación 1: individual_id debe existir y estar activo"""
        individual = self.individual_repository.get_by_id(individual_id)
        if not individual:
            raise EntityNotFoundError("Individual", individual_id)
        if not individual.is_active:
            raise BusinessRuleError(f"Individual {individual_id} no está activo")

    def _validate_business_group_exists(self, business_group_id: int) -> None:
        """Validación 2: business_group_id debe existir y estar activo"""
        bg = self.business_group_repository.get_by_id(business_group_id)
        if not bg:
            raise EntityNotFoundError("BusinessGroup", business_group_id)
        if not bg.is_active:
            raise BusinessRuleError(f"BusinessGroup {business_group_id} no está activo")

    def _validate_company_exists_and_belongs_to_bg(self, company_id: int, business_group_id: Optional[int]) -> None:
        """Validación 3: company_id debe existir, estar activo Y pertenecer a business_group"""
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise EntityNotFoundError("Company", company_id)
        if not company.is_active:
            raise BusinessRuleError(f"Company {company_id} no está activa")

        # Verificar que pertenece al business_group especificado
        if business_group_id and company.business_group_id != business_group_id:
            raise BusinessRuleError(
                f"Company {company_id} no pertenece al BusinessGroup {business_group_id}. "
                f"Pertenece a BusinessGroup {company.business_group_id}."
            )

    def _validate_branch_belongs_to_company(self, branch_id: int, company_id: Optional[int]) -> None:
        """Validación 4: branch_id debe existir, estar activo Y pertenecer a company"""
        branch = self.branch_repository.get_by_id(branch_id)
        if not branch:
            raise EntityNotFoundError("Branch", branch_id)
        if not branch.is_active:
            raise BusinessRuleError(f"Branch {branch_id} no está activa")

        # Verificar que pertenece a la company especificada
        if company_id and branch.company_id != company_id:
            raise BusinessRuleError(
                f"Branch {branch_id} no pertenece a Company {company_id}. "
                f"Pertenece a Company {branch.company_id}."
            )

    def _validate_department_belongs_to_company(self, department_id: int, company_id: Optional[int]) -> None:
        """Validación 5: department_id debe existir, estar activo Y pertenecer a company"""
        department = self.department_repository.get_by_id(department_id)
        if not department:
            raise EntityNotFoundError("Department", department_id)
        if not department.is_active:
            raise BusinessRuleError(f"Department {department_id} no está activo")

        # Verificar que pertenece a la company especificada
        if company_id and department.company_id != company_id:
            raise BusinessRuleError(
                f"Department {department_id} no pertenece a Company {company_id}. "
                f"Pertenece a Company {department.company_id}."
            )

    def _validate_position_belongs_to_company(self, position_id: int, company_id: Optional[int]) -> None:
        """Validación 6: position_id debe existir, estar activo Y pertenecer a company"""
        position = self.position_repository.get_by_id(position_id)
        if not position:
            raise EntityNotFoundError("Position", position_id)
        if not position.is_active:
            raise BusinessRuleError(f"Position {position_id} no está activa")

        # Verificar que pertenece a la company especificada
        if company_id and position.company_id != company_id:
            raise BusinessRuleError(
                f"Position {position_id} no pertenece a Company {company_id}. "
                f"Pertenece a Company {position.company_id}."
            )

    def _validate_supervisor_same_company(self, supervisor_id: int, company_id: Optional[int]) -> None:
        """Validación 7: supervisor_id debe ser employee de la MISMA company"""
        supervisor = self.repository.get_by_id(supervisor_id)
        if not supervisor:
            raise EntityNotFoundError("Supervisor (Employee)", supervisor_id)
        if not supervisor.is_active:
            raise BusinessRuleError(f"Supervisor (Employee) {supervisor_id} no está activo")

        # Verificar que pertenece a la misma company
        if company_id and supervisor.company_id != company_id:
            raise BusinessRuleError(
                f"Supervisor (Employee) {supervisor_id} no pertenece a la misma Company {company_id}. "
                f"El supervisor pertenece a Company {supervisor.company_id}."
            )

    def _validate_employee_code_unique(self, company_id: int, employee_code: str, employee_id: Optional[int] = None) -> None:
        """Validación 8: employee_code único dentro de company"""
        existing = self.repository.get_by_employee_code(company_id, employee_code)

        if existing and existing.id != employee_id:
            raise EntityAlreadyExistsError(
                "Employee",
                "employee_code",
                employee_code,
                f"Ya existe un empleado con código '{employee_code}' en la Company {company_id}"
            )

    def _validate_no_circular_supervisor(self, employee_id: Optional[int], supervisor_id: int) -> None:
        """
        Validaciones 9 y 10: No circular reference y no auto-supervisión.

        Algoritmo: Recorre la cadena de supervisores hasta la raíz,
        detectando ciclos y auto-referencias.
        """
        if employee_id is None:
            # En CREATE, no hay employee_id aún, solo validamos que supervisor existe
            return

        # Validación 10: No auto-supervisión
        if employee_id == supervisor_id:
            raise BusinessRuleError(
                f"Employee {employee_id} no puede ser su propio supervisor"
            )

        # Validación 9: No circular reference
        visited = set()
        current_id = supervisor_id
        depth = 0

        while current_id is not None:
            # Detectar ciclo
            if current_id in visited:
                raise BusinessRuleError(
                    f"Referencia circular detectada: supervisor_id {supervisor_id} crea un ciclo en la jerarquía"
                )

            # Detectar si el supervisor_id apunta al employee actual (circular)
            if current_id == employee_id:
                raise BusinessRuleError(
                    f"Referencia circular: Employee {employee_id} no puede estar en la cadena de supervisión de su supervisor {supervisor_id}"
                )

            visited.add(current_id)
            depth += 1

            # Protección contra jerarquías muy profundas
            if depth > self.MAX_HIERARCHY_DEPTH:
                raise BusinessRuleError(
                    f"Jerarquía de supervisión no puede exceder {self.MAX_HIERARCHY_DEPTH} niveles"
                )

            # Obtener siguiente supervisor
            supervisor = self.repository.get_by_id(current_id)
            if not supervisor:
                break
            current_id = supervisor.supervisor_id

    def _validate_user_individual_match(self, user_id: int, individual_id: int) -> None:
        """Validación 11: Si user_id, verificar User.individual_id == Employee.individual_id"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        # Verificar que el User está vinculado al mismo Individual
        user_individual = self.individual_repository.get_by_id(individual_id)
        if not user_individual:
            raise EntityNotFoundError("Individual", individual_id)

        if user_individual.user_id != user_id:
            raise BusinessRuleError(
                f"User {user_id} no está vinculado al Individual {individual_id}. "
                f"El User debe estar vinculado al mismo Individual del Employee."
            )
