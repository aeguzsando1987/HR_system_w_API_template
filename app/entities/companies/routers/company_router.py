"""
Router: Company

Endpoints REST API para gestión de Companies.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, User
from auth import get_current_user
from app.entities.companies.controllers.company_controller import CompanyController
from app.entities.companies.schemas.company_schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
    CompanySearchResponse
)
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    BusinessRuleError
)

router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Companies"]
)


@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una nueva Company."""
    try:
        controller = CompanyController(db)
        data = company_data.model_dump()
        company = controller.create_company(data, current_user_id=current_user.id)
        return company
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


@router.get("/", response_model=List[CompanyResponse])
def get_all_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene lista de Companies."""
    try:
        controller = CompanyController(db)
        return controller.get_all_companies(skip, limit, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paginated", response_model=CompanyListResponse)
def get_companies_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene Companies paginadas."""
    try:
        controller = CompanyController(db)
        result = controller.paginate_companies(page, per_page)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=CompanySearchResponse)
def search_companies(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Busca Companies por nombre."""
    try:
        controller = CompanyController(db)
        companies = controller.search_companies(q, limit)
        return {"items": companies, "total": len(companies), "query": q}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una Company por ID."""
    try:
        controller = CompanyController(db)
        return controller.get_company(company_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza una Company."""
    try:
        controller = CompanyController(db)
        data = company_data.model_dump(exclude_unset=True)
        return controller.update_company(company_id, data, current_user_id=current_user.id)
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


@router.delete("/{company_id}", response_model=CompanyResponse)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina una Company (soft delete)."""
    try:
        controller = CompanyController(db)
        controller.delete_company(company_id, current_user_id=current_user.id)
        return controller.get_company(company_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
