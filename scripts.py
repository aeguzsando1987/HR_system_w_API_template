#!/usr/bin/env python
"""
CLI de Utilidades para FastAPI Template

Script consolidado para tareas comunes de desarrollo y administración.

Uso:
    python scripts.py genkey         - Generar claves seguras
    python scripts.py start          - Iniciar servidor
    python scripts.py restart        - Reiniciar servidor
    python scripts.py truncate       - Truncar base de datos (metodo seguro)
    python scripts.py truncate-hard  - Truncar base de datos (metodo alternativo)
    python scripts.py help           - Mostrar ayuda

Autor: E. Guzman
"""

import sys
import os
import secrets
import string
import subprocess
import time
import socket
from typing import Optional

# ==================== COMANDO: GENERAR CLAVES ====================

def generate_secret_key(length: int = 32) -> str:
    """Genera SECRET_KEY segura para JWT."""
    return secrets.token_urlsafe(length)


def generate_secure_password(length: int = 16) -> str:
    """Genera contraseña segura con caracteres alfanumericos y especiales."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_database_password(length: int = 20) -> str:
    """Genera contraseña para base de datos (sin caracteres especiales problematicos)."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def cmd_genkey():
    """Genera claves seguras para produccion."""
    print("=" * 60)
    print("GENERADOR DE CLAVES SEGURAS - API TEMPLATE")
    print("=" * 60)

    print("\nPARA ACTUALIZAR .env EN PRODUCCION:")
    print("-" * 40)

    secret_key = generate_secret_key(32)
    db_password = generate_database_password(20)
    admin_password = generate_secure_password(12)

    print(f"SECRET_KEY={secret_key}")
    print(f"DATABASE_URL=postgresql://postgres:{db_password}@localhost:5432/tu_db")
    print(f"DEFAULT_ADMIN_PASSWORD={admin_password}")

    print("\nIMPORTANTE:")
    print("   1. Guarda estas claves en un lugar seguro")
    print("   2. Nunca compartas el SECRET_KEY")
    print("   3. Cambia la contraseña de PostgreSQL en tu servidor")
    print("   4. Actualiza .env con estos valores")
    print("   5. Reinicia la aplicacion despues del cambio")

    print("\nDESARROLLO:")
    print("   Para desarrollo, puedes mantener los valores actuales")
    print("   Usa estas claves solo en PRODUCCION")

    print("\n" + "=" * 60)


# ==================== COMANDO: INICIAR SERVIDOR ====================

def find_free_port(start_port: int = 8000) -> Optional[int]:
    """Encuentra un puerto libre comenzando desde start_port."""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None


def kill_python_processes():
    """Mata todos los procesos Python."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe"],
            capture_output=True,
            text=True
        )
        print("Procesos Python terminados")
        time.sleep(2)
    except Exception as e:
        print(f"Error matando procesos: {e}")


def cmd_start():
    """Inicia el servidor en un puerto libre."""
    # Encontrar puerto libre
    port = find_free_port(8000)
    if not port:
        print("Error: No se encontro puerto libre")
        sys.exit(1)

    print(f"Puerto libre encontrado: {port}")
    print(f"Servidor estara disponible en: http://127.0.0.1:{port}")
    print(f"Swagger UI: http://127.0.0.1:{port}/docs")
    print("\nIniciando servidor...")

    try:
        subprocess.run([
            sys.executable, "-c",
            f"""
import uvicorn
from main import app
uvicorn.run(app, host='127.0.0.1', port={port})
"""
        ])
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario")


# ==================== COMANDO: REINICIAR SERVIDOR ====================

def cmd_restart():
    """Reinicia el servidor automaticamente."""
    print("Reiniciando servidor...")

    # Verificar si psutil esta disponible
    try:
        import psutil

        print("\nBuscando procesos Python en puerto 8001...")
        killed = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('main.py' in str(arg) for arg in cmdline):
                        print(f"   Matando proceso {proc.info['pid']}: {' '.join(cmdline)}")
                        proc.kill()
                        killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if killed > 0:
            print(f"OK: {killed} proceso(s) terminado(s)")
            time.sleep(2)
        else:
            print("OK: No hay procesos previos corriendo")

    except ImportError:
        print("Advertencia: psutil no disponible, usando metodo alternativo...")
        kill_python_processes()

    # Iniciar servidor nuevo
    print("\nIniciando servidor nuevo...")
    print("=" * 60)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario")
    except Exception as e:
        print(f"\nError al iniciar servidor: {e}")


# ==================== COMANDO: TRUNCAR BD ====================

def cmd_truncate():
    """Truncar base de datos usando metodo seguro (DROP SCHEMA CASCADE)."""
    try:
        from database import engine
        from sqlalchemy import text

        print("Advertencia: Esto eliminara TODAS las tablas de la base de datos")
        confirm = input("Escribe 'CONFIRMAR' para continuar: ")

        if confirm != "CONFIRMAR":
            print("Operacion cancelada")
            return

        print("\nEliminando todas las tablas...")

        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE;"))
            conn.execute(text("CREATE SCHEMA public;"))
            conn.commit()

        print("Todas las tablas eliminadas exitosamente")
        print("Las tablas se recrearan automaticamente en el siguiente inicio del servidor")
        print("\nEjecuta: python main.py")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_truncate_hard():
    """Truncar base de datos usando metodo alternativo (DROP TABLE por tabla)."""
    try:
        from sqlalchemy import create_engine, text
        import os
        from dotenv import load_dotenv

        load_dotenv()

        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/api_demo_db")

        print("Advertencia: Esto eliminara TODAS las tablas de la base de datos")
        print(f"Base de datos: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'N/A'}")
        confirm = input("Escribe 'CONFIRMAR' para continuar: ")

        if confirm != "CONFIRMAR":
            print("Operacion cancelada")
            return

        print("\nConectando a la base de datos...")
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

            print(f"Tablas encontradas: {len(tables)}")

            # Eliminar cada tabla
            for table in tables:
                print(f"  Eliminando {table}...")
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

            conn.commit()

            # Reactivar foreign keys
            conn.execute(text("SET session_replication_role = 'origin';"))
            conn.commit()

        print("Base de datos truncada exitosamente!")
        print("\nEjecuta: python main.py")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# ==================== COMANDO: AYUDA ====================

def cmd_help():
    """Muestra ayuda de comandos disponibles."""
    print(__doc__)


# ==================== MAIN ====================

def main():
    """Punto de entrada principal del CLI."""
    if len(sys.argv) < 2:
        cmd_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    commands = {
        'genkey': cmd_genkey,
        'start': cmd_start,
        'restart': cmd_restart,
        'truncate': cmd_truncate,
        'truncate-hard': cmd_truncate_hard,
        'help': cmd_help,
        '--help': cmd_help,
        '-h': cmd_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Error: Comando desconocido '{command}'")
        print("\nComandos disponibles:")
        print("  genkey         - Generar claves seguras")
        print("  start          - Iniciar servidor")
        print("  restart        - Reiniciar servidor")
        print("  truncate       - Truncar base de datos (metodo seguro)")
        print("  truncate-hard  - Truncar base de datos (metodo alternativo)")
        print("  help           - Mostrar ayuda")
        sys.exit(1)


if __name__ == "__main__":
    main()