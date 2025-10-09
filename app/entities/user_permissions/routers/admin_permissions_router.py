"""
Router para administración de permisos (Admin/Mobile App)

Define endpoints especiales para gestión masiva de permisos desde la app móvil.
"""

from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, User
from auth import get_current_user
from app.entities.user_permissions.controllers.user_permission_controller import UserPermissionController
from app.entities.user_permissions.schemas.user_permission_schemas import (
    AvailableEndpointsResponse,
    PermissionsJSONResponse,
    BulkPermissionUpdate
)
from app.core.endpoint_registry import discover_endpoints_from_app
from app.core.permissions import get_user_permissions_json
from app.shared.exceptions import (
    EntityValidationError,
    BusinessRuleError
)

router = APIRouter(
    prefix="/api/v1/admin/permissions",
    tags=["User Permissions"]
)


@router.get("/endpoints", response_model=AvailableEndpointsResponse)
def get_available_endpoints(
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene lista de todos los endpoints disponibles en la aplicación.

    **Requiere autenticación.**

    **Uso:** La app móvil usa este endpoint para mostrar la lista completa
    de endpoints disponibles al administrador cuando configura permisos.

    **Auto-discovery:** Este endpoint detecta automáticamente todos los endpoints
    registrados en FastAPI, por lo que NO necesitas editar código cuando
    agregas nuevas entidades.

    **Response:**
    ```json
    {
        "endpoints": [
            {
                "endpoint": "/api/v1/employees",
                "methods": ["GET", "POST"],
                "name": "get_all_employees",
                "tags": ["Employees"]
            }
        ]
    }
    ```
    """
    try:
        # Importación lazy para evitar circular import
        from fastapi import FastAPI
        from main import app
        endpoints = discover_endpoints_from_app(app)
        return {"total": len(endpoints), "endpoints": endpoints}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/json", response_model=PermissionsJSONResponse)
def get_user_permissions_as_json(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene permisos de un usuario en formato JSON para la app móvil.

    **Requiere autenticación.**

    **Uso:** La app móvil usa este endpoint para cargar los permisos actuales
    del usuario y mostrarlos como checkboxes (true/false).

    **Response formato mobile-friendly:**
    ```json
    {
        "user_id": 2,
        "user_name": "Ana López",
        "role": 2,
        "permissions": {
            "/api/v1/employees": {
                "GET": true,
                "POST": true,
                "PUT": false,
                "DELETE": false
            },
            "/api/v1/business-groups": {
                "GET": true,
                "POST": false
            }
        }
    }
    ```
    """
    try:
        permissions_json = get_user_permissions_json(db, user_id)
        return permissions_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/user/{user_id}/bulk", response_model=Dict[str, str])
def bulk_update_user_permissions(
    user_id: int,
    permissions_data: BulkPermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza masivamente todos los permisos de un usuario.

    **Requiere autenticación.**

    **Uso:** La app móvil envía el JSON completo con todos los permisos
    modificados (checkboxes marcados/desmarcados) y este endpoint:
    1. Elimina (soft delete) todos los permisos existentes del usuario
    2. Crea nuevos permisos según el JSON recibido

    **Request Body:**
    ```json
    {
        "permissions": {
            "/api/v1/employees": {
                "GET": true,
                "POST": true,
                "DELETE": false
            },
            "/api/v1/business-groups": {
                "GET": true
            }
        }
    }
    ```

    **Validaciones:**
    - Estructura JSON válida
    - Solo métodos permitidos (GET, POST, PUT, DELETE)
    - Valores booleanos
    - Transacción atómica (todo o nada)

    **Response:**
    ```json
    {
        "message": "Permisos actualizados exitosamente",
        "permissions_created": 5
    }
    ```
    """
    try:
        controller = UserPermissionController(db)
        data = permissions_data.model_dump()

        success = controller.bulk_update_user_permissions(
            user_id,
            data["permissions"],
            updated_by=current_user.id
        )

        if success:
            # Contar permisos creados
            from app.entities.user_permissions.repositories.user_permission_repository import UserPermissionRepository
            repo = UserPermissionRepository(db)
            count = len(repo.get_by_user_id(user_id, active_only=True))

            return {
                "message": "Permisos actualizados exitosamente",
                "permissions_created": str(count)
            }
        else:
            raise HTTPException(status_code=500, detail="Error al actualizar permisos")

    except EntityValidationError as e:
        raise HTTPException(status_code=422, detail={
            "message": e.message,
            "errors": e.details.get("validation_errors", {})
        })
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
