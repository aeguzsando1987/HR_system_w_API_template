import subprocess
import time
import socket
import sys

def find_free_port(start_port=8000):
    """Encuentra un puerto libre comenzando desde start_port"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def kill_python_processes():
    """Mata todos los procesos Python"""
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe"],
            capture_output=True,
            text=True
        )
        print("Procesos Python terminados")
        time.sleep(2)
    except Exception as e:
        print(f"Error matando procesos: {e}")

def start_server(port):
    """Inicia el servidor en el puerto especificado"""
    print(f"Iniciando servidor en puerto {port}...")
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
        print("Servidor detenido por el usuario")

if __name__ == "__main__":
    # Matar procesos existentes
    kill_python_processes()

    # Encontrar puerto libre
    port = find_free_port(8000)
    if not port:
        print("No se encontró puerto libre")
        sys.exit(1)

    print(f"Puerto libre encontrado: {port}")
    print(f"Servidor estará disponible en: http://127.0.0.1:{port}")
    print(f"Swagger UI: http://127.0.0.1:{port}/docs")

    # Iniciar servidor
    start_server(port)