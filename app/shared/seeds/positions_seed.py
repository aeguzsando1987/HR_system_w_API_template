"""
Seed: Position

Datos de seed para Position.
"""
from sqlalchemy.orm import Session
from app.entities.positions.models.position import Position, HierarchyLevelEnum
from app.entities.positions.services.position_service import PositionService


def seed_positions(db: Session, created_by_user_id: int = None):
    """
    Seeds Position data usando Service layer.

    Args:
        db: Database session
        created_by_user_id: User ID para auditoria (usualmente admin)
    """
    # Verificar si ya existen positions activos
    existing_count = db.query(Position).filter(
        Position.is_active == True,
        Position.is_deleted == False
    ).count()

    if existing_count > 0:
        print(f"Ya existen {existing_count} Positions activos. Omitiendo seed.")
        return

    # Limpiar registros soft-deleted para permitir recrear
    deleted_records = db.query(Position).filter(
        Position.is_deleted == True
    ).all()

    if deleted_records:
        for record in deleted_records:
            db.delete(record)  # Hard delete
        db.commit()
        print(f"[SEED] Limpiados {len(deleted_records)} registros soft-deleted")

    # Inicializar service
    service = PositionService(db)

    # Seed data: 8 positions por company (24 total para 3 companies)
    positions_data = [
        # ==================== COMPANY 1 (8 positions) ====================
        {"company_id": 1, "title": "CEO", "level": "executive", "hierarchy_level": HierarchyLevelEnum.C_LEVEL, "hierarchy_weight": 0, "description": "Chief Executive Officer"},
        {"company_id": 1, "title": "Director de TI", "level": "director", "hierarchy_level": HierarchyLevelEnum.DIRECTOR, "hierarchy_weight": 15, "description": "Dirige el departamento de tecnologia"},
        {"company_id": 1, "title": "Director de Ventas", "level": "director", "hierarchy_level": HierarchyLevelEnum.DIRECTOR, "hierarchy_weight": 18, "description": "Dirige el departamento de ventas"},
        {"company_id": 1, "title": "Gerente de Desarrollo", "level": "manager", "hierarchy_level": HierarchyLevelEnum.MANAGER, "hierarchy_weight": 28, "description": "Gerente del area de desarrollo"},
        {"company_id": 1, "title": "Gerente de Ventas", "level": "manager", "hierarchy_level": HierarchyLevelEnum.MANAGER, "hierarchy_weight": 32, "description": "Gerente del area de ventas"},
        {"company_id": 1, "title": "Desarrollador Senior", "level": "senior", "hierarchy_level": HierarchyLevelEnum.SENIOR, "hierarchy_weight": 65, "description": "Desarrollador de software senior"},
        {"company_id": 1, "title": "Desarrollador Junior", "level": "junior", "hierarchy_level": HierarchyLevelEnum.JUNIOR, "hierarchy_weight": 85, "description": "Desarrollador de software junior"},
        {"company_id": 1, "title": "Practicante", "level": "trainee", "hierarchy_level": HierarchyLevelEnum.TRAINEE, "hierarchy_weight": 95, "description": "Practicante profesional"},

        # ==================== COMPANY 2 (8 positions) ====================
        {"company_id": 2, "title": "Presidente", "level": "executive", "hierarchy_level": HierarchyLevelEnum.C_LEVEL, "hierarchy_weight": 2, "description": "Presidente de la compania"},
        {"company_id": 2, "title": "Director de Operaciones", "level": "director", "hierarchy_level": HierarchyLevelEnum.DIRECTOR, "hierarchy_weight": 15, "description": "Dirige operaciones"},
        {"company_id": 2, "title": "Director Financiero", "level": "director", "hierarchy_level": HierarchyLevelEnum.DIRECTOR, "hierarchy_weight": 12, "description": "CFO de la compania"},
        {"company_id": 2, "title": "Gerente de Produccion", "level": "manager", "hierarchy_level": HierarchyLevelEnum.MANAGER, "hierarchy_weight": 30, "description": "Gerente de linea de produccion"},
        {"company_id": 2, "title": "Coordinador de Logistica", "level": "coordinator", "hierarchy_level": HierarchyLevelEnum.COORDINATOR, "hierarchy_weight": 45, "description": "Coordina logistica y distribucion"},
        {"company_id": 2, "title": "Especialista en Calidad", "level": "specialist", "hierarchy_level": HierarchyLevelEnum.SPECIALIST, "hierarchy_weight": 55, "description": "Especialista en control de calidad"},
        {"company_id": 2, "title": "Operador de Maquinaria", "level": "intermediate", "hierarchy_level": HierarchyLevelEnum.INTERMEDIATE, "hierarchy_weight": 75, "description": "Opera maquinaria industrial"},
        {"company_id": 2, "title": "Auxiliar de Almacen", "level": "junior", "hierarchy_level": HierarchyLevelEnum.JUNIOR, "hierarchy_weight": 88, "description": "Auxiliar en almacen"},
    ]

    # Crear positions usando service
    created_count = 0
    for position_data in positions_data:
        try:
            service.create_position(position_data, created_by=created_by_user_id)
            created_count += 1
        except Exception as e:
            print(f"[SEED] Error al crear position '{position_data.get('title')}': {str(e)}")

    print(f"Seed completado: {created_count}/{len(positions_data)} Positions creados")
    if created_by_user_id:
        print(f"  Creados por user_id: {created_by_user_id}")