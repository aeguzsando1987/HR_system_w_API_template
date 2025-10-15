"""
Script para integrar Individual entity en main.py e init_db.py
Ejecutar: python integrate_individual.py
"""

# Paso 1: Agregar imports en main.py
print("Integrando Individual en main.py...")

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Agregar import del router
if "individual_router" not in content:
    content = content.replace(
        "from app.entities.positions.routers.position_router import router as position_router",
        "from app.entities.positions.routers.position_router import router as position_router\nfrom app.entities.individuals.routers.individual_router import router as individual_router"
    )
    print("✓ Import del router Individual agregado")

# Agregar import del modelo
if "from app.entities.individuals.models.individual import Individual" not in content:
    content = content.replace(
        "from app.entities.positions.models.position import Position",
        "from app.entities.positions.models.position import Position\nfrom app.entities.individuals.models.individual import Individual"
    )
    print("✓ Import del modelo Individual agregado")

# Agregar tag
if '"Individuals"' not in content:
    content = content.replace(
        '{"name": "Positions", "description": "Gestión de puestos/cargos con niveles jerárquicos"}',
        '{"name": "Positions", "description": "Gestión de puestos/cargos con niveles jerárquicos"},\n    {"name": "Individuals", "description": "Gestión de personas físicas (con o sin usuario)"}'
    )
    print("✓ Tag Individual agregado")

# Agregar router
if "app.include_router(individual_router)" not in content:
    content = content.replace(
        "app.include_router(position_router)",
        "app.include_router(position_router)\napp.include_router(individual_router)"
    )
    print("✓ Router Individual incluido")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✓ main.py actualizado exitosamente\n")

# Paso 2: Agregar seed en init_db.py
print("Integrando seed Individual en init_db.py...")

with open("app/shared/init_db.py", "r", encoding="utf-8") as f:
    init_content = f.read()

if "from app.shared.seeds.individuals_seed import seed_individuals" not in init_content:
    init_content = init_content.replace(
        "from app.shared.seeds.positions_seed import seed_positions",
        "from app.shared.seeds.positions_seed import seed_positions\nfrom app.shared.seeds.individuals_seed import seed_individuals"
    )
    print("✓ Import seed_individuals agregado")

if "seed_individuals(db, created_by_user_id=1)" not in init_content:
    init_content = init_content.replace(
        "seed_positions(db, created_by_user_id=1)",
        "seed_positions(db, created_by_user_id=1)\n    seed_individuals(db, created_by_user_id=1)"
    )
    print("✓ Llamada seed_individuals agregada")

with open("app/shared/init_db.py", "w", encoding="utf-8") as f:
    f.write(init_content)

print("✓ init_db.py actualizado exitosamente\n")

print("=" * 60)
print("INTEGRACIÓN COMPLETADA ✅")
print("=" * 60)
print("\nPróximos pasos:")
print("1. Matar servidores zombie: taskkill /F /IM python.exe")
print("2. Iniciar servidor: python main.py")
print("3. Obtener token: curl -X POST http://localhost:8001/token ...")
print("4. Probar endpoints Individual")