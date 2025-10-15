"""
Individual Router - Endpoints REST API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db, User
from auth import get_current_user
from app.entities.individuals.controllers.individual_controller import IndividualController
from app.entities.individuals.schemas.individual_schemas import (
    IndividualCreate,
    IndividualCreateWithUser,
    IndividualUpdate,
    IndividualResponse
)
from app.shared.exceptions import EntityNotFoundError, EntityValidationError, BusinessRuleError, EntityAlreadyExistsError

router = APIRouter(prefix="/api/v1/individuals", tags=["Individuals"])


@router.post("/", response_model=IndividualResponse, status_code=201)
def create_individual(
    individual_data: IndividualCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo Individual (sin User asociado).

    Para crear un Individual con User, usa el endpoint POST /with-user
    """
    try:
        controller = IndividualController(db)
        data = individual_data.model_dump(exclude_unset=True)
        return controller.create_individual(data, current_user_id=current_user.id)
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


@router.post("/with-user", response_model=IndividualResponse, status_code=201)
def create_individual_with_user(
    individual_data: IndividualCreateWithUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ⭐ Crea un Individual + User en una transacción atómica.

    Este es el endpoint principal para registrar nuevas personas con acceso al sistema.

    **Transacción atómica**: Si falla cualquier parte (User o Individual), se hace rollback completo.

    **Ejemplo**:
    ```json
    {
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan.perez@empresa.com",
      "phone": "+52-555-1234",
      "user_email": "juan.perez@sistema.com",
      "user_password": "SecurePass123!",
      "user_role": 4
    }
    ```
    """
    try:
        controller = IndividualController(db)
        data = individual_data.model_dump(exclude_unset=True)
        return controller.create_individual_with_user(data, current_user_id=current_user.id)
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


@router.get("/search", response_model=List[IndividualResponse])
def search_individuals(
    q: str = Query(..., min_length=2, description="Texto a buscar en nombre, apellido o email"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca Individuals por nombre, apellido o email.

    **Búsqueda case-insensitive** en los campos:
    - first_name
    - last_name
    - email
    """
    try:
        controller = IndividualController(db)
        return controller.search_individuals(q, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-document", response_model=IndividualResponse)
def get_individual_by_document(
    document_number: str = Query(None, description="Número de documento"),
    curp: str = Query(None, description="CURP (18 caracteres)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca un Individual por número de documento o CURP.

    **Debe proveer al menos uno**:
    - document_number: Número de documento
    - curp: CURP (México, 18 caracteres)
    """
    if not document_number and not curp:
        raise HTTPException(
            status_code=400,
            detail="Debe proveer document_number o curp"
        )

    try:
        controller = IndividualController(db)

        if curp:
            individual = controller.get_individual_by_curp(curp)
        else:
            individual = controller.get_individual_by_document(document_number)

        if not individual:
            raise HTTPException(
                status_code=404,
                detail=f"Individual no encontrado con {'CURP: ' + curp if curp else 'documento: ' + document_number}"
            )

        return individual
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{individual_id}", response_model=IndividualResponse)
def get_individual(
    individual_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un Individual por ID."""
    try:
        controller = IndividualController(db)
        return controller.get_individual(individual_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{individual_id}", response_model=IndividualResponse)
def update_individual(
    individual_id: int,
    individual_data: IndividualUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza un Individual."""
    try:
        controller = IndividualController(db)
        data = individual_data.model_dump(exclude_unset=True)
        return controller.update_individual(individual_id, data, current_user_id=current_user.id)
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


@router.delete("/{individual_id}", response_model=IndividualResponse)
def delete_individual(
    individual_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un Individual (soft delete)."""
    try:
        controller = IndividualController(db)
        controller.delete_individual(individual_id, current_user_id=current_user.id)
        return controller.get_individual(individual_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[IndividualResponse])
def list_individuals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos los Individuals con paginación.

    **Query Parameters**:
    - skip: Número de registros a saltar (default: 0)
    - limit: Número máximo de registros (default: 100, max: 500)
    - active_only: Solo activos y no eliminados (default: true)
    """
    try:
        controller = IndividualController(db)
        individuals = controller.service.repository.get_all(
            skip=skip,
            limit=limit,
            active_only=active_only
        )
        return individuals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))