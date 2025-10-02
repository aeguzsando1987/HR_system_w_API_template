"""
Script para truncar completamente la base de datos
"""
from database import Base, engine
from sqlalchemy import text

def truncate_database():
    print("Eliminando todas las tablas...")

    # Usar CASCADE para eliminar todas las dependencias
    with engine.connect() as conn:
        # Eliminar todas las tablas con CASCADE
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()

    print("Todas las tablas eliminadas exitosamente")
    print("Las tablas se recrearan automaticamente en el siguiente inicio del servidor")

if __name__ == "__main__":
    truncate_database()