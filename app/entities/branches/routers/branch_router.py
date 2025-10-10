"""
Router: Branch

Endpoints REST API para gestión de Branches.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, User
from auth import get_current_user
from app.entities.branches.controllers.branch_controller import BranchController
from app.entities.branches.schemas.branch_schemas import (
    BranchCreate,
    BranchUpdate,
    BranchResponse,
    BranchListResponse
)
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    BusinessRuleError
)

router = APIRouter(
    prefix="/api/v1/branches",
    tags=["Branches"]
)


@router.post("/", response_model=BranchResponse, status_code=201)
def create_branch(
    branch_data: BranchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una nueva Branch."""
    try:
        controller = BranchController(db)
        data = branch_data.model_dump()
        branch = controller.create_branch(data, current_user_id=current_user.id)
        return branch
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[BranchResponse])
def get_all_branches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene lista de Branches."""
    try:
        controller = BranchController(db)
        return controller.get_all_branches(skip, limit, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paginated", response_model=BranchListResponse)
def get_branches_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene Branches paginadas."""
    try:
        controller = BranchController(db)
        result = controller.paginate_branches(page, per_page)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[BranchResponse])
def search_branches(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Busca Branches por nombre."""
    try:
        controller = BranchController(db)
        branches = controller.search_branches(q, limit)
        return branches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-company/{company_id}", response_model=List[BranchResponse])
def get_branches_by_company(
    company_id: int,
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene Branches por Company."""
    try:
        controller = BranchController(db)
        return controller.get_branches_by_company(company_id, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una Branch por ID."""
    try:
        controller = BranchController(db)
        return controller.get_branch(branch_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{branch_id}", response_model=BranchResponse)
def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza una Branch."""
    try:
        controller = BranchController(db)
        data = branch_data.model_dump(exclude_unset=True)
        return controller.update_branch(branch_id, data, current_user_id=current_user.id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{branch_id}", response_model=BranchResponse)
def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina una Branch (soft delete)."""
    try:
        controller = BranchController(db)
        controller.delete_branch(branch_id, current_user_id=current_user.id)
        return controller.get_branch(branch_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
