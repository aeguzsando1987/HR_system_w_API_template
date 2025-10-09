"""
Schemas Pydantic para UserPermission

Define los esquemas de validación y serialización para los permisos granulares.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum


class HTTPMethodEnum(str, Enum):
    """Métodos HTTP permitidos para permisos."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class PermissionBase(BaseModel):
    """Schema base con campos comunes."""
    user_id: int = Field(..., description="ID del usuario")
    endpoint: str = Field(..., min_length=1, max_length=255, description="Ruta del endpoint (/api/v1/employees)")
    method: HTTPMethodEnum = Field(..., description="Método HTTP (GET, POST, PUT, DELETE, PATCH)")
    allowed: bool = Field(default=False, description="Permiso concedido (true) o denegado (false)")

    @field_validator('endpoint')
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Valida que endpoint comience con /api/"""
        if not v.startswith('/api/'):
            raise ValueError("Endpoint debe comenzar con /api/")
        return v


class PermissionCreate(PermissionBase):
    """
    Schema para crear un permiso (POST).

    Ejemplo:
    {
        "user_id": 2,
        "endpoint": "/api/v1/employees",
        "method": "GET",
        "allowed": true
    }
    """
    pass


class PermissionUpdate(BaseModel):
    """
    Schema para actualizar un permiso (PUT/PATCH).

    Solo permite actualizar el campo 'allowed' (true/false).
    """
    allowed: bool = Field(..., description="Nuevo valor de permiso")


class PermissionResponse(PermissionBase):
    """
    Schema para respuesta de permiso (GET).

    Incluye todos los campos de auditoría.
    """
    id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]
    deleted_by: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class PermissionListResponse(BaseModel):
    """Schema para respuesta de lista de permisos."""
    total: int
    items: List[PermissionResponse]

    model_config = ConfigDict(from_attributes=True)


# ==================== SCHEMAS PARA APP MÓVIL ====================


class EndpointInfo(BaseModel):
    """
    Información de un endpoint para mostrar en app móvil.

    Usado en auto-discovery de endpoints disponibles.
    """
    endpoint: str = Field(..., description="Ruta del endpoint")
    methods: List[str] = Field(..., description="Métodos HTTP disponibles")
    name: str = Field(..., description="Nombre del endpoint")
    tags: List[str] = Field(default=[], description="Tags del endpoint")
    description: Optional[str] = Field(None, description="Descripción del endpoint")


class AvailableEndpointsResponse(BaseModel):
    """
    Lista de todos los endpoints disponibles en el sistema.

    Usado por app móvil para construir UI dinámica de permisos.
    """
    total: int
    endpoints: List[EndpointInfo]


class PermissionsJSONResponse(BaseModel):
    """
    JSON completo de permisos de un usuario para app móvil.

    Estructura optimizada para renderizar checkboxes en app.

    Ejemplo:
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
            "/api/v1/individuals/with-user": {
                "POST": true
            }
        }
    }
    """
    user_id: int
    user_name: str
    role: int
    permissions: Dict[str, Dict[str, bool]] = Field(
        ...,
        description="Permisos agrupados por endpoint y método"
    )


class BulkPermissionUpdate(BaseModel):
    """
    Schema para actualización masiva de permisos desde app móvil.

    Permite que Admin actualice múltiples permisos en una sola llamada.

    Ejemplo:
    {
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
    """
    permissions: Dict[str, Dict[str, bool]] = Field(
        ...,
        description="Permisos a actualizar agrupados por endpoint y método"
    )

    @field_validator('permissions')
    @classmethod
    def validate_permissions_structure(cls, v: Dict) -> Dict:
        """Valida que la estructura del JSON sea correcta."""
        for endpoint, methods in v.items():
            if not endpoint.startswith('/api/'):
                raise ValueError(f"Endpoint '{endpoint}' debe comenzar con /api/")

            for method, allowed in methods.items():
                if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    raise ValueError(f"Método '{method}' no es válido")
                if not isinstance(allowed, bool):
                    raise ValueError(f"Valor de permiso debe ser boolean, recibido: {type(allowed)}")

        return v
