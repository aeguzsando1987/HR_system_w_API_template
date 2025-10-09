"""
Sistema de Permisos Basado en Scopes

Funciones auxiliares para verificar permisos basados en UserScope.
Este módulo permite control granular de acceso a recursos.

NOTA: Algunas funciones relacionadas con Employee están implementadas como
placeholders ya que la entidad Employee no existe aún. Se implementarán
completamente cuando se cree la entidad Employee.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.entities.user_scopes.models.user_scope import UserScope
from app.entities.user_scopes.schemas.enums import ScopeTypeEnum


def get_user_scopes(db: Session, user_id: int, active_only: bool = True) -> List[UserScope]:
    """
    Obtiene todos los scopes activos de un usuario.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        active_only: Si True, solo retorna scopes activos

    Returns:
        Lista de UserScopes del usuario
    """
    query = db.query(UserScope).filter(
        UserScope.user_id == user_id,
        UserScope.is_deleted == False
    )

    if active_only:
        query = query.filter(UserScope.is_active == True)

    return query.all()


def user_has_global_access(db: Session, user_id: int) -> bool:
    """
    Verifica si un usuario tiene acceso GLOBAL (sin scopes).

    Los usuarios Admin (role=1) pueden tener acceso global,
    lo cual significa que NO tienen ningún UserScope asignado
    o tienen acceso total a toda la organización.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        True si el usuario tiene acceso global, False en caso contrario
    """
    # Verificar si el usuario es Admin
    from database import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != 1:  # Solo Admin puede tener acceso global
        return False

    # Si no tiene scopes, tiene acceso global
    scopes = get_user_scopes(db, user_id, active_only=True)
    return len(scopes) == 0


def user_has_access_to_business_group(
    db: Session,
    user_id: int,
    business_group_id: int
) -> bool:
    """
    Verifica si un usuario tiene acceso a un BusinessGroup específico.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        business_group_id: ID del BusinessGroup

    Returns:
        True si tiene acceso, False en caso contrario
    """
    # Acceso global tiene acceso a todo
    if user_has_global_access(db, user_id):
        return True

    # Verificar si tiene scope específico para este BusinessGroup
    scope = db.query(UserScope).filter(
        UserScope.user_id == user_id,
        UserScope.scope_type == ScopeTypeEnum.BUSINESS_GROUP,
        UserScope.business_group_id == business_group_id,
        UserScope.is_active == True,
        UserScope.is_deleted == False
    ).first()

    return scope is not None


def get_accessible_business_group_ids(db: Session, user_id: int) -> Optional[List[int]]:
    """
    Obtiene los IDs de BusinessGroups a los que tiene acceso un usuario.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        Lista de IDs de BusinessGroups, o None si tiene acceso global (todos)
    """
    # Si tiene acceso global, retornar None (significa "todos")
    if user_has_global_access(db, user_id):
        return None

    # Obtener scopes de BusinessGroup
    scopes = db.query(UserScope).filter(
        UserScope.user_id == user_id,
        UserScope.scope_type == ScopeTypeEnum.BUSINESS_GROUP,
        UserScope.business_group_id.isnot(None),
        UserScope.is_active == True,
        UserScope.is_deleted == False
    ).all()

    return [scope.business_group_id for scope in scopes if scope.business_group_id]


# ==================== PLACEHOLDERS PARA EMPLOYEE ====================
# Las siguientes funciones se implementarán completamente cuando
# se cree la entidad Employee.

def can_access_employee(db: Session, user_id: int, employee_id: int) -> bool:
    """
    PLACEHOLDER: Verifica si un usuario puede acceder a un Employee específico.

    Esta función se implementará completamente cuando se cree la entidad Employee.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        employee_id: ID del Employee

    Returns:
        True (por ahora, siempre retorna True como placeholder)
    """
    # TODO: Implementar cuando Employee exista
    # Lógica propuesta:
    # 1. Si tiene acceso global, retornar True
    # 2. Si tiene scope BUSINESS_GROUP, verificar que Employee pertenezca a ese BusinessGroup
    # 3. Si tiene scope COMPANY, verificar que Employee pertenezca a esa Company
    # 4. Si tiene scope BRANCH, verificar que Employee pertenezca a ese Branch
    # 5. Si tiene scope DEPARTMENT, verificar que Employee pertenezca a ese Department
    return True


def filter_employees_by_scope(db: Session, user_id: int):
    """
    PLACEHOLDER: Retorna un query filtrado de Employees según el scope del usuario.

    Esta función se implementará completamente cuando se cree la entidad Employee.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        Query filtrado (por ahora, retorna None como placeholder)
    """
    # TODO: Implementar cuando Employee exista
    # Lógica propuesta:
    # 1. Si tiene acceso global, retornar query sin filtros
    # 2. Si tiene scopes específicos, filtrar Employee por business_group_id, company_id, etc.
    # 3. Usar OR para combinar múltiples scopes
    return None


def can_create_employee_in_scope(
    db: Session,
    user_id: int,
    business_group_id: Optional[int] = None,
    company_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    department_id: Optional[int] = None
) -> bool:
    """
    PLACEHOLDER: Verifica si un usuario puede crear un Employee en un scope específico.

    Esta función se implementará completamente cuando se cree la entidad Employee.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        business_group_id: ID del BusinessGroup (opcional)
        company_id: ID de la Company (opcional)
        branch_id: ID del Branch (opcional)
        department_id: ID del Department (opcional)

    Returns:
        True (por ahora, siempre retorna True como placeholder)
    """
    # TODO: Implementar cuando Employee exista
    # Lógica propuesta:
    # 1. Si tiene acceso global, retornar True
    # 2. Verificar que el usuario tenga scope sobre al menos uno de los IDs proporcionados
    return True


def can_edit_employee(db: Session, user_id: int, employee_id: int) -> bool:
    """
    PLACEHOLDER: Verifica si un usuario puede editar un Employee específico.

    Esta función se implementará completamente cuando se cree la entidad Employee.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        employee_id: ID del Employee

    Returns:
        True (por ahora, siempre retorna True como placeholder)
    """
    # TODO: Implementar cuando Employee exista
    # Por ahora, reutilizar la lógica de can_access_employee
    return can_access_employee(db, user_id, employee_id)


def can_delete_employee(db: Session, user_id: int, employee_id: int) -> bool:
    """
    PLACEHOLDER: Verifica si un usuario puede eliminar un Employee específico.

    Esta función se implementará completamente cuando se cree la entidad Employee.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        employee_id: ID del Employee

    Returns:
        True (por ahora, siempre retorna True como placeholder)
    """
    # TODO: Implementar cuando Employee exista
    # Por ahora, reutilizar la lógica de can_access_employee
    return can_access_employee(db, user_id, employee_id)


# ==================== SISTEMA HÍBRIDO: PERMISSIONS (CAPA 3) ====================
# Funciones para validación granular de permisos por endpoint.
# Sistema de 3 capas: ROLE → SCOPE → PERMISSION

def has_permission(
    db: Session,
    user_id: int,
    endpoint: str,
    method: str
) -> bool:
    """
    Valida si un usuario tiene permiso para un endpoint y método HTTP.

    **Validación Híbrida** (búsqueda en orden):
    1. Busca permiso ESPECÍFICO: /api/v1/individuals/with-user
    2. Si no existe, busca permiso BASE: /api/v1/individuals

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        endpoint: Ruta del endpoint (/api/v1/employees)
        method: Método HTTP (GET, POST, PUT, DELETE, PATCH)

    Returns:
        True si tiene permiso, False si no

    Ejemplo:
        # Ana hace POST /api/v1/individuals/with-user
        if has_permission(db, 2, "/api/v1/individuals/with-user", "POST"):
            # ✅ Permitir
    """
    from app.entities.user_permissions.repositories.user_permission_repository import UserPermissionRepository
    from app.core.endpoint_registry import normalize_endpoint

    repo = UserPermissionRepository(db)

    # 1. Buscar permiso ESPECÍFICO primero
    specific_permission = repo.get_permission(user_id, endpoint, method)
    if specific_permission:
        return specific_permission.allowed

    # 2. Si no hay específico, buscar permiso BASE
    normalized_endpoint = normalize_endpoint(endpoint)
    if normalized_endpoint != endpoint:  # Solo si es diferente
        base_permission = repo.get_permission(user_id, normalized_endpoint, method)
        if base_permission:
            return base_permission.allowed

    # 3. Si no existe ningún permiso, denegar por defecto
    return False


def get_user_permissions_json(db: Session, user_id: int) -> dict:
    """
    Genera JSON completo de permisos de un usuario para app móvil.

    Estructura optimizada para renderizar checkboxes en app.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        Diccionario con estructura:
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

    Ejemplo:
        json_perms = get_user_permissions_json(db, 2)
        # App móvil usa este JSON para construir UI de checkboxes
    """
    from database import User
    from app.entities.user_permissions.repositories.user_permission_repository import UserPermissionRepository

    # Obtener usuario
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"user_id": user_id, "error": "Usuario no encontrado"}

    # Obtener permisos
    repo = UserPermissionRepository(db)
    permissions = repo.get_by_user_id(user_id, active_only=True)

    # Construir estructura agrupada por endpoint
    permissions_dict = {}
    for perm in permissions:
        if perm.endpoint not in permissions_dict:
            permissions_dict[perm.endpoint] = {}
        permissions_dict[perm.endpoint][perm.method] = perm.allowed

    return {
        "user_id": user.id,
        "user_name": user.name,
        "role": user.role,
        "permissions": permissions_dict
    }


def bulk_update_permissions(
    db: Session,
    user_id: int,
    permissions: dict,
    updated_by: int
) -> bool:
    """
    Actualización masiva de permisos desde app móvil.

    Proceso:
    1. Elimina (soft delete) todos los permisos existentes del usuario
    2. Crea nuevos permisos según el JSON recibido

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a actualizar
        permissions: Diccionario con estructura:
            {
                "/api/v1/employees": {"GET": true, "POST": true, "DELETE": false},
                "/api/v1/individuals/with-user": {"POST": true}
            }
        updated_by: ID del usuario que actualiza (Admin)

    Returns:
        True si exitoso, False si error

    Ejemplo:
        # Admin actualiza permisos de Ana desde app móvil
        new_perms = {
            "/api/v1/employees": {"GET": True, "POST": True}
        }
        bulk_update_permissions(db, 2, new_perms, updated_by=1)
    """
    from app.entities.user_permissions.repositories.user_permission_repository import UserPermissionRepository

    try:
        repo = UserPermissionRepository(db)

        # 1. Limpiar permisos existentes (soft delete)
        repo.bulk_delete_by_user(user_id, deleted_by=updated_by)

        # 2. Crear nuevos permisos
        permissions_to_create = []
        for endpoint, methods in permissions.items():
            for method, allowed in methods.items():
                permissions_to_create.append({
                    "user_id": user_id,
                    "endpoint": endpoint,
                    "method": method,
                    "allowed": allowed
                })

        if permissions_to_create:
            repo.bulk_create(permissions_to_create, created_by=updated_by)

        return True

    except Exception as e:
        db.rollback()
        print(f"Error en bulk_update_permissions: {str(e)}")
        return False


def validate_endpoint_exists(app, endpoint: str) -> bool:
    """
    Valida que un endpoint exista en la aplicación FastAPI.

    Usado en validación al crear permisos para evitar endpoints inexistentes.

    Args:
        app: Instancia de FastAPI
        endpoint: Ruta del endpoint (/api/v1/employees)

    Returns:
        True si existe, False si no

    Ejemplo:
        if not validate_endpoint_exists(app, "/api/v1/fake-endpoint"):
            raise ValueError("Endpoint no existe")
    """
    from app.core.endpoint_registry import discover_endpoints_from_app

    endpoints = discover_endpoints_from_app(app)
    existing_endpoints = [ep["endpoint"] for ep in endpoints]

    return endpoint in existing_endpoints
