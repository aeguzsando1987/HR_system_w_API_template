"""
Endpoint Registry - Auto-Discovery y Normalización de Endpoints

Sistema de auto-descubrimiento de endpoints desde FastAPI.
NO requiere editar código al agregar nuevas entidades.

Funciones principales:
1. discover_endpoints_from_app() - Auto-descubre todos los endpoints
2. normalize_endpoint() - Normaliza rutas para validación híbrida
3. get_endpoint_metadata() - Metadata opcional para UI
"""

from typing import List, Dict, Optional
from fastapi import FastAPI
from fastapi.routing import APIRoute


def discover_endpoints_from_app(app: FastAPI) -> List[Dict]:
    """
    Auto-descubre todos los endpoints registrados en FastAPI.

    Extrae automáticamente la lista de endpoints al consultar app.routes.
    Útil para que app móvil construya UI dinámica de permisos.

    Args:
        app: Instancia de FastAPI

    Returns:
        Lista de diccionarios con info de cada endpoint:
        [
            {
                "endpoint": "/api/v1/employees",
                "methods": ["GET", "POST"],
                "name": "list_employees",
                "tags": ["Employees"]
            },
            ...
        ]

    Ejemplo:
        endpoints = discover_endpoints_from_app(app)
        # Retorna TODOS los endpoints, incluyendo especiales:
        # - /api/v1/employees
        # - /api/v1/individuals/with-user
        # - /api/v1/employees/{id}/upload-photo
    """
    endpoints = []
    seen = set()  # Evitar duplicados

    for route in app.routes:
        if isinstance(route, APIRoute):
            # Filtrar solo rutas API (excluir /docs, /openapi.json, /health)
            if route.path.startswith("/api/"):
                # Crear clave única para evitar duplicados
                key = (route.path, tuple(sorted(route.methods)))

                if key not in seen:
                    seen.add(key)

                    endpoints.append({
                        "endpoint": route.path,
                        "methods": sorted(list(route.methods)),  # GET, POST, etc.
                        "name": route.name,
                        "tags": list(route.tags) if route.tags else [],
                        "description": route.summary if hasattr(route, 'summary') else None
                    })

    # Ordenar por endpoint para UI consistente
    endpoints.sort(key=lambda x: x["endpoint"])

    return endpoints


def normalize_endpoint(path: str) -> str:
    """
    Normaliza endpoint para validación híbrida.

    Convierte rutas específicas a ruta base para permitir permisos generales.

    Ejemplos:
        /api/v1/employees/123        → /api/v1/employees
        /api/v1/employees/           → /api/v1/employees
        /api/v1/individuals/with-user → /api/v1/individuals
        /api/v1/employees/{id}/photo  → /api/v1/employees

    Args:
        path: Ruta completa del endpoint

    Returns:
        Ruta base normalizada (primeros 4 segmentos)

    Uso en validación híbrida:
        1. Buscar permiso ESPECÍFICO: /api/v1/individuals/with-user
        2. Si no existe, buscar BASE: /api/v1/individuals
    """
    # Remover trailing slash
    path = path.rstrip('/')

    # Dividir por /
    parts = path.split("/")

    # Retornar primeros 4 segmentos: /api/v1/entity
    if len(parts) >= 4:
        return "/".join(parts[:4])

    return path


def is_normalized_endpoint(path: str) -> bool:
    """
    Verifica si un endpoint ya está normalizado (es ruta base).

    Args:
        path: Ruta del endpoint

    Returns:
        True si es ruta base, False si es específica

    Ejemplos:
        /api/v1/employees         → True (ruta base)
        /api/v1/employees/123     → False (ruta específica)
        /api/v1/individuals/with-user → False (ruta específica)
    """
    path = path.rstrip('/')
    parts = path.split("/")

    # Ruta base tiene exactamente 4 segmentos: /api/v1/entity
    return len(parts) == 4


