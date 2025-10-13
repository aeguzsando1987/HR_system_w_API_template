"""
Seed: Departments

Datos de prueba para la entidad Department.
Incluye departamentos corporativos y de sucursal con jerarquia.
"""
from sqlalchemy.orm import Session
from typing import Optional

from app.entities.departments.services.department_service import DepartmentService


def seed_departments(db: Session, created_by_user_id: Optional[int] = None) -> None:
    """
    Crea departamentos de prueba si no existen.
    Incluye departamentos corporativos y de sucursal con jerarquia (padre-hijo).

    Args:
        db: Sesion de base de datos
        created_by_user_id: ID del usuario que crea los registros (para auditoria)
    """
    service = DepartmentService(db)

    # Verificar si ya existen departments
    existing = service.get_all_departments(skip=0, limit=1, active_only=False)
    if existing:
        print(f"[SEED] Departments ya existen ({len(existing)} registros). Omitiendo seed.")
        return

    # Datos de departamentos de prueba
    # Asumiendo:
    # - Company ID 1: Test Company
    # - Branch ID 1, 2: Branches de Test Company

    departments = [
        # DEPARTAMENTOS CORPORATIVOS (sin branch_id)
        {
            "company_id": 1,
            "branch_id": None,
            "parent_id": None,
            "code": "DIR-GEN",
            "name": "Direccion General",
            "description": "Direccion General de la empresa (corporativo)",
            "is_corporate": True
        },
        {
            "company_id": 1,
            "branch_id": None,
            "parent_id": None,  # Se actualizara despues de crear DIR-GEN
            "code": "FIN-CORP",
            "name": "Finanzas Corporativas",
            "description": "Departamento de finanzas a nivel corporativo",
            "is_corporate": True
        },
        {
            "company_id": 1,
            "branch_id": None,
            "parent_id": None,  # Se actualizara despues de crear DIR-GEN
            "code": "TI-CORP",
            "name": "Tecnologias de Informacion",
            "description": "Departamento de TI corporativo",
            "is_corporate": True
        },

        # DEPARTAMENTOS DE SUCURSAL (con branch_id)
        {
            "company_id": 1,
            "branch_id": 1,  # Sucursal 1
            "parent_id": None,
            "code": "VEN-SUC1",
            "name": "Ventas Sucursal 1",
            "description": "Departamento de ventas en sucursal 1",
            "is_corporate": False
        },
        {
            "company_id": 1,
            "branch_id": 1,
            "parent_id": None,
            "code": "OPS-SUC1",
            "name": "Operaciones Sucursal 1",
            "description": "Departamento de operaciones en sucursal 1",
            "is_corporate": False
        },
        {
            "company_id": 1,
            "branch_id": 2,  # Sucursal 2 (si existe)
            "parent_id": None,
            "code": "VEN-SUC2",
            "name": "Ventas Sucursal 2",
            "description": "Departamento de ventas en sucursal 2",
            "is_corporate": False
        },
    ]

    created_count = 0
    created_ids = {}

    # Fase 1: Crear departamentos raiz
    for dept_data in departments:
        try:
            dept = service.create_department(dept_data, created_by=created_by_user_id)
            created_count += 1
            created_ids[dept_data['code']] = dept.id
            print(f"[SEED] Department creado: {dept.name} (code: {dept.code}, id: {dept.id}, is_corporate: {dept.is_corporate})")
        except Exception as e:
            print(f"[SEED ERROR] No se pudo crear department {dept_data['code']}: {str(e)}")
            continue

    # Fase 2: Crear subdepartamentos (con parent_id)
    if "TI-CORP" in created_ids:
        subdepartments = [
            {
                "company_id": 1,
                "branch_id": None,
                "parent_id": created_ids["TI-CORP"],
                "code": "TI-DEV",
                "name": "Desarrollo de Software",
                "description": "Subdepartamento de desarrollo bajo TI",
                "is_corporate": True
            },
            {
                "company_id": 1,
                "branch_id": None,
                "parent_id": created_ids["TI-CORP"],
                "code": "TI-INFRA",
                "name": "Infraestructura",
                "description": "Subdepartamento de infraestructura bajo TI",
                "is_corporate": True
            },
        ]

        for subdept_data in subdepartments:
            try:
                subdept = service.create_department(subdept_data, created_by=created_by_user_id)
                created_count += 1
                print(f"[SEED] Subdepartment creado: {subdept.name} (code: {subdept.code}, parent_id: {subdept.parent_id})")
            except Exception as e:
                print(f"[SEED ERROR] No se pudo crear subdepartment {subdept_data['code']}: {str(e)}")
                continue

    print(f"[SEED] Departments seed completado: {created_count} departments creados")


def run_seed():
    """Funcion auxiliar para ejecutar el seed manualmente desde la linea de comandos."""
    from database import get_db

    db = next(get_db())
    try:
        seed_departments(db, created_by_user_id=1)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()