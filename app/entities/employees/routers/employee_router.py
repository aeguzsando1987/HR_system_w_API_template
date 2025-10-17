"""
Employee Router - REST API endpoints for Employee entity
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, User
from auth import get_current_user
from app.entities.employees.controllers.employee_controller import EmployeeController
from app.entities.employees.schemas.employee_schemas import (
    EmployeeCreate,
    EmployeeCreateWithUser,
    EmployeeUpdate,
    EmployeeResponse
)
from app.shared.exceptions import EntityNotFoundError, EntityValidationError, BusinessRuleError, EntityAlreadyExistsError


router = APIRouter(prefix="/api/v1/employees", tags=["Employees"])


@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un Employee (requiere Individual existente).

    **Requiere:**
    - individual_id: Debe existir en la base de datos
    - company_id, business_group_id: Requeridos
    - employee_code: Único por empresa

    **Opcional:**
    - branch_id, department_id, position_id, supervisor_id
    """
    try:
        controller = EmployeeController(db)
        data = employee_data.model_dump(exclude_unset=True)
        return controller.create_employee(data, current_user_id=current_user.id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/with-user", response_model=EmployeeResponse, status_code=201)
def create_employee_with_user(
    employee_data: EmployeeCreateWithUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ⭐ Crea Employee + Individual + User en transacción atómica.

    **Este es el endpoint principal para registro completo de empleados.**

    **Transacción atómica**: Si falla cualquier parte, se hace rollback completo.

    **Datos requeridos:**
    - Individual: first_name, last_name, email, phone
    - Employee: business_group_id, company_id, employee_code, hire_date
    - User (opcional): user_email, user_password, user_role

    **Ejemplo con User**:
    ```json
    {
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan.perez@empresa.com",
      "phone": "+52-555-1234",
      "business_group_id": 1,
      "company_id": 1,
      "employee_code": "EMP001",
      "hire_date": "2025-01-15",
      "user_email": "juan.perez@sistema.com",
      "user_password": "SecurePass123!",
      "user_role": 4
    }
    ```

    **Ejemplo sin User**:
    ```json
    {
      "first_name": "María",
      "last_name": "López",
      "email": "maria.lopez@empresa.com",
      "phone": "+52-555-5678",
      "business_group_id": 1,
      "company_id": 1,
      "employee_code": "EMP002",
      "hire_date": "2025-01-20"
    }
    ```
    """
    try:
        controller = EmployeeController(db)
        data = employee_data.model_dump(exclude_unset=True)
        return controller.create_employee_with_user(data, current_user_id=current_user.id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# RUTAS ESPECÍFICAS ANTES DE RUTAS PARAMETRIZADAS (evita error de route ordering)

@router.get("/search", response_model=List[EmployeeResponse])
def search_employees(
    q: str = Query(..., min_length=2, description="Texto a buscar en código, nombre o email"),
    company_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca Employees por código, nombre o email.

    **Búsqueda case-insensitive** en:
    - employee_code
    - Individual.first_name
    - Individual.last_name
    - Individual.email
    """
    try:
        controller = EmployeeController(db)
        return controller.search_employees(q, company_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-company/{company_id}", response_model=List[EmployeeResponse])
def get_employees_by_company(
    company_id: int,
    active_only: bool = Query(True, description="Solo empleados activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los Employees de una empresa.

    **Query Parameters**:
    - active_only: Si es True, solo empleados activos (default: True)
    """
    try:
        controller = EmployeeController(db)
        return controller.get_by_company(company_id, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-supervisor/{supervisor_id}", response_model=List[EmployeeResponse])
def get_employees_by_supervisor(
    supervisor_id: int,
    active_only: bool = Query(True, description="Solo empleados activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los subordinados de un supervisor.

    **Query Parameters**:
    - active_only: Si es True, solo empleados activos (default: True)
    """
    try:
        controller = EmployeeController(db)
        return controller.get_by_supervisor(supervisor_id, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AHORA LAS RUTAS PARAMETRIZADAS

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un Employee por ID."""
    try:
        controller = EmployeeController(db)
        return controller.get_employee(employee_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un Employee.

    **Campos actualizables:**
    - branch_id, department_id, position_id, supervisor_id
    - employee_code, employment_status, employment_type
    - base_salary, currency
    """
    try:
        controller = EmployeeController(db)
        data = employee_data.model_dump(exclude_unset=True)
        return controller.update_employee(employee_id, data, current_user_id=current_user.id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{employee_id}", response_model=EmployeeResponse)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un Employee (soft delete).

    **Validación**: No puede eliminar si tiene subordinados activos.
    """
    try:
        controller = EmployeeController(db)
        controller.delete_employee(employee_id, current_user_id=current_user.id)
        return controller.get_employee(employee_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[EmployeeResponse])
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos los Employees con paginación.

    **Query Parameters**:
    - skip: Número de registros a saltar (default: 0)
    - limit: Número máximo de registros (default: 100, max: 500)
    - active_only: Solo activos y no eliminados (default: True)
    """
    try:
        controller = EmployeeController(db)
        employees = controller.service.repository.get_all(
            skip=skip,
            limit=limit,
            active_only=active_only
        )
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
