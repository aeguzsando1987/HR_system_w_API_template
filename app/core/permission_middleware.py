"""
Middleware de validación de permisos

Valida automáticamente los permisos de usuario antes de ejecutar endpoints.
Implementa el sistema de 3 capas: ROLE → SCOPE → PERMISSION
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db, User
from auth import verify_token
from app.core.permissions import has_permission
from app.core.endpoint_registry import normalize_endpoint


class PermissionMiddleware(BaseHTTPMiddleware):
    """
    Middleware que valida permisos granulares por endpoint.

    Flujo de validación:
    1. Verificar token JWT válido
    2. Obtener user_id del token
    3. Validar permiso con has_permission() (validación híbrida)
    4. Si no tiene permiso → 403 Forbidden
    5. Si tiene permiso → Continuar con el request

    Endpoints excluidos (no requieren validación de permisos):
    - /token (login)
    - /docs, /redoc, /openapi.json (documentación)
    - /health (health check)
    - Endpoints públicos específicos
    """

    def __init__(self, app):
        super().__init__(app)
        # Endpoints que NO requieren validación de permisos
        self.excluded_paths = [
            "/token",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]

    async def dispatch(self, request: Request, call_next):
        """
        Intercepta cada request y valida permisos antes de continuar.

        Args:
            request: Request de FastAPI
            call_next: Siguiente handler en la cadena

        Returns:
            Response del endpoint o error 403
        """
        # 1. Verificar si el endpoint está excluido
        if self._is_excluded_path(request.url.path):
            # No validar permisos, continuar
            return await call_next(request)

        # 2. Extraer token del header Authorization
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            # No hay token, dejar que FastAPI maneje con get_current_user
            return await call_next(request)

        token = authorization.replace("Bearer ", "")

        # 3. Verificar token y obtener user_id
        payload = verify_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token inválido o expirado"}
            )

        user_id = payload.get("user_id")
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token no contiene user_id"}
            )

        # 4. Obtener sesión de BD
        db: Session = next(get_db())

        try:
            # 5. Validar permiso granular
            endpoint = normalize_endpoint(request.url.path)
            method = request.method

            # Validación híbrida: específico → base route
            if not has_permission(db, user_id, endpoint, method):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": f"No tienes permiso para {method} {endpoint}",
                        "endpoint": endpoint,
                        "method": method
                    }
                )

            # 6. Permiso válido, continuar con el request
            response = await call_next(request)
            return response

        finally:
            db.close()

    def _is_excluded_path(self, path: str) -> bool:
        """
        Verifica si el path está en la lista de exclusiones.

        Args:
            path: Path del request

        Returns:
            True si está excluido, False si requiere validación
        """
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False


# ==================== USO DEL MIDDLEWARE ====================
# Para activar el middleware, agregar en main.py:
#
# from app.core.permission_middleware import PermissionMiddleware
# app.add_middleware(PermissionMiddleware)
#
# IMPORTANTE: Agregar DESPUÉS de crear la app pero ANTES de registrar routers
# ============================================================
