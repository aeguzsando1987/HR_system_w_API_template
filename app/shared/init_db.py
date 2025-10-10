"""
Inicializacion de Base de Datos

Script que se ejecuta al startup de la aplicacion para:
1. Crear tablas si no existen
2. Cargar datos iniciales de paises y estados
"""
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from database import Base, engine
from app.shared.data.countries_states_data import COUNTRIES_STATES_DATA
from app.entities.countries.models.country import Country
from app.entities.states.models.state import State
from app.shared.seeds.business_groups_seed import seed_business_groups
from app.shared.seeds.companies_seed import seed_companies
from app.shared.seeds.branches_seed import seed_branches


def table_exists(table_name: str) -> bool:
    """Verifica si una tabla existe en la base de datos."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def initialize_database(db: Session):
    """
    Inicializa la base de datos con tablas y datos base.

    Esta funcion es idempotente: puede ejecutarse multiples veces sin duplicar datos.
    """
    print("Inicializando base de datos...")

    # 1. Crear tablas si no existen
    if not table_exists("countries") or not table_exists("states"):
        print("Creando tablas de base de datos...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente")
    else:
        print("Tablas ya existen")

    # 2. Verificar si ya existen datos
    existing_countries = db.query(Country).count()
    if existing_countries > 0:
        print(f"Base de datos ya contiene {existing_countries} paises. Omitiendo seed.")
        return

    # 3. Cargar datos de paises y estados
    print("Cargando datos de paises y estados...")

    countries_created = 0
    states_created = 0

    for country_key, country_data in COUNTRIES_STATES_DATA.items():
        # Crear pais
        country = Country(
            name=country_data["name"],
            iso_code_2=country_data["iso_code_2"],
            iso_code_3=country_data["iso_code_3"],
            numeric_code=country_data.get("numeric_code"),
            phone_code=country_data.get("phone_code"),
            currency_code=country_data.get("currency_code"),
            currency_name=country_data.get("currency_name"),
            is_active=True
        )
        db.add(country)
        db.flush()  # Para obtener el ID del pais
        countries_created += 1

        # Crear estados del pais
        for state_data in country_data["states"]:
            state = State(
                name=state_data["name"],
                code=state_data["code"],
                country_id=country.id,
                is_active=True
            )
            db.add(state)
            states_created += 1

    # Commit de todos los cambios
    db.commit()

    print(f"Se crearon {countries_created} paises")
    print(f"Se crearon {states_created} estados/provincias/departamentos")

    # 4. Cargar datos de Business Groups, Companies y Branches
    print("\nCargando datos de Business Groups, Companies y Branches...")
    seed_business_groups(db, created_by_user_id=1)
    seed_companies(db, created_by_user_id=1)
    seed_branches(db, created_by_user_id=1)

    print("Inicializacion de base de datos completada")


def seed_countries_states(db: Session):
    """
    Funcion alternativa para cargar solo datos de paises/estados
    sin crear tablas.
    """
    existing_countries = db.query(Country).count()
    if existing_countries > 0:
        print(f"Ya existen {existing_countries} paises. No se cargaran datos.")
        return

    countries_created = 0
    states_created = 0

    for country_key, country_data in COUNTRIES_STATES_DATA.items():
        country = Country(
            name=country_data["name"],
            iso_code_2=country_data["iso_code_2"],
            iso_code_3=country_data["iso_code_3"],
            numeric_code=country_data.get("numeric_code"),
            phone_code=country_data.get("phone_code"),
            currency_code=country_data.get("currency_code"),
            currency_name=country_data.get("currency_name"),
            is_active=True
        )
        db.add(country)
        db.flush()
        countries_created += 1

        for state_data in country_data["states"]:
            state = State(
                name=state_data["name"],
                code=state_data["code"],
                country_id=country.id,
                is_active=True
            )
            db.add(state)
            states_created += 1

    db.commit()
    print(f"Seed completado: {countries_created} paises, {states_created} estados")