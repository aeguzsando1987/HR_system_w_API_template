"""
Seed data: Companies

Script para crear companies de prueba.
Ejecutar después de crear las tablas y seed de business_groups.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.entities.companies.models.company import Company
from app.entities.companies.services.company_service import CompanyService


def seed_companies(db: Session, created_by_user_id: Optional[int] = None) -> None:
    """
    Crea companies de prueba.

    Args:
        db: Sesión de base de datos
        created_by_user_id: ID del usuario que crea los registros

    Companies creadas: 4 total (2 por business_group)
    """
    existing_count = db.query(Company).filter(
        Company.is_active == True,
        Company.is_deleted == False
    ).count()
    if existing_count > 0:
        print(f"Ya existen {existing_count} companies activas. Omitiendo seed.")
        return

    service = CompanyService(db)

    companies = [
        # BusinessGroup 1 - Grupo Empresarial México (bg_id=1)
        {"business_group_id": 1, "code": "TECH-MX", "name": "TechCorp México",
         "legal_name": "TechCorp México S.A. de C.V.", "tax_id": "TECH900101XYZ",
         "industry": "Tecnología", "description": "Empresa de desarrollo de software"},

        {"business_group_id": 1, "code": "RETAIL-MX", "name": "RetailMax México",
         "legal_name": "RetailMax México S.A. de C.V.", "tax_id": "RETL900102ABC",
         "industry": "Retail", "description": "Cadena de tiendas departamentales"},

        # BusinessGroup 2 - Grupo Empresarial Global (bg_id=2)
        {"business_group_id": 2, "code": "SVC-GL", "name": "Global Services",
         "legal_name": "Global Services Inc.", "tax_id": "GLB900103DEF",
         "industry": "Servicios", "description": "Servicios empresariales internacionales"},

        {"business_group_id": 2, "code": "MFG-GL", "name": "Manufacturing Global",
         "legal_name": "Manufacturing Global Corp.", "tax_id": "MFG900104GHI",
         "industry": "Manufactura", "description": "Producción industrial"},
    ]

    created = 0
    for company_data in companies:
        try:
            service.create_company(company_data, created_by=created_by_user_id)
            created += 1
        except Exception as e:
            print(f"[SEED] Warning: {str(e)}")

    print(f"Seed completado: {created} companies creadas")


def run_seed():
    """Ejecuta el seed de forma standalone."""
    from database import get_db
    db = next(get_db())
    try:
        seed_companies(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
