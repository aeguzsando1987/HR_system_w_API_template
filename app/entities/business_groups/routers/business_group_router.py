"""
Router: BusinessGroup

Endpoints REST para BusinessGroup.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user, require_admin
from database import User
from app.entities.business_groups.controllers.business_group_controller import BusinessGroupController
from app.entities.business_groups.schemas.business_group_schemas import (
    BusinessGroupCreate,
    BusinessGroupUpdate,
    BusinessGroupResponse,
    BusinessGroupListResponse
)


router = APIRouter(
    prefix="/api/v1/business-groups",
    tags=["Business Groups"]
)


@router.post(
    "",
    response_model=BusinessGroupResponse,
    status_code=201,
    summary="Crear BusinessGroup",
    description="Crea un nuevo grupo empresarial. Requiere rol de administrador."
)
def create_business_group(
    business_group_data: BusinessGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Crea un nuevo BusinessGroup.

    **Permisos:** Admin

    **Validaciones:**
    - name es obligatorio (min 2 caracteres)
    - tax_id debe ser único si se proporciona

    **Ejemplo de request:**
    ```json
    {
        "name": "Corporativo Global SA",
        "legal_name": "Corporativo Global Sociedad Anónima",
        "tax_id": "CGS123456",
        "description": "Grupo empresarial multinacional"
    }
    ```
    """
    controller = BusinessGroupController(db)
    return controller.create_business_group(
        business_group_data,
        current_user_id=current_user.id
    )


@router.get(
    "",
    response_model=list[BusinessGroupResponse],
    summary="Listar BusinessGroups",
    description="Obtiene lista de grupos empresariales con paginación."
)
def get_all_business_groups(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    active_only: bool = Query(True, description="Solo registros activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene lista de BusinessGroups con paginación simple.

    **Permisos:** Usuario autenticado

    **Parámetros:**
    - skip: Número de registros a saltar (default: 0)
    - limit: Máximo de registros a retornar (default: 100, max: 500)
    - active_only: Si es True, solo retorna registros activos (default: True)
    """
    controller = BusinessGroupController(db)
    return controller.get_all_business_groups(skip, limit, active_only)


@router.get(
    "/paginated",
    response_model=BusinessGroupListResponse,
    summary="Listar BusinessGroups paginados",
    description="Obtiene BusinessGroups con paginación avanzada y metadatos."
)
def get_business_groups_paginated(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Registros por página"),
    active_only: bool = Query(True, description="Solo activos"),
    order_by: str = Query("created_at", description="Campo de ordenamiento"),
    order_direction: str = Query("desc", regex="^(asc|desc)$", description="Dirección de ordenamiento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene BusinessGroups con paginación avanzada.

    **Permisos:** Usuario autenticado

    **Retorna:**
    - items: Lista de BusinessGroups
    - total: Total de registros
    - page: Página actual
    - per_page: Registros por página
    - pages: Total de páginas
    """
    controller = BusinessGroupController(db)
    return controller.paginate_business_groups(
        page=page,
        per_page=per_page,
        active_only=active_only,
        order_by=order_by,
        order_direction=order_direction
    )


@router.get(
    "/search",
    response_model=list[BusinessGroupResponse],
    summary="Buscar BusinessGroups",
    description="Busca BusinessGroups por nombre (case-insensitive)."
)
def search_business_groups(
    name: str = Query(..., min_length=1, description="Término de búsqueda"),
    limit: int = Query(50, ge=1, le=200, description="Máximo de resultados"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca BusinessGroups por nombre o razón social.

    **Permisos:** Usuario autenticado

    **Búsqueda:**
    - Case-insensitive
    - Busca en campos: name, legal_name
    """
    controller = BusinessGroupController(db)
    return controller.search_business_groups(name, limit)


@router.get(
    "/{business_group_id}",
    response_model=BusinessGroupResponse,
    summary="Obtener BusinessGroup por ID",
    description="Obtiene un BusinessGroup específico por su ID."
)
def get_business_group(
    business_group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un BusinessGroup por ID.

    **Permisos:** Usuario autenticado

    **Errores:**
    - 404: BusinessGroup no encontrado
    """
    controller = BusinessGroupController(db)
    return controller.get_business_group(business_group_id)


@router.put(
    "/{business_group_id}",
    response_model=BusinessGroupResponse,
    summary="Actualizar BusinessGroup",
    description="Actualiza un BusinessGroup existente. Requiere rol de administrador."
)
def update_business_group(
    business_group_id: int,
    business_group_data: BusinessGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Actualiza un BusinessGroup.

    **Permisos:** Admin

    **Validaciones:**
    - tax_id debe ser único si se modifica

    **Ejemplo de request:**
    ```json
    {
        "name": "Corporativo Global SA (Actualizado)",
        "description": "Nueva descripción",
        "is_active": true
    }
    ```

    **Errores:**
    - 404: BusinessGroup no encontrado
    - 422: Errores de validación
    - 409: tax_id duplicado
    """
    controller = BusinessGroupController(db)
    return controller.update_business_group(
        business_group_id,
        business_group_data,
        current_user_id=current_user.id
    )


@router.delete(
    "/{business_group_id}",
    summary="Eliminar BusinessGroup",
    description="Elimina un BusinessGroup (soft delete). Requiere rol de administrador."
)
def delete_business_group(
    business_group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Elimina un BusinessGroup (soft delete).

    **Permisos:** Admin

    **Validaciones:**
    - No se puede eliminar si tiene empresas activas asociadas

    **Errores:**
    - 404: BusinessGroup no encontrado
    - 400: Tiene empresas activas asociadas
    """
    controller = BusinessGroupController(db)
    return controller.delete_business_group(
        business_group_id,
        current_user_id=current_user.id
    )
