"""
Router: Department

Endpoints REST API para gestión de Departments.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db, User
from auth import get_current_user
from app.entities.departments.controllers.department_controller import DepartmentController
from app.entities.departments.schemas.department_schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentListResponse
)
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    BusinessRuleError
)

router = APIRouter(
    prefix="/api/v1/departments",
    tags=["Departments"]
)


@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea un nuevo Department."""
    try:
        controller = DepartmentController(db)
        data = department_data.model_dump()
        department = controller.create_department(data, current_user_id=current_user.id)
        return department
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'uq_company_department_code' in error_msg:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un departamento con el código '{department_data.code}' en esta empresa"
            )
        raise HTTPException(status_code=400, detail=f"Error de integridad en la base de datos: {error_msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[DepartmentResponse])
def get_all_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene lista de Departments."""
    try:
        controller = DepartmentController(db)
        return controller.get_all_departments(skip, limit, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paginated", response_model=DepartmentListResponse)
def get_departments_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene Departments paginados."""
    try:
        controller = DepartmentController(db)
        result = controller.paginate_departments(page, per_page)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[DepartmentResponse])
def search_departments(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Busca Departments por nombre o código."""
    try:
        controller = DepartmentController(db)
        departments = controller.search_departments(q, limit)
        return departments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-company/{company_id}", response_model=List[DepartmentResponse])
def get_departments_by_company(
    company_id: int,
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene Departments por Company."""
    try:
        controller = DepartmentController(db)
        return controller.get_departments_by_company(company_id, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-branch/{branch_id}", response_model=List[DepartmentResponse])
def get_departments_by_branch(
    branch_id: int,
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene Departments por Branch."""
    try:
        controller = DepartmentController(db)
        return controller.get_departments_by_branch(branch_id, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un Department por ID."""
    try:
        controller = DepartmentController(db)
        return controller.get_department(department_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza un Department."""
    try:
        controller = DepartmentController(db)
        data = department_data.model_dump(exclude_unset=True)
        return controller.update_department(department_id, data, current_user_id=current_user.id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'uq_company_department_code' in error_msg:
            code = data.get('code', 'especificado')
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un departamento con el código '{code}' en esta empresa"
            )
        raise HTTPException(status_code=400, detail=f"Error de integridad en la base de datos: {error_msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{department_id}", response_model=DepartmentResponse)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un Department (soft delete)."""
    try:
        controller = DepartmentController(db)
        controller.delete_department(department_id, current_user_id=current_user.id)
        return controller.get_department(department_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))