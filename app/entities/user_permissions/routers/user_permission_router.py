"""
Router para UserPermission

Define los endpoints REST API para gestión de permisos granulares de usuarios.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, User
from auth import get_current_user
from app.entities.user_permissions.controllers.user_permission_controller import UserPermissionController
from app.entities.user_permissions.schemas.user_permission_schemas import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionListResponse
)
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    BusinessRuleError
)

router = APIRouter(
    prefix="/api/v1/permissions",
    tags=["User Permissions"]
)


@router.post("/", response_model=PermissionResponse, status_code=201)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo permiso para un usuario.

    **Requiere autenticación.**

    - **user_id**: ID del usuario al que se asigna el permiso
    - **endpoint**: Ruta del endpoint (ej: /api/v1/employees)
    - **method**: Método HTTP (GET, POST, PUT, DELETE)
    - **allowed**: Si el permiso está habilitado (true/false)

    **Validaciones:**
    - El endpoint debe comenzar con /api/
    - El método debe ser válido (GET, POST, PUT, DELETE)
    - No puede haber permisos duplicados (user_id + endpoint + method debe ser único)
    """
    try:
        controller = UserPermissionController(db)
        data = permission_data.model_dump()
        permission = controller.create_permission(data, created_by=current_user.id)
        return permission

    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={
            "message": e.message,
            "errors": e.details.get("validation_errors", {})
        })
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PermissionResponse])
def get_all_permissions(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    active_only: bool = Query(True, description="Solo permisos activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene lista de todos los permisos con paginación.

    **Requiere autenticación.**
    """
    try:
        controller = UserPermissionController(db)
        permissions = controller.get_all_permissions(skip, limit, active_only)
        return permissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[PermissionResponse])
def get_permissions_by_user(
    user_id: int,
    active_only: bool = Query(True, description="Solo permisos activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los permisos de un usuario específico.

    **Requiere autenticación.**

    - **user_id**: ID del usuario
    """
    try:
        controller = UserPermissionController(db)
        permissions = controller.get_permissions_by_user(user_id, active_only)
        return permissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un permiso por ID.

    **Requiere autenticación.**

    - **permission_id**: ID del permiso
    """
    try:
        controller = UserPermissionController(db)
        permission = controller.get_permission(permission_id)
        return permission
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un permiso existente.

    **Requiere autenticación.**

    - **permission_id**: ID del permiso a actualizar

    **Campos actualizables:**
    - allowed (true/false)
    - is_active

    **Nota:** No se puede cambiar user_id, endpoint ni method después de creado.
    Si necesitas cambiar estos valores, debes crear un nuevo permiso.
    """
    try:
        controller = UserPermissionController(db)
        data = permission_data.model_dump(exclude_unset=True)
        permission = controller.update_permission(permission_id, data, updated_by=current_user.id)
        return permission
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={
            "message": e.message,
            "errors": e.details.get("validation_errors", {})
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{permission_id}", response_model=PermissionResponse)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina (soft delete) un permiso.

    **Requiere autenticación.**

    - **permission_id**: ID del permiso a eliminar

    **Nota:** Esto es un soft delete. El registro permanece en la base de datos
    con is_deleted=True y deleted_at poblado.
    """
    try:
        controller = UserPermissionController(db)
        permission = controller.delete_permission(permission_id, deleted_by=current_user.id)
        return permission
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
