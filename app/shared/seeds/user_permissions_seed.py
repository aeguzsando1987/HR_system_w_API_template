"""
Seed data: UserPermissions

Script para crear permisos de prueba para usuarios de demostración.
Ejecutar después de crear las tablas y seed de usuarios.

IMPORTANTE: Usa el Service layer para garantizar validaciones.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.entities.user_permissions.models.user_permission import UserPermission
from app.entities.user_permissions.services.user_permission_service import UserPermissionService


def seed_user_permissions(db: Session, created_by_user_id: Optional[int] = None) -> None:
    """
    Crea permisos de prueba para usuarios demo.

    Args:
        db: Sesión de base de datos
        created_by_user_id: ID del usuario que crea los registros (generalmente el admin)

    Esta función es idempotente: puede ejecutarse múltiples veces
    sin crear duplicados.

    Permisos creados:
    - Admin (user_id=1): Todos los permisos
    - Gerente demo (user_id=2): Permisos limitados
    - Gestor demo (user_id=3): Permisos muy limitados
    """
    # Verificar si ya existen permisos ACTIVOS
    existing_count = db.query(UserPermission).filter(
        UserPermission.is_active == True,
        UserPermission.is_deleted == False
    ).count()
    if existing_count > 0:
        print(f"Ya existen {existing_count} permisos activos. Omitiendo seed.")
        return

    # Limpiar registros soft-deleted para permitir recrear
    deleted_records = db.query(UserPermission).filter(
        UserPermission.is_deleted == True
    ).all()
    if deleted_records:
        for record in deleted_records:
            db.delete(record)  # Hard delete
        db.commit()
        print(f"[SEED] Limpiados {len(deleted_records)} registros soft-deleted")

    # Inicializar el servicio
    service = UserPermissionService(db)

    # ==================== ADMIN (user_id=1) - TODOS LOS PERMISOS ====================
    admin_permissions = [
        # Business Groups
        {"user_id": 1, "endpoint": "/api/v1/business-groups", "method": "GET", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/business-groups", "method": "POST", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/business-groups", "method": "PUT", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/business-groups", "method": "DELETE", "allowed": True},

        # User Scopes
        {"user_id": 1, "endpoint": "/api/v1/user-scopes", "method": "GET", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/user-scopes", "method": "POST", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/user-scopes", "method": "PUT", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/user-scopes", "method": "DELETE", "allowed": True},

        # User Permissions
        {"user_id": 1, "endpoint": "/api/v1/permissions", "method": "GET", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/permissions", "method": "POST", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/permissions", "method": "PUT", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/permissions", "method": "DELETE", "allowed": True},

        # Admin Permissions
        {"user_id": 1, "endpoint": "/api/v1/admin/permissions", "method": "GET", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/admin/permissions", "method": "PUT", "allowed": True},

        # Persons
        {"user_id": 1, "endpoint": "/api/v1/persons", "method": "GET", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/persons", "method": "POST", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/persons", "method": "PUT", "allowed": True},
        {"user_id": 1, "endpoint": "/api/v1/persons", "method": "DELETE", "allowed": True},
    ]

    # ==================== GERENTE DEMO (user_id=2) - PERMISOS LIMITADOS ====================
    manager_permissions = [
        # Business Groups - Solo lectura
        {"user_id": 2, "endpoint": "/api/v1/business-groups", "method": "GET", "allowed": True},
        {"user_id": 2, "endpoint": "/api/v1/business-groups", "method": "POST", "allowed": False},
        {"user_id": 2, "endpoint": "/api/v1/business-groups", "method": "PUT", "allowed": False},
        {"user_id": 2, "endpoint": "/api/v1/business-groups", "method": "DELETE", "allowed": False},

        # User Scopes - Solo lectura
        {"user_id": 2, "endpoint": "/api/v1/user-scopes", "method": "GET", "allowed": True},
        {"user_id": 2, "endpoint": "/api/v1/user-scopes", "method": "POST", "allowed": False},
        {"user_id": 2, "endpoint": "/api/v1/user-scopes", "method": "PUT", "allowed": False},
        {"user_id": 2, "endpoint": "/api/v1/user-scopes", "method": "DELETE", "allowed": False},

        # Persons - CRUD completo
        {"user_id": 2, "endpoint": "/api/v1/persons", "method": "GET", "allowed": True},
        {"user_id": 2, "endpoint": "/api/v1/persons", "method": "POST", "allowed": True},
        {"user_id": 2, "endpoint": "/api/v1/persons", "method": "PUT", "allowed": True},
        {"user_id": 2, "endpoint": "/api/v1/persons", "method": "DELETE", "allowed": True},
    ]

    # ==================== GESTOR DEMO (user_id=3) - PERMISOS MUY LIMITADOS ====================
    supervisor_permissions = [
        # Business Groups - Solo lectura
        {"user_id": 3, "endpoint": "/api/v1/business-groups", "method": "GET", "allowed": True},
        {"user_id": 3, "endpoint": "/api/v1/business-groups", "method": "POST", "allowed": False},

        # Persons - Solo lectura y creación
        {"user_id": 3, "endpoint": "/api/v1/persons", "method": "GET", "allowed": True},
        {"user_id": 3, "endpoint": "/api/v1/persons", "method": "POST", "allowed": True},
        {"user_id": 3, "endpoint": "/api/v1/persons", "method": "PUT", "allowed": False},
        {"user_id": 3, "endpoint": "/api/v1/persons", "method": "DELETE", "allowed": False},
    ]

    # Crear permisos
    permissions_created = 0

    all_permissions = admin_permissions + manager_permissions + supervisor_permissions

    for perm_data in all_permissions:
        try:
            service.create_permission(perm_data, created_by=created_by_user_id)
            permissions_created += 1
        except Exception as e:
            # Si ya existe, continuar
            print(f"[SEED] Warning: {str(e)}")
            continue

    print(f"Seed completado: {permissions_created} permisos creados")
    print(f"  - Admin (user_id=1): {len(admin_permissions)} permisos")
    print(f"  - Gerente (user_id=2): {len(manager_permissions)} permisos")
    print(f"  - Gestor (user_id=3): {len(supervisor_permissions)} permisos")
    if created_by_user_id:
        print(f"  Creados por user_id: {created_by_user_id}")


def run_seed():
    """
    Función auxiliar para ejecutar el seed de forma standalone.

    Uso:
        python -c "from app.shared.seeds.user_permissions_seed import run_seed; run_seed()"
    """
    from database import get_db

    db = next(get_db())
    try:
        seed_user_permissions(db)
        print("Seed de UserPermissions ejecutado exitosamente")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
