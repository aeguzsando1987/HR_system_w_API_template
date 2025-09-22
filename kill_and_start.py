import os
import subprocess
import time
import sys

def kill_python_processes():
    try:
        # Matar todos los procesos python
        subprocess.run(["taskkill", "/f", "/im", "python.exe"],
                      capture_output=True, check=False)
        print("Procesos Python terminados")
        time.sleep(2)
    except Exception as e:
        print(f"Error matando procesos: {e}")

def start_server():
    print("Iniciando servidor...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("Servidor detenido por el usuario")
    except Exception as e:
        print(f"Error iniciando servidor: {e}")

if __name__ == "__main__":
    kill_python_processes()
    start_server()