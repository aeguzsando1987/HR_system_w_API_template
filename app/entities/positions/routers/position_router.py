"""
Router: Position

Endpoints REST API para gestion de Positions.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, User
from auth import get_current_user
from app.entities.positions.controllers.position_controller import PositionController
from app.entities.positions.schemas.position_schemas import (
    PositionCreate,
    PositionUpdate,
    PositionResponse,
    PositionListResponse
)
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    BusinessRuleError
)

router = APIRouter(
    prefix="/api/v1/positions",
    tags=["Positions"]
)


@router.post("/", response_model=PositionResponse, status_code=201)
def create_position(
    position_data: PositionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea un nuevo Position."""
    try:
        controller = PositionController(db)
        data = position_data.model_dump()
        position = controller.create_position(data, current_user_id=current_user.id)
        return position
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PositionResponse])
def get_all_positions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene lista de Positions."""
    try:
        controller = PositionController(db)
        return controller.get_all_positions(skip, limit, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paginated", response_model=PositionListResponse)
def get_positions_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene Positions paginados."""
    try:
        controller = PositionController(db)
        result = controller.paginate_positions(page, per_page)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[PositionResponse])
def search_positions(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Busca Positions por title."""
    try:
        controller = PositionController(db)
        positions = controller.search_positions(q, limit)
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-company/{company_id}", response_model=List[PositionResponse])
def get_positions_by_company(
    company_id: int,
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene Positions por Company."""
    try:
        controller = PositionController(db)
        return controller.get_positions_by_company(company_id, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{position_id}", response_model=PositionResponse)
def get_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un Position por ID."""
    try:
        controller = PositionController(db)
        return controller.get_position(position_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{position_id}", response_model=PositionResponse)
def update_position(
    position_id: int,
    position_data: PositionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza un Position."""
    try:
        controller = PositionController(db)
        data = position_data.model_dump(exclude_unset=True)
        return controller.update_position(position_id, data, current_user_id=current_user.id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "errors": e.details.get("validation_errors", {})})
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{position_id}", response_model=PositionResponse)
def delete_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un Position (soft delete)."""
    try:
        controller = PositionController(db)
        controller.delete_position(position_id, current_user_id=current_user.id)
        return controller.get_position(position_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))