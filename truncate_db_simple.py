"""
Script simple para truncar la base de datos.
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:root@localhost:5432/api_demo_db"

print("Conectando a la base de datos...")
engine = create_engine(DATABASE_URL)

print("Eliminando todas las tablas...")
with engine.connect() as conn:
    # Desactivar foreign keys
    conn.execute(text("SET session_replication_role = 'replica';"))
    conn.commit()

    # Obtener todas las tablas
    result = conn.execute(text("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
    """))
    tables = [row[0] for row in result]

    print(f"Tablas encontradas: {tables}")

    # Eliminar cada tabla
    for table in tables:
        print(f"  Eliminando {table}...")
        conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

    conn.commit()

    # Reactivar foreign keys
    conn.execute(text("SET session_replication_role = 'origin';"))
    conn.commit()

print("Base de datos truncada!")
print("Ahora ejecuta: python main.py")