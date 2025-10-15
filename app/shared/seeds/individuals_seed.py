"""
Seed data para Individuals
"""
from sqlalchemy.orm import Session
from datetime import date
from app.entities.individuals.models.individual import Individual
from auth import hash_password


def seed_individuals(db: Session, created_by_user_id: int = 1):
    """
    Crea 10 Individuals de prueba:
    - 5 con user_id asociado (usuarios del sistema)
    - 5 sin user_id (personas sin cuenta)
    """
    print("Seeding Individuals...")

    # Verificar si ya existen individuals
    existing_count = db.query(Individual).count()
    if existing_count > 0:
        print(f"Base de datos ya contiene {existing_count} individuals. Omitiendo seed.")
        return

    # Necesitamos obtener IDs de Countries y States existentes
    from app.entities.countries.models.country import Country
    from app.entities.states.models.state import State

    # Obtener países (asumiendo que ya fueron seeded)
    mexico = db.query(Country).filter(Country.name == "Mexico").first()
    colombia = db.query(Country).filter(Country.name == "Colombia").first()
    argentina = db.query(Country).filter(Country.name == "Argentina").first()

    # Obtener algunos states (si existen)
    cdmx_state = db.query(State).filter(State.name.ilike("%Ciudad de México%")).first()
    jalisco_state = db.query(State).filter(State.name.ilike("%Jalisco%")).first()

    # IDs por defecto si no se encuentran
    mexico_id = mexico.id if mexico else 1
    colombia_id = colombia.id if colombia else 2
    argentina_id = argentina.id if argentina else 3
    cdmx_state_id = cdmx_state.id if cdmx_state else None
    jalisco_state_id = jalisco_state.id if jalisco_state else None

    # ==================== INDIVIDUALS CON USER ====================

    individuals_data = [
        # 1. Individual con User (Admin - ya existe en sistema)
        {
            "first_name": "Carlos",
            "last_name": "Administrador",
            "email": "carlos.admin@empresa.com",
            "phone": "+52-555-1001",
            "mobile": "+52-555-1002",
            "document_type": "INE",
            "document_number": "CAAD900101HDFRRL01",
            "curp": "CAAD900101HDFRRL01",
            "birth_date": date(1990, 1, 1),
            "gender": "M",
            "address": "Av. Reforma 123, CDMX",
            "country_id": mexico_id,
            "state_id": cdmx_state_id,
            "payroll_number": "EMP001",
            "marital_status": "Married",
            "emergency_contact_name": "María Administrador",
            "emergency_contact_phone": "+52-555-9001",
            "emergency_contact_relation": "Spouse",
            "user_id": 1,  # Usuario admin existente
            "is_active": True,
            "created_by": created_by_user_id
        },

        # 2. Individual con User (Manager)
        {
            "first_name": "Ana",
            "last_name": "García Pérez",
            "email": "ana.garcia@empresa.com",
            "phone": "+52-555-2001",
            "mobile": "+52-555-2002",
            "document_type": "INE",
            "document_number": "GAPA850215MDFRRN02",
            "curp": "GAPA850215MDFRRN02",
            "birth_date": date(1985, 2, 15),
            "gender": "F",
            "address": "Calle Juárez 456, Guadalajara",
            "country_id": mexico_id,
            "state_id": jalisco_state_id,
            "payroll_number": "EMP002",
            "marital_status": "Single",
            "emergency_contact_name": "Luis García",
            "emergency_contact_phone": "+52-555-9002",
            "emergency_contact_relation": "Father",
            "user_id": None,  # Se crearía con endpoint with-user
            "is_active": True,
            "created_by": created_by_user_id
        },

        # 3. Individual con User (Collaborator)
        {
            "first_name": "Miguel",
            "last_name": "Rodríguez López",
            "email": "miguel.rodriguez@empresa.com",
            "phone": "+52-555-3001",
            "mobile": "+52-555-3002",
            "document_type": "CURP",
            "curp": "ROLM920530HDGDPG03",
            "birth_date": date(1992, 5, 30),
            "gender": "M",
            "address": "Col. Roma Norte, CDMX",
            "country_id": mexico_id,
            "state_id": cdmx_state_id,
            "payroll_number": "EMP003",
            "marital_status": "Domestic Partnership",
            "emergency_contact_name": "Laura Martínez",
            "emergency_contact_phone": "+52-555-9003",
            "emergency_contact_relation": "Partner",
            "user_id": None,
            "is_active": True,
            "created_by": created_by_user_id
        },

        # 4. Individual Colombia (con pasaporte)
        {
            "first_name": "Sofía",
            "last_name": "Martínez Gómez",
            "email": "sofia.martinez@empresa.com",
            "phone": "+57-1-4001",
            "mobile": "+57-300-4002",
            "document_type": "CC",
            "document_number": "52345678",
            "birth_date": date(1988, 7, 20),
            "gender": "F",
            "address": "Calle 100, Bogotá",
            "country_id": colombia_id,
            "state_id": None,
            "payroll_number": "EMP004",
            "marital_status": "Married",
            "emergency_contact_name": "Juan Martínez",
            "emergency_contact_phone": "+57-300-9004",
            "emergency_contact_relation": "Spouse",
            "user_id": None,
            "is_active": True,
            "created_by": created_by_user_id
        },

        # 5. Individual Argentina
        {
            "first_name": "Diego",
            "last_name": "Fernández Silva",
            "email": "diego.fernandez@empresa.com",
            "phone": "+54-11-5001",
            "mobile": "+54-9-11-5002",
            "document_type": "DNI",
            "document_number": "38765432",
            "birth_date": date(1995, 11, 10),
            "gender": "M",
            "address": "Av. Corrientes 1234, Buenos Aires",
            "country_id": argentina_id,
            "state_id": None,
            "payroll_number": "EMP005",
            "marital_status": "Single",
            "emergency_contact_name": "Rosa Fernández",
            "emergency_contact_phone": "+54-9-11-9005",
            "emergency_contact_relation": "Mother",
            "user_id": None,
            "is_active": True,
            "created_by": created_by_user_id
        },

        # ==================== INDIVIDUALS SIN USER ====================

        # 6. Individual sin User (mínimos campos)
        {
            "first_name": "Laura",
            "last_name": "Sánchez Torres",
            "email": "laura.sanchez@personal.com",
            "phone": "+52-555-6001",
            "is_active": True,
            "created_by": created_by_user_id
        },

        # 7. Individual sin User (con documento pero sin CURP)
        {
            "first_name": "Roberto",
            "last_name": "Jiménez Morales",
            "email": "roberto.jimenez@personal.com",
            "phone": "+52-555-7001",
            "mobile": "+52-555-7002",
            "document_type": "IFE",
            "document_number": "JIMR880412HDFJMB04",
            "birth_date": date(1988, 4, 12),
            "gender": "M",
            "country_id": mexico_id,
            "is_active": True,
            "created_by": created_by_user_id
        },

        # 8. Individual sin User (con todos los campos opcionales)
        {
            "first_name": "Patricia",
            "last_name": "Hernández Ruiz",
            "email": "patricia.hernandez@personal.com",
            "phone": "+52-555-8001",
            "mobile": "+52-555-8002",
            "document_type": "INE",
            "document_number": "HERP870925MDFRRT05",
            "curp": "HERP870925MDFRRT05",
            "birth_date": date(1987, 9, 25),
            "gender": "F",
            "address": "Colonia Del Valle, CDMX",
            "photo_url": "https://example.com/photos/patricia.jpg",
            "country_id": mexico_id,
            "state_id": cdmx_state_id,
            "payroll_number": "EMP008",
            "marital_status": "Divorced",
            "emergency_contact_name": "Carmen Ruiz",
            "emergency_contact_phone": "+52-555-9008",
            "emergency_contact_relation": "Sister",
            "is_active": True,
            "created_by": created_by_user_id
        },

        # 9. Individual sin User (Colombia, sin documento)
        {
            "first_name": "Andrés",
            "last_name": "Castro Vargas",
            "email": "andres.castro@personal.com",
            "phone": "+57-1-9001",
            "mobile": "+57-300-9002",
            "birth_date": date(1993, 3, 8),
            "gender": "M",
            "country_id": colombia_id,
            "marital_status": "Single",
            "is_active": True,
            "created_by": created_by_user_id
        },

        # 10. Individual sin User (joven, 18 años)
        {
            "first_name": "Valeria",
            "last_name": "Moreno Cruz",
            "email": "valeria.moreno@personal.com",
            "phone": "+52-555-1000",
            "mobile": "+52-555-1001",
            "curp": "MOCV060814MDFRRL06",
            "birth_date": date(2006, 8, 14),  # 18 años
            "gender": "F",
            "country_id": mexico_id,
            "marital_status": "Single",
            "emergency_contact_name": "Sandra Cruz",
            "emergency_contact_phone": "+52-555-9010",
            "emergency_contact_relation": "Mother",
            "is_active": True,
            "created_by": created_by_user_id
        }
    ]

    # Insertar individuals
    for data in individuals_data:
        individual = Individual(**data)
        db.add(individual)

    try:
        db.commit()
        print(f"✓ {len(individuals_data)} Individuals creados exitosamente")
    except Exception as e:
        db.rollback()
        print(f"✗ Error al crear Individuals: {str(e)}")
        raise e