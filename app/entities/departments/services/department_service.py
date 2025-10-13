"""
Service: Department

Lógica de negocio y validaciones para Department.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
from math import ceil

from app.entities.departments.repositories.department_repository import DepartmentRepository
from app.entities.departments.models.department import Department
from app.entities.companies.repositories.company_repository import CompanyRepository
from app.entities.branches.repositories.branch_repository import BranchRepository
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)

# Límite de profundidad de jerarquía
MAX_HIERARCHY_DEPTH = 10


class DepartmentService:
    """Servicio para lógica de negocio de Department."""

    def __init__(self, db: Session):
        """Inicializa el servicio con el repositorio."""
        self.db = db
        self.repository = DepartmentRepository(db)
        self.company_repository = CompanyRepository(db)
        self.branch_repository = BranchRepository(db)

    # ==================== OPERACIONES CRUD ====================

    def create_department(
        self,
        data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> Department:
        """
        Crea un nuevo Department con validaciones de negocio.

        Args:
            data: Datos del Department
            created_by: ID del usuario que crea el registro

        Returns:
            Department creado

        Raises:
            EntityValidationError: Si los datos no son válidos
            EntityAlreadyExistsError: Si code ya existe para la company
            EntityNotFoundError: Si company_id, branch_id o parent_id no existen
            BusinessRuleError: Si hay violaciones de reglas de negocio
        """
        # Validar datos de entrada
        self._validate_department_data(data)

        # Validar que company_id existe y está activo
        company = self.company_repository.get_by_id(data["company_id"])
        if not company:
            raise EntityNotFoundError("Company", data["company_id"])

        if not company.is_active or company.is_deleted:
            raise BusinessRuleError(
                f"La Company {data['company_id']} no está activa",
                details={"company_id": data["company_id"]}
            )

        # Validar lógica corporativa: is_corporate vs branch_id
        is_corporate = data.get("is_corporate", False)
        branch_id = data.get("branch_id")

        if is_corporate and branch_id is not None:
            raise BusinessRuleError(
                "Departamentos corporativos no pueden tener branch_id asignado",
                details={"is_corporate": is_corporate, "branch_id": branch_id}
            )

        if not is_corporate and branch_id is None:
            raise BusinessRuleError(
                "Departamentos de sucursal deben tener branch_id asignado",
                details={"is_corporate": is_corporate}
            )

        # Validar que branch_id existe y pertenece a la company
        if branch_id:
            branch = self.branch_repository.get_by_id(branch_id)
            if not branch:
                raise EntityNotFoundError("Branch", branch_id)

            if branch.company_id != data["company_id"]:
                raise BusinessRuleError(
                    f"El Branch {branch_id} no pertenece a la Company {data['company_id']}",
                    details={
                        "branch_id": branch_id,
                        "branch_company_id": branch.company_id,
                        "expected_company_id": data["company_id"]
                    }
                )

            if not branch.is_active or branch.is_deleted:
                raise BusinessRuleError(
                    f"El Branch {branch_id} no está activo",
                    details={"branch_id": branch_id}
                )

        # Validar que parent_id existe y pertenece a la misma company
        if parent_id := data.get("parent_id"):
            parent = self.repository.get_by_id(parent_id)
            if not parent:
                raise EntityNotFoundError("Department (parent)", parent_id)

            if parent.company_id != data["company_id"]:
                raise BusinessRuleError(
                    f"El Department padre {parent_id} no pertenece a la misma Company {data['company_id']}",
                    details={
                        "parent_id": parent_id,
                        "parent_company_id": parent.company_id,
                        "expected_company_id": data["company_id"]
                    }
                )

            # CRITICAL: Validar no hay referencia circular
            # Este método debe ejecutarse ANTES de crear el registro
            # Nota: En creación, el department_id aún no existe, así que usamos None
            # La validación será más relevante en actualización
            if parent.parent_id:  # Si el padre tiene padre, validamos la cadena
                self._validate_no_circular_reference(None, parent_id)

        # Validar que code sea único por company
        existing_department = self.repository.get_by_code(data["company_id"], data["code"])
        if existing_department:
            raise EntityAlreadyExistsError(
                "Department",
                "code",
                data["code"]
            )

        # Agregar auditoría
        if created_by:
            data["created_by"] = created_by

        # Crear el registro
        return self.repository.create(data)

    def get_department_by_id(self, department_id: int) -> Department:
        """
        Obtiene un Department por ID.

        Args:
            department_id: ID del Department

        Returns:
            Department encontrado

        Raises:
            EntityNotFoundError: Si no se encuentra el Department
        """
        department = self.repository.get_by_id(department_id)
        if not department:
            raise EntityNotFoundError("Department", department_id)
        return department

    def get_all_departments(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Department]:
        """
        Obtiene todos los Departments con paginación.

        Args:
            skip: Registros a saltar
            limit: Máximo de registros
            active_only: Solo activos

        Returns:
            Lista de Departments
        """
        return self.repository.get_all(skip, limit, active_only)

    def get_departments_by_company(
        self,
        company_id: int,
        active_only: bool = True
    ) -> List[Department]:
        """
        Obtiene todos los Departments de una Company.

        Args:
            company_id: ID de la Company
            active_only: Solo activos

        Returns:
            Lista de Departments
        """
        return self.repository.get_by_company(company_id, active_only)

    def get_departments_by_branch(
        self,
        branch_id: int,
        active_only: bool = True
    ) -> List[Department]:
        """
        Obtiene Departments de una Branch específica.

        Args:
            branch_id: ID de la Branch
            active_only: Solo activos

        Returns:
            Lista de Departments
        """
        return self.repository.get_by_branch(branch_id, active_only)

    def update_department(
        self,
        department_id: int,
        data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> Department:
        """
        Actualiza un Department existente.

        Args:
            department_id: ID del Department
            data: Datos a actualizar
            updated_by: ID del usuario que actualiza

        Returns:
            Department actualizado

        Raises:
            EntityNotFoundError: Si no se encuentra el Department, Company, Branch o parent
            EntityAlreadyExistsError: Si code ya existe para la company
            EntityValidationError: Si los datos no son válidos
            BusinessRuleError: Si hay violaciones de reglas de negocio
        """
        # Verificar que existe
        department = self.get_department_by_id(department_id)

        # Validar datos de entrada
        self._validate_department_data(data, is_update=True)

        # Si se actualiza company_id, validar que existe y está activo
        if "company_id" in data:
            company = self.company_repository.get_by_id(data["company_id"])
            if not company:
                raise EntityNotFoundError("Company", data["company_id"])

            if not company.is_active or company.is_deleted:
                raise BusinessRuleError(
                    f"La Company {data['company_id']} no está activa",
                    details={"company_id": data["company_id"]}
                )

        # Validar lógica corporativa si se actualiza
        if "is_corporate" in data or "branch_id" in data:
            is_corporate = data.get("is_corporate", department.is_corporate)
            branch_id = data.get("branch_id", department.branch_id)

            if is_corporate and branch_id is not None:
                raise BusinessRuleError(
                    "Departamentos corporativos no pueden tener branch_id asignado",
                    details={"is_corporate": is_corporate, "branch_id": branch_id}
                )

            if not is_corporate and branch_id is None:
                raise BusinessRuleError(
                    "Departamentos de sucursal deben tener branch_id asignado",
                    details={"is_corporate": is_corporate}
                )

        # Si se actualiza branch_id, validar que existe y pertenece a la company
        if "branch_id" in data and data["branch_id"] is not None:
            branch = self.branch_repository.get_by_id(data["branch_id"])
            if not branch:
                raise EntityNotFoundError("Branch", data["branch_id"])

            # Determinar el company_id a validar (nuevo o actual)
            company_id = data.get("company_id", department.company_id)
            if branch.company_id != company_id:
                raise BusinessRuleError(
                    f"El Branch {data['branch_id']} no pertenece a la Company {company_id}",
                    details={
                        "branch_id": data["branch_id"],
                        "branch_company_id": branch.company_id,
                        "expected_company_id": company_id
                    }
                )

        # Si se actualiza parent_id, validar que existe y no crea ciclos
        if "parent_id" in data and data["parent_id"] is not None:
            parent_id = data["parent_id"]
            parent = self.repository.get_by_id(parent_id)
            if not parent:
                raise EntityNotFoundError("Department (parent)", parent_id)

            # Determinar el company_id a validar (nuevo o actual)
            company_id = data.get("company_id", department.company_id)
            if parent.company_id != company_id:
                raise BusinessRuleError(
                    f"El Department padre {parent_id} no pertenece a la misma Company {company_id}",
                    details={
                        "parent_id": parent_id,
                        "parent_company_id": parent.company_id,
                        "expected_company_id": company_id
                    }
                )

            # CRITICAL: Validar no hay referencia circular
            self._validate_no_circular_reference(department_id, parent_id)

        # Validar code único por company si se está actualizando
        if "code" in data:
            # Determinar el company_id a validar (nuevo o actual)
            company_id = data.get("company_id", department.company_id)
            existing_department = self.repository.get_by_code(company_id, data["code"])
            if existing_department and existing_department.id != department_id:
                raise EntityAlreadyExistsError(
                    "Department",
                    "code",
                    data["code"]
                )

        # Agregar auditoría
        if updated_by:
            data["updated_by"] = updated_by

        # Actualizar
        return self.repository.update(department_id, data)

    def delete_department(
        self,
        department_id: int,
        deleted_by: Optional[int] = None,
        soft_delete: bool = True
    ) -> bool:
        """
        Elimina un Department (soft delete por defecto).

        Args:
            department_id: ID del Department
            deleted_by: ID del usuario que elimina
            soft_delete: Si True, marca como inactivo

        Returns:
            True si se eliminó correctamente

        Raises:
            EntityNotFoundError: Si no se encuentra el Department
            BusinessRuleError: Si tiene dependencias activas
        """
        # Verificar que existe
        department = self.get_department_by_id(department_id)

        # Validar que no tenga subdepartamentos activos
        if self.repository.has_active_children(department_id):
            raise BusinessRuleError(
                "No se puede eliminar un Department con subdepartamentos activos asociados",
                details={"department_id": department_id}
            )

        # Validar que no tenga empleados activos (TODO placeholder)
        if self.repository.has_active_employees(department_id):
            raise BusinessRuleError(
                "No se puede eliminar un Department con employees activos asociados",
                details={"department_id": department_id}
            )

        # Si es soft delete, marcar deleted_by
        if soft_delete and deleted_by:
            self.repository.update(department_id, {
                "is_active": False,
                "is_deleted": True,
                "deleted_by": deleted_by,
                "deleted_at": datetime.utcnow()
            })
            return True

        return self.repository.delete(department_id, soft_delete)

    # ==================== OPERACIONES AVANZADAS ====================

    def search_departments(self, query: str, limit: int = 50) -> List[Department]:
        """
        Busca Departments por nombre o código (case-insensitive).

        Args:
            query: Término de búsqueda
            limit: Máximo de resultados

        Returns:
            Lista de Departments que coinciden
        """
        return self.repository.search(query, limit)

    def paginate_departments(
        self,
        page: int = 1,
        per_page: int = 20,
        active_only: bool = True,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> Dict[str, Any]:
        """
        Obtiene Departments paginados.

        Args:
            page: Número de página
            per_page: Registros por página
            active_only: Solo activos
            order_by: Campo de ordenamiento
            order_direction: Dirección de ordenamiento

        Returns:
            Diccionario con items paginados y metadatos
        """
        filters = {}
        if active_only:
            filters["is_active"] = True
            filters["is_deleted"] = False

        return self.repository.paginate(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by=order_by,
            order_direction=order_direction
        )

    # ==================== VALIDACIONES ====================

    def _validate_no_circular_reference(self, department_id: Optional[int], parent_id: int) -> None:
        """
        Valida que no existan referencias circulares en la jerarquía.
        Traversa la cadena de padres hasta la raíz.

        Args:
            department_id: ID del departamento actual (None si es creación)
            parent_id: ID del padre propuesto

        Raises:
            BusinessRuleError: Si se detecta un ciclo o se excede la profundidad máxima
        """
        visited = set()
        current_id = parent_id
        depth = 0

        while current_id is not None:
            # Detectar ciclo
            if current_id in visited:
                raise BusinessRuleError(
                    f"Referencia circular detectada: parent_id {parent_id} crea un ciclo",
                    details={"parent_id": parent_id, "cycle_detected_at": current_id}
                )

            # Prevenir auto-referencia (department no puede ser su propio padre)
            if department_id and current_id == department_id:
                raise BusinessRuleError(
                    "Un departamento no puede ser su propio padre",
                    details={"department_id": department_id, "parent_id": parent_id}
                )

            visited.add(current_id)
            depth += 1

            # Proteger contra jerarquías muy profundas
            if depth > MAX_HIERARCHY_DEPTH:
                raise BusinessRuleError(
                    f"La jerarquía no puede exceder {MAX_HIERARCHY_DEPTH} niveles",
                    details={"max_depth": MAX_HIERARCHY_DEPTH, "current_depth": depth}
                )

            # Obtener siguiente padre
            parent = self.repository.get_by_id(current_id)
            if not parent:
                break
            current_id = parent.parent_id

    def _validate_department_data(
        self,
        data: Dict[str, Any],
        is_update: bool = False
    ) -> None:
        """
        Valida los datos de un Department.

        Args:
            data: Datos a validar
            is_update: Si es una actualización (campos opcionales)

        Raises:
            EntityValidationError: Si hay errores de validación
        """
        errors = {}

        # Validar company_id (obligatorio en creación)
        if not is_update or "company_id" in data:
            company_id = data.get("company_id")
            if not company_id:
                errors["company_id"] = "El company_id es obligatorio"
            elif not isinstance(company_id, int) or company_id <= 0:
                errors["company_id"] = "El company_id debe ser un entero positivo"

        # Validar code (obligatorio en creación)
        if not is_update or "code" in data:
            code = data.get("code", "").strip() if isinstance(data.get("code"), str) else ""
            if not code:
                errors["code"] = "El código es obligatorio"
            elif len(code) > 50:
                errors["code"] = "El código no puede exceder 50 caracteres"

        # Validar name (obligatorio en creación)
        if not is_update or "name" in data:
            name = data.get("name", "").strip() if isinstance(data.get("name"), str) else ""
            if not name:
                errors["name"] = "El nombre es obligatorio"
            elif len(name) < 2:
                errors["name"] = "El nombre debe tener al menos 2 caracteres"
            elif len(name) > 200:
                errors["name"] = "El nombre no puede exceder 200 caracteres"

        # Validar description si se proporciona
        if "description" in data and data["description"]:
            if not isinstance(data["description"], str):
                errors["description"] = "La descripción debe ser texto"

        if errors:
            raise EntityValidationError("Department", errors)