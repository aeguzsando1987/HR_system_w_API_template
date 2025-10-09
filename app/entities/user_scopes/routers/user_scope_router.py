"""
Router para UserScope

Define los endpoints REST API para gestión de UserScopes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, User
from auth import get_current_user
from app.entities.user_scopes.controllers.user_scope_controller import UserScopeController
from app.entities.user_scopes.schemas.user_scope_schemas import (
    UserScopeCreate,
    UserScopeUpdate,
    UserScopeResponse,
    UserScopeListResponse
)
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    BusinessRuleError
)

router = APIRouter(
    prefix="/api/v1/user-scopes",
    tags=["User Scopes"]
)


@router.post("/", response_model=UserScopeResponse, status_code=201)
def create_user_scope(
    user_scope_data: UserScopeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo UserScope.

    **Requiere autenticación.**

    - **user_id**: ID del usuario al que se asigna el scope
    - **scope_type**: Tipo de scope (GLOBAL, BUSINESS_GROUP, COMPANY, BRANCH, DEPARTMENT)
    - **business_group_id**: ID del BusinessGroup (solo si scope_type=BUSINESS_GROUP)
    - **company_id**: ID de la Company (solo si scope_type=COMPANY)
    - **branch_id**: ID del Branch (solo si scope_type=BRANCH)
    - **department_id**: ID del Department (solo si scope_type=DEPARTMENT)

    **Validaciones:**
    - Admin (role=1): Puede asignar cualquier scope
    - Gerente (role=2): Solo puede asignar BUSINESS_GROUP, COMPANY o BRANCH
    - Gestor (role=3): Solo puede asignar DEPARTMENT
    - Colaborador (role=4) y Guest (role=5): NO pueden tener scopes
    """
    try:
        controller = UserScopeController(db)
        data = user_scope_data.model_dump()

        # Obtener el rol del usuario al que se le asigna el scope
        from database import User as UserModel
        target_user = db.query(UserModel).filter(UserModel.id == data["user_id"]).first()
        if not target_user:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {data['user_id']} no encontrado")

        user_scope = controller.create_user_scope(
            data,
            user_role=target_user.role,
            created_by=current_user.id
        )
        return user_scope

    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={
            "message": e.message,
            "errors": e.details.get("validation_errors", {})
        })
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[UserScopeResponse])
def get_all_user_scopes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    active_only: bool = Query(True, description="Solo scopes activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene lista de todos los UserScopes con paginación.

    **Requiere autenticación.**
    """
    try:
        controller = UserScopeController(db)
        user_scopes = controller.get_all_user_scopes(skip, limit, active_only)
        return user_scopes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[UserScopeResponse])
def get_scopes_by_user(
    user_id: int,
    active_only: bool = Query(True, description="Solo scopes activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los scopes de un usuario específico.

    **Requiere autenticación.**

    - **user_id**: ID del usuario
    """
    try:
        controller = UserScopeController(db)
        user_scopes = controller.get_scopes_by_user(user_id, active_only)
        return user_scopes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_scope_id}", response_model=UserScopeResponse)
def get_user_scope(
    user_scope_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un UserScope por ID.

    **Requiere autenticación.**

    - **user_scope_id**: ID del UserScope
    """
    try:
        controller = UserScopeController(db)
        user_scope = controller.get_user_scope(user_scope_id)
        return user_scope
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_scope_id}", response_model=UserScopeResponse)
def update_user_scope(
    user_scope_id: int,
    user_scope_data: UserScopeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un UserScope existente.

    **Requiere autenticación.**

    - **user_scope_id**: ID del UserScope a actualizar

    **Campos actualizables:**
    - business_group_id, company_id, branch_id, department_id
    - is_active

    **Nota:** No se puede cambiar user_id ni scope_type después de creado.
    """
    try:
        controller = UserScopeController(db)
        data = user_scope_data.model_dump(exclude_unset=True)
        user_scope = controller.update_user_scope(user_scope_id, data, updated_by=current_user.id)
        return user_scope
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_scope_id}", response_model=UserScopeResponse)
def delete_user_scope(
    user_scope_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina (soft delete) un UserScope.

    **Requiere autenticación.**

    - **user_scope_id**: ID del UserScope a eliminar

    **Nota:** Esto es un soft delete. El registro permanece en la base de datos
    con is_deleted=True y deleted_at poblado.
    """
    try:
        controller = UserScopeController(db)
        user_scope = controller.delete_user_scope(user_scope_id, deleted_by=current_user.id)
        return user_scope
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
