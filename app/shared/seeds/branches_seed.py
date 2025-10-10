"""
Seed: Branches

Datos de prueba para la entidad Branch.
Crea 6 sucursales distribuidas en 2 empresas.
"""
from sqlalchemy.orm import Session
from typing import Optional

from app.entities.branches.services.branch_service import BranchService


def seed_branches(db: Session, created_by_user_id: Optional[int] = None) -> None:
    """
    Crea sucursales de prueba si no existen.

    Args:
        db: Sesión de base de datos
        created_by_user_id: ID del usuario que crea los registros (para auditoría)
    """
    service = BranchService(db)

    # Verificar si ya existen branches
    existing = service.get_all_branches(skip=0, limit=1, active_only=False)
    if existing:
        print(f"[SEED] Branches ya existen ({len(existing)} registros). Omitiendo seed.")
        return

    # Datos de sucursales de prueba
    # Asumiendo:
    # - Company ID 1: Test Company
    # - Country ID 2: Mexico (MX)
    # - State IDs para México: 51-82 (32 estados)
    # - Country ID 1: United States (US)
    # - State IDs para USA: 1-50 (50 estados)

    branches = [
        # Company 1 - Sucursales en México
        {
            "company_id": 1,
            "country_id": 2,  # Mexico
            "state_id": 51,  # Aguascalientes (primer estado de México)
            "code": "AGS-01",
            "name": "Sucursal Aguascalientes Centro",
            "address": "Av. Tecnológico 123, Centro",
            "city": "Aguascalientes",
            "postal_code": "20000",
            "phone": "+52 449 123 4567",
            "email": "ags@testcompany.com",
            "description": "Sucursal principal en Aguascalientes"
        },
        {
            "company_id": 1,
            "country_id": 2,  # Mexico
            "state_id": 76,  # Jalisco
            "code": "GDL-01",
            "name": "Sucursal Guadalajara Centro",
            "address": "Av. Chapultepec 456, Col. Americana",
            "city": "Guadalajara",
            "postal_code": "44100",
            "phone": "+52 33 3456 7890",
            "email": "gdl@testcompany.com",
            "description": "Sucursal principal en Guadalajara"
        },
        {
            "company_id": 1,
            "country_id": 2,  # Mexico
            "state_id": 69,  # Ciudad de México
            "code": "CDMX-01",
            "name": "Sucursal CDMX Polanco",
            "address": "Av. Presidente Masaryk 789, Polanco",
            "city": "Ciudad de México",
            "postal_code": "11560",
            "phone": "+52 55 1234 5678",
            "email": "cdmx@testcompany.com",
            "description": "Oficina principal en la capital"
        },

        # Company 1 - Sucursales en USA
        {
            "company_id": 1,
            "country_id": 1,  # United States
            "state_id": 5,   # California (estimado)
            "code": "CA-01",
            "name": "San Francisco Office",
            "address": "123 Market Street, Downtown",
            "city": "San Francisco",
            "postal_code": "94102",
            "phone": "+1 415 555 1234",
            "email": "sf@testcompany.com",
            "description": "Main office in San Francisco"
        },

        # Sucursales para otra empresa (si existe Company ID 2 o más)
        # Se puede descomentar cuando haya más empresas
        # {
        #     "company_id": 2,
        #     "country_id": 2,
        #     "state_id": 64,  # Nuevo León
        #     "code": "MTY-01",
        #     "name": "Sucursal Monterrey",
        #     "address": "Av. Constitución 100, Centro",
        #     "city": "Monterrey",
        #     "postal_code": "64000",
        #     "phone": "+52 81 8765 4321",
        #     "email": "mty@company2.com",
        #     "description": "Oficina regional norte"
        # }
    ]

    created_count = 0
    for branch_data in branches:
        try:
            branch = service.create_branch(branch_data, created_by=created_by_user_id)
            created_count += 1
            print(f"[SEED] Branch creado: {branch.name} (code: {branch.code}, company_id: {branch.company_id})")
        except Exception as e:
            print(f"[SEED ERROR] No se pudo crear branch {branch_data['code']}: {str(e)}")
            continue

    print(f"[SEED] Branches seed completado: {created_count}/{len(branches)} branches creados")


def run_seed():
    """Función auxiliar para ejecutar el seed manualmente desde la línea de comandos."""
    from database import get_db

    db = next(get_db())
    try:
        seed_branches(db, created_by_user_id=1)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()