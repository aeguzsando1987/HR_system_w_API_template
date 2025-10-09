"""
Seed data: UserScopes

Script para crear datos de prueba de UserScopes.
Ejecutar después de crear las tablas y BusinessGroups.

IMPORTANTE: Usa el Service layer para garantizar que los campos de auditoría
(created_by, updated_by, deleted_by) se registren correctamente.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.entities.user_scopes.models.user_scope import UserScope
from app.entities.user_scopes.services.user_scope_service import UserScopeService
from app.entities.user_scopes.schemas.enums import ScopeTypeEnum
from app.entities.business_groups.models.business_group import BusinessGroup


def seed_user_scopes(db: Session, created_by_user_id: Optional[int] = None) -> None:
    """
    Crea UserScopes de prueba si no existen.

    Este seed crea:
    1. UserScope para Admin con acceso a BusinessGroup específico (ejemplo)

    Args:
        db: Sesión de base de datos
        created_by_user_id: ID del usuario que crea los registros (generalmente el admin)

    Esta función es idempotente: puede ejecutarse múltiples veces
    sin crear duplicados.
    """
    # Verificar si ya existen UserScopes ACTIVOS (no soft-deleted)
    existing_count = db.query(UserScope).filter(
        UserScope.is_active == True,
        UserScope.is_deleted == False
    ).count()

    if existing_count > 0:
        print(f"Ya existen {existing_count} UserScopes activos. Omitiendo seed.")
        return

    # Limpiar registros soft-deleted para permitir recrear
    deleted_records = db.query(UserScope).filter(
        UserScope.is_deleted == True
    ).all()

    if deleted_records:
        for record in deleted_records:
            db.delete(record)  # Hard delete de registros soft-deleted
        db.commit()
        print(f"[SEED] Limpiados {len(deleted_records)} registros soft-deleted para recrear seed")

    # Obtener el BusinessGroup de ejemplo (el primero disponible)
    business_group = db.query(BusinessGroup).filter(
        BusinessGroup.is_active == True,
        BusinessGroup.is_deleted == False
    ).first()

    if not business_group:
        print("[SEED] No hay BusinessGroups disponibles. Primero ejecuta seed_business_groups.")
        return

    # Inicializar el servicio
    service = UserScopeService(db)

    # Obtener usuario admin (ID=1)
    from database import User
    admin_user = db.query(User).filter(User.id == 1).first()

    if not admin_user:
        print("[SEED] No se encontró usuario Admin (ID=1). No se pueden crear UserScopes.")
        return

    # Crear UserScopes de prueba
    user_scopes_data = [
        {
            "user_id": 1,  # Admin
            "scope_type": ScopeTypeEnum.BUSINESS_GROUP,
            "business_group_id": business_group.id,
            "company_id": None,
            "branch_id": None,
            "department_id": None
        }
    ]

    user_scopes_created = 0

    for scope_data in user_scopes_data:
        try:
            # Usar el Service para crear (garantiza validaciones y campos de auditoría)
            service.create_user_scope(
                scope_data,
                user_role=admin_user.role,
                created_by=created_by_user_id
            )
            user_scopes_created += 1
        except Exception as e:
            print(f"[SEED] Error al crear UserScope: {str(e)}")
            continue

    print(f"Seed completado: {user_scopes_created} UserScopes creados")
    print(f"- Admin (user_id=1) con scope BUSINESS_GROUP en '{business_group.name}' (ID={business_group.id})")
    if created_by_user_id:
        print(f"  Creados por user_id: {created_by_user_id}")


def run_seed():
    """
    Función auxiliar para ejecutar el seed de forma standalone.

    Uso:
        python -c "from app.shared.seeds.user_scopes_seed import run_seed; run_seed()"
    """
    from database import get_db

    db = next(get_db())
    try:
        seed_user_scopes(db)
        print("Seed de UserScopes ejecutado exitosamente")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