def get_endpoint_metadata(endpoint_path: str) -> Dict:
    """
    Retorna metadata opcional de un endpoint para UI mejorada.

    Metadata definida manualmente para mejorar UX en app móvil.
    NO ES REQUERIDO - Si no existe metadata, usa defaults.

    Args:
        endpoint_path: Ruta del endpoint

    Returns:
        Diccionario con metadata:
        {
            "display_name": "Gestión de Empleados",
            "description": "CRUD completo de empleados",
            "icon": "👥",
            "category": "Recursos Humanos"
        }

    Uso:
        metadata = get_endpoint_metadata("/api/v1/employees")
        # App móvil usa metadata["icon"] para mostrar icono
    """
    # Metadata opcional (agregar según necesidad)
    ENDPOINT_METADATA = {
        "/api/v1/employees": {
            "display_name": "Gestión de Empleados",
            "description": "CRUD completo de empleados",
            "icon": "👥",
            "category": "Recursos Humanos"
        },
        "/api/v1/business-groups": {
            "display_name": "Grupos Empresariales",
            "description": "Gestión de grupos empresariales",
            "icon": "🏢",
            "category": "Organización"
        },
        "/api/v1/user-scopes": {
            "display_name": "Scopes de Usuario",
            "description": "Ámbitos de acceso organizacional",
            "icon": "🗺️",
            "category": "Permisos"
        },
        "/api/v1/individuals": {
            "display_name": "Individuales",
            "description": "Gestión de personas individuales",
            "icon": "👤",
            "category": "Recursos Humanos"
        },
        "/api/v1/individuals/with-user": {
            "display_name": "Crear Individual con Usuario",
            "description": "Crea Individual + User en una transacción",
            "icon": "👤➕",
            "category": "Recursos Humanos",
            "is_special": True
        }
    }

    # Retornar metadata si existe, sino defaults
    return ENDPOINT_METADATA.get(endpoint_path, {
        "display_name": endpoint_path.split("/")[-1].replace("-", " ").title(),
        "description": "Endpoint estándar",
        "icon": "📌",
        "category": "General"
    })


def group_endpoints_by_entity(endpoints: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Agrupa endpoints por entidad para UI organizada.

    Útil para app móvil que muestra permisos agrupados por sección.

    Args:
        endpoints: Lista de endpoints (de discover_endpoints_from_app)

    Returns:
        Diccionario agrupado por entidad:
        {
            "employees": [
                {"endpoint": "/api/v1/employees", "methods": ["GET", "POST"]},
                {"endpoint": "/api/v1/employees/{id}", "methods": ["PUT", "DELETE"]}
            ],
            "individuals": [
                {"endpoint": "/api/v1/individuals", "methods": ["GET"]},
                {"endpoint": "/api/v1/individuals/with-user", "methods": ["POST"]}
            ]
        }

    Ejemplo en app móvil:
        grouped = group_endpoints_by_entity(endpoints)
        for entity, entity_endpoints in grouped.items():
            render_section(entity)
            for ep in entity_endpoints:
                render_checkboxes(ep)
    """
    grouped = {}

    for endpoint in endpoints:
        # Extraer entidad de la ruta: /api/v1/employees → employees
        parts = endpoint["endpoint"].split("/")
        if len(parts) >= 4:
            entity = parts[3]  # employees, individuals, business-groups, etc.

            if entity not in grouped:
                grouped[entity] = []

            grouped[entity].append(endpoint)

    return grouped


def filter_special_endpoints(endpoints: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """
    Separa endpoints estándar de endpoints especiales.

    Útil para app móvil con modo simple/avanzado.

    Args:
        endpoints: Lista de endpoints

    Returns:
        Tupla (endpoints_estandar, endpoints_especiales)

    Ejemplo:
        standard, special = filter_special_endpoints(endpoints)
        # standard: [/api/v1/employees, /api/v1/individuals]
        # special: [/api/v1/individuals/with-user, /api/v1/employees/{id}/photo]
    """
    standard = []
    special = []

    for endpoint in endpoints:
        path = endpoint["endpoint"]

        # Es especial si tiene más de 4 segmentos
        if not is_normalized_endpoint(path):
            special.append(endpoint)
        else:
            standard.append(endpoint)

    return standard, special
