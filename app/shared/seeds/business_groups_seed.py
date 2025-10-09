"""
Seed data: BusinessGroups

Script para crear datos de prueba de BusinessGroups.
Ejecutar después de crear las tablas.

IMPORTANTE: Usa el Service layer para garantizar que los campos de auditoría
(created_by, updated_by, deleted_by) se registren correctamente.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.entities.business_groups.models.business_group import BusinessGroup
from app.entities.business_groups.services.business_group_service import BusinessGroupService


def seed_business_groups(db: Session, created_by_user_id: Optional[int] = None) -> None:
    """
    Crea 2 BusinessGroups de prueba si no existen.

    Args:
        db: Sesión de base de datos
        created_by_user_id: ID del usuario que crea los registros (generalmente el admin)

    Esta función es idempotente: puede ejecutarse múltiples veces
    sin crear duplicados.
    """
    # Verificar si ya existen BusinessGroups ACTIVOS (no soft-deleted)
    existing_count = db.query(BusinessGroup).filter(
        BusinessGroup.is_active == True,
        BusinessGroup.is_deleted == False
    ).count()
    if existing_count > 0:
        print(f"Ya existen {existing_count} BusinessGroups activos. Omitiendo seed.")
        return

    # Limpiar registros soft-deleted para permitir recrear con mismos tax_ids
    deleted_records = db.query(BusinessGroup).filter(
        BusinessGroup.is_deleted == True
    ).all()
    if deleted_records:
        for record in deleted_records:
            db.delete(record)  # Hard delete de registros soft-deleted
        db.commit()
        print(f"[SEED] Limpiados {len(deleted_records)} registros soft-deleted para recrear seed")

    # Inicializar el servicio
    service = BusinessGroupService(db)

    # Crear BusinessGroups de prueba
    business_groups_data = [
        {
            "name": "Corporativo Global SA",
            "legal_name": "Corporativo Global Sociedad Anónima de Capital Variable",
            "tax_id": "CGS123456ABC",
            "description": "Grupo empresarial multinacional con presencia en América Latina y Europa. Especializado en tecnología y servicios financieros."
        },
        {
            "name": "Grupo Empresarial Regional",
            "legal_name": "Grupo Empresarial Regional S.A.",
            "tax_id": "GER789012DEF",
            "description": "Holding regional enfocado en manufactura, retail y logística en la región centroamericana."
        }
    ]

    business_groups_created = 0

    for bg_data in business_groups_data:
        # Usar el Service para crear (garantiza validaciones y campos de auditoría)
        service.create_business_group(bg_data, created_by=created_by_user_id)
        business_groups_created += 1

    print(f"Seed completado: {business_groups_created} BusinessGroups creados")
    print("- Corporativo Global SA (tax_id: CGS123456ABC)")
    print("- Grupo Empresarial Regional (tax_id: GER789012DEF)")
    if created_by_user_id:
        print(f"  Creados por user_id: {created_by_user_id}")


def run_seed():
    """
    Función auxiliar para ejecutar el seed de forma standalone.

    Uso:
        python -c "from app.shared.seeds.business_groups_seed import run_seed; run_seed()"
    """
    from database import get_db

    db = next(get_db())
    try:
        seed_business_groups(db)
        print("Seed de BusinessGroups ejecutado exitosamente")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
