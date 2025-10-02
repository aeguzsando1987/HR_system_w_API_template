# -*- coding: utf-8 -*-
"""
Script para reiniciar el servidor automaticamente.
Mata procesos Python existentes y reinicia el servidor.
"""
import os
import sys
import subprocess
import time
import psutil

print("Reiniciando servidor...")

# 1. Matar procesos Python que esten usando el puerto 8001
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
    time.sleep(2)  # Esperar a que liberen el puerto
else:
    print("OK: No hay procesos previos corriendo")

# 2. Iniciar servidor nuevo
print("\nIniciando servidor nuevo...")
print("=" * 60)

# Cambiar al directorio del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Ejecutar main.py
try:
    subprocess.run([sys.executable, "main.py"], check=True)
except KeyboardInterrupt:
    print("\n\nServidor detenido por el usuario")
except Exception as e:
    print(f"\nError al iniciar servidor: {e}")