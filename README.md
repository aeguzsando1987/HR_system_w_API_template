# FastAPI Template - Sistema Completo de Autenticación y Entidades

Template FastAPI profesional con autenticación JWT, sistema de roles, arquitectura modular y configuración híbrida. Listo para usar en producción.
Esta plantilla permite crear un sistema completo con autenticación, roles, arquitectura modular y configuración híbrida. Una buena base para crear aplicativos con bases de datos relacionales que requieran funciones CRUD para registros de personas, clientes, proveedores, libros, peliculas, etc. El limite esta en las especificaciones del sistema que se busque desarrollar.

## Características Principales

- **Autenticación JWT** con OAuth2 integrado en Swagger
- **Sistema de Roles** de 5 niveles (Admin, Gerente, Colaborador, Lector, Guest)
- **Arquitectura Modular** para agregar nuevas entidades sin modificar el core
- **Configuración Híbrida** con soporte .env y fallbacks automáticos
- **Base de Datos PostgreSQL** con relaciones y transacciones atómicas
- **Soft Delete** y campos de auditoría
- **Documentación Automática** con Swagger UI y ReDoc

## Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- Git

## Instalación Paso a Paso

### 1. Copiar el Template

```bash
# Opción A: Clonar repositorio
git clone <url-del-repositorio> mi-nuevo-proyecto
cd mi-nuevo-proyecto

# Opción B: Copiar archivos manualmente
# Copiar toda la carpeta del template a tu nuevo directorio de proyecto
```

### 2. Crear Ambiente Virtual

```bash
# Crear ambiente virtual
python -m venv venv

# Activar ambiente virtual
# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

```bash
# Crear base de datos en PostgreSQL
psql -U postgres
CREATE DATABASE mi_proyecto_db;
\q
```

### 5. Configurar Variables de Entorno

```bash
# Editar archivo .env con tus configuraciones
# El template incluye valores por defecto que funcionan sin .env
```

**Archivo .env (opcional - el template funciona sin él):**
```env
# Configuración de la Aplicación
APP_NAME=Mi Proyecto API
VERSION=1.0.0
DEBUG=true

# Base de datos PostgreSQL
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/mi_proyecto_db

# JWT Security (generar con generate_secret_key.py)
SECRET_KEY=tu-clave-secreta-super-segura-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Admin por defecto
DEFAULT_ADMIN_EMAIL=admin@tuempresa.com
DEFAULT_ADMIN_PASSWORD=tu_password_seguro

# Servidor
HOST=0.0.0.0
PORT=8000
```

### 6. Generar Claves Seguras para Producción

```bash
python generate_secret_key.py
```

### 7. Ejecutar la Aplicación

```bash
python main.py
```

### 8. Verificar Instalación

Abrir en el navegador:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Usuario Admin por Defecto

- **Email:** admin@bapta.com.mx
- **Contraseña:** root

## Probar la API

1. Ir a http://localhost:8000/docs
2. Hacer click en **"Authorize"**
3. Usar credenciales del admin
4. Probar cualquier endpoint

## Agregar Nueva Entidad: Ejemplo "Persona"

### Paso 1: Crear Estructura de Módulo

```bash
mkdir -p modules/personas
```

### Paso 2: Crear Archivo `modules/personas/__init__.py`

```python
from .routes import router

__all__ = ["router"]
```

### Paso 3: Crear Modelo `modules/personas/models.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Campos específicos de Persona
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    birth_date = Column(DateTime, nullable=True)

    # Campos de control
    status = Column(String, default="active")
    is_active = Column(Boolean, default=True)

    # Campos de auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relaciones
    user = relationship("User", foreign_keys=[user_id])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
```

### Paso 4: Crear Esquemas `modules/personas/schemas.py`

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PersonaBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[datetime] = None
    status: str = "active"

class PersonaCreate(PersonaBase):
    user_id: Optional[int] = None

class PersonaUpdate(BaseModel):
    user_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[datetime] = None
    status: Optional[str] = None

class PersonaWithUserCreate(BaseModel):
    # Datos del usuario
    user_email: str
    user_name: str
    user_password: str
    user_role: int = 4

    # Datos de la persona
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[datetime] = None
    status: str = "active"

class PersonaResponse(PersonaBase):
    id: int
    user_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Paso 5: Crear Rutas `modules/personas/routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, User
from auth import require_any_user, require_collaborator_or_better, require_manager_or_admin, require_admin, hash_password
from .models import Persona
from .schemas import PersonaCreate, PersonaUpdate, PersonaWithUserCreate, PersonaResponse

router = APIRouter(prefix="/personas", tags=["personas"])

@router.post("/", response_model=PersonaResponse)
def create_persona(
    persona_data: PersonaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_collaborator_or_better)
):
    # Validar usuario si se proporciona user_id
    if persona_data.user_id and persona_data.user_id > 0:
        user = db.query(User).filter(User.id == persona_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

    persona = Persona(**persona_data.dict())
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona

@router.get("/", response_model=List[PersonaResponse])
def get_personas(
    db: Session = Depends(get_db),
    current_user = Depends(require_any_user)
):
    personas = db.query(Persona).filter(Persona.is_active == True).all()
    return personas

@router.get("/{persona_id}", response_model=PersonaResponse)
def get_persona(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_any_user)
):
    persona = db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.is_active == True
    ).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

@router.put("/{persona_id}", response_model=PersonaResponse)
def update_persona(
    persona_id: int,
    persona_data: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_collaborator_or_better)
):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # Validar user_id si se está actualizando
    if persona_data.user_id is not None:
        if persona_data.user_id == 0:
            persona_data.user_id = None
        elif persona_data.user_id > 0:
            user = db.query(User).filter(User.id == persona_data.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar campos
    update_data = persona_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(persona, field, value)

    persona.updated_by = current_user.id
    db.commit()
    db.refresh(persona)
    return persona

@router.delete("/{persona_id}")
def delete_persona(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    persona.is_active = False
    persona.updated_by = current_user.id
    db.commit()
    return {"message": "Persona eliminada exitosamente"}

@router.post("/with-user")
def create_persona_with_user(
    data: PersonaWithUserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_manager_or_admin)
):
    # Verificar si el email ya existe
    if db.query(User).filter(User.email == data.user_email).first():
        raise HTTPException(status_code=400, detail="Email ya existe")

    try:
        # Transacción atómica: crear usuario y persona
        user = User(
            email=data.user_email,
            name=data.user_name,
            password_hash=hash_password(data.user_password),
            role=data.user_role
        )
        db.add(user)
        db.flush()  # Obtener el ID sin hacer commit

        persona = Persona(
            user_id=user.id,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            address=data.address,
            birth_date=data.birth_date,
            status=data.status
        )
        db.add(persona)

        db.commit()
        db.refresh(user)
        db.refresh(persona)

        return {
            "message": "Usuario y persona creados exitosamente",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            },
            "persona": {
                "id": persona.id,
                "first_name": persona.first_name,
                "last_name": persona.last_name,
                "user_id": persona.user_id
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear usuario y persona: {str(e)}")
```

### Paso 6: Integrar en la Aplicación Principal

Editar `main.py`:

```python
# Agregar import del modelo para crear tablas
from modules.personas.models import Persona

# Agregar import del router
from modules.personas import router as personas_router

# Incluir el router en la aplicación
app.include_router(personas_router)

# Agregar tag en la configuración de FastAPI
openapi_tags=[
    # ... tags existentes ...
    {"name": "personas", "description": "Gestión de personas"},
]
```

### Paso 7: Probar la Nueva Entidad

```bash
# Reiniciar la aplicación
python main.py
```

Ir a http://localhost:8000/docs y verificar que aparezcan los nuevos endpoints:

- `POST /personas/` - Crear persona
- `GET /personas/` - Listar personas
- `GET /personas/{persona_id}` - Obtener persona específica
- `PUT /personas/{persona_id}` - Actualizar persona
- `DELETE /personas/{persona_id}` - Eliminar persona (soft delete)
- `POST /personas/with-user` - **Crear persona con usuario asociado**

## Endpoints Disponibles

### Autenticación
- `POST /token` - Obtener token OAuth2
- `POST /login` - Login alternativo

### Usuarios
- `POST /users` - Crear usuario
- `GET /users` - Listar usuarios
- `GET /users/me` - Perfil actual
- `GET /users/{user_id}` - Usuario específico
- `PUT /users/{user_id}` - Actualizar usuario
- `DELETE /users/{user_id}` - Eliminar usuario

### Personas (Ejemplo de Nueva Entidad)
- `POST /personas/` - Crear persona
- `GET /personas/` - Listar personas
- `GET /personas/{persona_id}` - Obtener persona
- `PUT /personas/{persona_id}` - Actualizar persona
- `DELETE /personas/{persona_id}` - Eliminar persona
- `POST /personas/with-user` -  **Crear persona + usuario**

### Sistema
- `GET /health` - Estado del sistema

## Sistema de Permisos y Roles - Guía Completa

### Jerarquía de Roles (Menor número = Mayor poder)

| Rol | Nivel | Nombre | Descripción | Permisos |
|-----|-------|--------|-------------|----------|
| 1 | **Admin** | Administrador | Acceso total al sistema | Crear/Leer/Actualizar/Eliminar todo |
| 2 | **Gerente** | Manager | Gestión de usuarios y entidades | CRUD usuarios y entidades, NO eliminar usuarios |
| 3 | **Colaborador** | Collaborator | Gestión de entidades | CRUD entidades, NO gestión de usuarios |
| 4 | **Lector** | Reader | Solo lectura | Solo ver entidades, NO crear/modificar |
| 5 | **Guest** | Invitado | Acceso limitado | Acceso muy restringido |

### Funciones de Permisos Disponibles

En `auth.py` tenemos estas funciones listas para usar:

```python
# Funciones de autorización por roles
require_admin()                    # Solo Admin (role=1)
require_manager_or_admin()         # Gerente o Admin (role<=2)
require_collaborator_or_better()   # Colaborador o superior (role<=3)
require_any_user()                 # Cualquier usuario autenticado (role<=5)
require_role(minimum_role)         # Función genérica con rol mínimo
```

### Matriz de Permisos por Endpoint

#### Usuarios (`/users`)
| Endpoint | Admin (1) | Gerente (2) | Colaborador (3) | Lector (4) | Guest (5) |
|----------|-----------|-------------|-----------------|------------|-----------|
| `POST /users` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `GET /users` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `GET /users/me` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /users/{id}` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `PUT /users/{id}` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `DELETE /users/{id}` | ✅ | ❌ | ❌ | ❌ | ❌ |

#### Entidades (`/examples`, `/personas`)
| Endpoint | Admin (1) | Gerente (2) | Colaborador (3) | Lector (4) | Guest (5) |
|----------|-----------|-------------|-----------------|------------|-----------|
| `POST /entidad` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `GET /entidad` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /entidad/{id}` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `PUT /entidad/{id}` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `DELETE /entidad/{id}` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `POST /entidad/with-user` | ✅ | ✅ | ❌ | ❌ | ❌ |

### 🔧 Cómo Implementar Permisos en Nuevas Entidades

#### Ejemplo Práctico: Endpoint con Permisos

```python
from auth import require_collaborator_or_better, require_admin, require_any_user

# Solo Colaborador o superior puede crear
@router.post("/productos/")
def create_producto(
    producto_data: ProductoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_collaborator_or_better)  # Roles 1,2,3
):
    # Lógica del endpoint...

# Cualquier usuario autenticado puede leer
@router.get("/productos/")
def get_productos(
    db: Session = Depends(get_db),
    current_user = Depends(require_any_user)  # Roles 1,2,3,4,5
):
    # Lógica del endpoint...

# Solo Admin puede eliminar
@router.delete("/productos/{id}")
def delete_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)  # Solo role=1
):
    # Lógica del endpoint...
```

###  Recomendaciones de Permisos por Operación

#### **CREATE (Crear)**
```python
# Para entidades normales
current_user = Depends(require_collaborator_or_better)  # Roles 1,2,3

# Para operaciones sensibles (crear usuarios)
current_user = Depends(require_manager_or_admin)  # Roles 1,2
```

#### **READ (Leer)**
```python
# Para datos públicos de la empresa
current_user = Depends(require_any_user)  # Roles 1,2,3,4,5

# Para datos sensibles (lista de usuarios)
current_user = Depends(require_manager_or_admin)  # Roles 1,2
```

#### **UPDATE (Actualizar)**
```python
# Para entidades normales
current_user = Depends(require_collaborator_or_better)  # Roles 1,2,3

# Para usuarios/configuraciones
current_user = Depends(require_manager_or_admin)  # Roles 1,2
```

#### **DELETE (Eliminar)**
```python
# Para soft delete de entidades
current_user = Depends(require_admin)  # Solo role=1

# Para eliminación permanente
current_user = Depends(require_admin)  # Solo role=1
```

### Función Genérica para Casos Especiales

```python
from auth import require_role

# Ejemplo: Solo niveles 1 y 2 pueden acceder
@router.post("/reportes-financieros/")
def create_reporte_financiero(
    current_user = Depends(require_role(2))  # Admin(1) y Gerente(2)
):
    # Lógica del endpoint...

# Ejemplo: Solo nivel 1 (Admin) puede configurar sistema
@router.put("/configuracion-sistema/")
def update_configuracion(
    current_user = Depends(require_role(1))  # Solo Admin(1)
):
    # Lógica del endpoint...
```

### Errores Comunes y Soluciones

#### **Error Común**: Usar números incorrectos
```python
# INCORRECTO - Los números altos NO tienen más permisos
current_user = Depends(require_role(5))  # ¡Solo Guests!

# CORRECTO - Los números bajos tienen más permisos
current_user = Depends(require_role(2))  # Admin y Gerente
```

#### **Error Común**: No considerar la jerarquía
```python
# INCORRECTO - Excluye al Admin
if current_user.role == 2:  # Solo Gerente

# CORRECTO - Incluye Admin y Gerente
if current_user.role <= 2:  # Admin(1) y Gerente(2)
```

### Probar Permisos

#### 1. Crear usuarios de prueba con diferentes roles:

```python
# Via API o script
admin_user = {"email": "admin@test.com", "role": 1}
manager_user = {"email": "manager@test.com", "role": 2}
collaborator_user = {"email": "colaborador@test.com", "role": 3}
reader_user = {"email": "lector@test.com", "role": 4}
```

#### 2. Probar cada endpoint con diferentes usuarios

#### 3. Verificar respuestas esperadas:
- **200/201**: Usuario tiene permisos
- **403**: Usuario no tiene permisos suficientes
- **401**: Usuario no está autenticado

### Consejos de Seguridad

1. **Principio de menor privilegio**: Dar el mínimo rol necesario
2. **Validar en el backend**: Nunca confiar solo en el frontend
3. **Auditoría**: Usar campos `updated_by` para tracking
4. **Roles granulares**: Crear roles específicos si necesitas más control

### Flujo de Autenticación y Autorización

```
1. Cliente envía request → 2. ¿Token válido?
   ↓ No: Error 401
3. Obtener usuario del token → 4. ¿Usuario activo?
   ↓ No: Error 403
5. Verificar rol del usuario → 6. ¿Rol suficiente?
   ↓ No: Error 403
7. Ejecutar endpoint
```

Este sistema de permisos te permite controlar granularmente quién puede hacer qué en tu aplicación, manteniendo la seguridad y escalabilidad.

## Crear Nuevos Endpoints - Guía Práctica

### Ejemplo: Endpoint de Reportes de Ventas

Vamos a crear un endpoint que genere reportes de ventas con diferentes niveles de acceso según el rol del usuario.

#### Paso 1: Agregar el Endpoint al Router Existente

En `modules/personas/routes.py` (o crear un nuevo módulo):

```python
from datetime import datetime, timedelta
from typing import Optional

# Esquema para el reporte
class ReporteVentasRequest(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    incluir_detalles: bool = False

class ReporteVentasResponse(BaseModel):
    periodo: str
    total_ventas: float
    cantidad_transacciones: int
    vendedor_top: Optional[str] = None
    detalles: Optional[list] = None

# Endpoint básico - Solo lectura de resumen
@router.get("/reportes/ventas/resumen", response_model=ReporteVentasResponse)
def get_resumen_ventas(
    db: Session = Depends(get_db),
    current_user = Depends(require_any_user)  # Cualquier usuario puede ver resumen
):
    # Lógica para generar resumen básico de ventas
    return {
        "periodo": "Último mes",
        "total_ventas": 150000.00,
        "cantidad_transacciones": 45,
        "vendedor_top": "Juan Pérez"
    }

# Endpoint avanzado - Reporte detallado
@router.post("/reportes/ventas/detallado", response_model=ReporteVentasResponse)
def get_reporte_ventas_detallado(
    reporte_data: ReporteVentasRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_manager_or_admin)  # Solo gerentes y admins
):
    # Validar rango de fechas
    if reporte_data.fecha_fin <= reporte_data.fecha_inicio:
        raise HTTPException(status_code=400, detail="Fecha fin debe ser posterior a fecha inicio")

    # Lógica para generar reporte detallado
    ventas_detalle = []
    if reporte_data.incluir_detalles and current_user.role <= 2:  # Solo admin y gerente
        ventas_detalle = [
            {"fecha": "2024-01-15", "monto": 1500.00, "cliente": "Cliente A"},
            {"fecha": "2024-01-16", "monto": 2300.00, "cliente": "Cliente B"}
        ]

    return {
        "periodo": f"{reporte_data.fecha_inicio.date()} a {reporte_data.fecha_fin.date()}",
        "total_ventas": 50000.00,
        "cantidad_transacciones": 15,
        "vendedor_top": "María García",
        "detalles": ventas_detalle if reporte_data.incluir_detalles else None
    }

# Endpoint administrativo - Exportar datos
@router.get("/reportes/ventas/exportar")
def exportar_ventas(
    formato: str = "csv",  # csv, excel, pdf
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)  # Solo administradores
):
    if formato not in ["csv", "excel", "pdf"]:
        raise HTTPException(status_code=400, detail="Formato no válido. Use: csv, excel, pdf")

    # Lógica para generar archivo de exportación
    archivo_url = f"/downloads/ventas_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{formato}"

    return {
        "message": "Reporte generado exitosamente",
        "formato": formato,
        "archivo_url": archivo_url,
        "generado_por": current_user.email,
        "timestamp": datetime.now()
    }
```

#### Paso 2: Agregar Endpoints de Utilidad

```python
# Endpoint para obtener estadísticas rápidas
@router.get("/dashboard/estadisticas")
def get_estadisticas_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(require_collaborator_or_better)  # Colaboradores y superiores
):
    # Diferente información según el rol
    stats_base = {
        "total_usuarios": 150,
        "usuarios_activos_hoy": 23,
        "servidor_status": "OK"
    }

    # Información adicional para roles superiores
    if current_user.role <= 2:  # Admin y Gerente
        stats_base.update({
            "ingresos_mes": 75000.00,
            "crecimiento_mensual": 12.5,
            "usuarios_nuevos_semana": 8
        })

    # Información ultra sensible solo para Admin
    if current_user.role == 1:  # Solo Admin
        stats_base.update({
            "costo_operacional": 45000.00,
            "margen_ganancia": 40.0,
            "proyeccion_trimestre": 225000.00
        })

    return stats_base

# Endpoint para búsquedas avanzadas
@router.get("/buscar/avanzada")
def busqueda_avanzada(
    q: str,
    tipo: str = "personas",  # personas, usuarios, reportes
    limite: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(require_any_user)
):
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Consulta debe tener al menos 2 caracteres")

    resultados = []

    if tipo == "personas" and current_user.role <= 4:  # Hasta lector
        # Búsqueda en personas
        personas = db.query(Persona).filter(
            Persona.first_name.ilike(f"%{q}%") |
            Persona.last_name.ilike(f"%{q}%")
        ).limit(limite).all()

        resultados = [
            {
                "tipo": "persona",
                "id": p.id,
                "nombre": f"{p.first_name} {p.last_name}",
                "telefono": p.phone if current_user.role <= 3 else None  # Solo colaborador+
            }
            for p in personas
        ]

    elif tipo == "usuarios" and current_user.role <= 2:  # Solo admin y gerente
        # Búsqueda en usuarios
        usuarios = db.query(User).filter(
            User.name.ilike(f"%{q}%") |
            User.email.ilike(f"%{q}%")
        ).limit(limite).all()

        resultados = [
            {
                "tipo": "usuario",
                "id": u.id,
                "nombre": u.name,
                "email": u.email,
                "rol": u.role
            }
            for u in usuarios
        ]

    return {
        "consulta": q,
        "tipo": tipo,
        "total_encontrados": len(resultados),
        "resultados": resultados
    }
```

#### Paso 3: Endpoints con Validaciones Complejas

```python
# Endpoint para operaciones en lote
@router.post("/operaciones/lote")
def operacion_en_lote(
    operacion: str,  # activar, desactivar, eliminar
    ids: list[int],
    confirmar: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)  # Solo admin para operaciones masivas
):
    if operacion not in ["activar", "desactivar", "eliminar"]:
        raise HTTPException(status_code=400, detail="Operación no válida")

    if len(ids) == 0:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un ID")

    if len(ids) > 50:
        raise HTTPException(status_code=400, detail="Máximo 50 elementos por lote")

    # Confirmación requerida para operaciones destructivas
    if operacion == "eliminar" and not confirmar:
        return {
            "message": "Operación requiere confirmación",
            "elementos_afectados": len(ids),
            "operacion": operacion,
            "confirmar_requerido": True
        }

    # Ejecutar operación
    personas_afectadas = db.query(Persona).filter(Persona.id.in_(ids)).all()

    if len(personas_afectadas) != len(ids):
        raise HTTPException(status_code=404, detail="Algunos IDs no fueron encontrados")

    contador = 0
    for persona in personas_afectadas:
        if operacion == "activar":
            persona.is_active = True
        elif operacion == "desactivar":
            persona.is_active = False
        elif operacion == "eliminar":
            persona.is_active = False  # Soft delete

        persona.updated_by = current_user.id
        contador += 1

    db.commit()

    return {
        "message": f"Operación '{operacion}' completada",
        "elementos_procesados": contador,
        "procesado_por": current_user.email,
        "timestamp": datetime.now()
    }

# Endpoint para auditoría
@router.get("/auditoria/cambios")
def get_log_cambios(
    entidad_id: Optional[int] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    limite: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(require_manager_or_admin)  # Solo gerente y admin
):
    # Construir query base
    query = db.query(Persona).filter(Persona.updated_by.isnot(None))

    # Aplicar filtros
    if entidad_id:
        query = query.filter(Persona.id == entidad_id)

    if fecha_desde:
        query = query.filter(Persona.updated_at >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Persona.updated_at <= fecha_hasta)

    # Obtener resultados
    cambios = query.order_by(Persona.updated_at.desc()).limit(limite).all()

    resultado = []
    for persona in cambios:
        # Obtener información del usuario que hizo el cambio
        usuario_editor = db.query(User).filter(User.id == persona.updated_by).first()

        resultado.append({
            "entidad_id": persona.id,
            "entidad_nombre": f"{persona.first_name} {persona.last_name}",
            "fecha_cambio": persona.updated_at,
            "editado_por": usuario_editor.name if usuario_editor else "Usuario desconocido",
            "editor_email": usuario_editor.email if usuario_editor else None,
            "estado_actual": "Activo" if persona.is_active else "Inactivo"
        })

    return {
        "total_cambios": len(resultado),
        "filtros_aplicados": {
            "entidad_id": entidad_id,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        },
        "cambios": resultado
    }
```

### Patrones para Diferentes Tipos de Endpoints

#### **Endpoints de Consulta (GET)**
```python
# Patrón básico
@router.get("/recurso")
def get_recurso(current_user = Depends(require_any_user)):
    return {"data": "información pública"}

# Con parámetros de consulta
@router.get("/recurso/filtrado")
def get_recurso_filtrado(
    filtro: str = None,
    limite: int = 10,
    current_user = Depends(require_any_user)
):
    return {"filtro": filtro, "limite": limite}

# Con path parameters
@router.get("/recurso/{recurso_id}")
def get_recurso_by_id(
    recurso_id: int,
    current_user = Depends(require_any_user)
):
    return {"id": recurso_id}
```

#### **Endpoints de Acción (POST)**
```python
# Crear recurso
@router.post("/recurso")
def create_recurso(
    data: RecursoCreate,
    current_user = Depends(require_collaborator_or_better)
):
    return {"message": "Creado", "data": data}

# Acción específica
@router.post("/recurso/{id}/accion")
def ejecutar_accion(
    id: int,
    parametros: AccionRequest,
    current_user = Depends(require_manager_or_admin)
):
    return {"message": "Acción ejecutada", "id": id}
```

#### **Endpoints de Actualización (PUT/PATCH)**
```python
@router.put("/recurso/{id}")
def update_recurso(
    id: int,
    data: RecursoUpdate,
    current_user = Depends(require_collaborator_or_better)
):
    return {"message": "Actualizado", "id": id}
```

#### **Endpoints de Eliminación (DELETE)**
```python
@router.delete("/recurso/{id}")
def delete_recurso(
    id: int,
    current_user = Depends(require_admin)
):
    return {"message": "Eliminado", "id": id}
```

### Mejores Prácticas para Nuevos Endpoints

1. **Siempre usar el permiso mínimo necesario**
2. **Validar parámetros de entrada**
3. **Manejar errores apropiadamente**
4. **Documentar con docstrings**
5. **Usar response_model cuando sea posible**
6. **Implementar paginación para listas grandes**
7. **Agregar logging para operaciones críticas**

### 🧪 Probar Nuevos Endpoints

```python
# Agregar tests básicos
def test_nuevo_endpoint():
    # Probar con diferentes roles
    # Validar respuestas esperadas
    # Verificar permisos
    pass
```

Esta guía te permite agregar cualquier tipo de endpoint manteniendo la consistencia y seguridad del sistema.

## Endpoints Dinámicos Avanzados - Filtros y Búsquedas

### Ejemplo 1: Búsqueda por Rango de Fechas

```python
from datetime import datetime, date
from typing import Optional, List

# Esquemas para filtros dinámicos
class FiltroFechas(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    include_time: bool = False

class FiltroNumerico(BaseModel):
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    operador: str = "between"  # between, greater, less, equal

# Endpoint con filtros de fechas dinámicos
@router.get("/personas/filtro-fechas")
def buscar_personas_por_fechas(
    # Parámetros de consulta directos
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    edad_minima: Optional[int] = None,
    edad_maxima: Optional[int] = None,
    incluir_inactivos: bool = False,
    ordenar_por: str = "created_at",  # created_at, birth_date, first_name
    orden: str = "desc",  # asc, desc
    pagina: int = 1,
    limite: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(require_any_user)
):
    """
    Busca personas con filtros dinámicos de fechas y criterios múltiples.

    Ejemplos de uso:
    - /personas/filtro-fechas?fecha_inicio=2024-01-01&fecha_fin=2024-12-31
    - /personas/filtro-fechas?edad_minima=18&edad_maxima=65
    - /personas/filtro-fechas?ordenar_por=first_name&orden=asc
    """

    # Construir query base
    query = db.query(Persona)

    # Aplicar filtros dinámicamente
    filtros_aplicados = []

    # Filtro por estado activo
    if not incluir_inactivos:
        query = query.filter(Persona.is_active == True)
        filtros_aplicados.append("Solo activos")

    # Filtros de fechas de creación
    if fecha_inicio:
        query = query.filter(Persona.created_at >= datetime.combine(fecha_inicio, datetime.min.time()))
        filtros_aplicados.append(f"Desde: {fecha_inicio}")

    if fecha_fin:
        query = query.filter(Persona.created_at <= datetime.combine(fecha_fin, datetime.max.time()))
        filtros_aplicados.append(f"Hasta: {fecha_fin}")

    # Filtros de edad (calculada dinámicamente)
    if edad_minima or edad_maxima:
        from sqlalchemy import extract, func

        # Calcular fecha límite para edad
        if edad_maxima:
            fecha_nacimiento_min = date.today().replace(year=date.today().year - edad_maxima - 1)
            query = query.filter(Persona.birth_date >= fecha_nacimiento_min)
            filtros_aplicados.append(f"Edad máxima: {edad_maxima}")

        if edad_minima:
            fecha_nacimiento_max = date.today().replace(year=date.today().year - edad_minima)
            query = query.filter(Persona.birth_date <= fecha_nacimiento_max)
            filtros_aplicados.append(f"Edad mínima: {edad_minima}")

    # Ordenamiento dinámico
    if ordenar_por == "first_name":
        order_column = Persona.first_name
    elif ordenar_por == "birth_date":
        order_column = Persona.birth_date
    else:  # default created_at
        order_column = Persona.created_at

    if orden == "asc":
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())

    # Contar total antes de paginación
    total_registros = query.count()

    # Aplicar paginación
    offset = (pagina - 1) * limite
    personas = query.offset(offset).limit(limite).all()

    # Calcular edad para cada persona
    resultados = []
    for persona in personas:
        edad = None
        if persona.birth_date:
            edad = date.today().year - persona.birth_date.year
            if (date.today().month, date.today().day) < (persona.birth_date.month, persona.birth_date.day):
                edad -= 1

        resultados.append({
            "id": persona.id,
            "nombre_completo": f"{persona.first_name} {persona.last_name}",
            "telefono": persona.phone,
            "edad": edad,
            "fecha_nacimiento": persona.birth_date,
            "fecha_creacion": persona.created_at,
            "activo": persona.is_active
        })

    return {
        "resultados": resultados,
        "paginacion": {
            "pagina_actual": pagina,
            "limite": limite,
            "total_registros": total_registros,
            "total_paginas": (total_registros + limite - 1) // limite
        },
        "filtros_aplicados": filtros_aplicados,
        "ordenamiento": f"{ordenar_por} {orden}"
    }
```

### Ejemplo 2: Filtros Numéricos Dinámicos

```python
# Endpoint para búsquedas con operadores numéricos
@router.get("/personas/filtro-numerico")
def buscar_con_filtros_numericos(
    # Filtros numéricos con operadores
    campo: str = "id",  # id, user_id, age
    operador: str = "equal",  # equal, greater, less, between, not_equal
    valor: Optional[float] = None,
    valor_min: Optional[float] = None,
    valor_max: Optional[float] = None,

    # Filtros de texto con operadores
    campo_texto: str = "first_name",  # first_name, last_name, phone, address
    texto_buscar: Optional[str] = None,
    busqueda_exacta: bool = False,

    db: Session = Depends(get_db),
    current_user = Depends(require_any_user)
):
    """
    Búsqueda avanzada con operadores numéricos y de texto.

    Ejemplos:
    - /personas/filtro-numerico?campo=id&operador=greater&valor=10
    - /personas/filtro-numerico?campo=age&operador=between&valor_min=25&valor_max=40
    - /personas/filtro-numerico?campo_texto=first_name&texto_buscar=Juan&busqueda_exacta=false
    """

    query = db.query(Persona).filter(Persona.is_active == True)

    # Aplicar filtros numéricos dinámicamente
    if valor is not None or (valor_min is not None and valor_max is not None):

        # Mapear campos numéricos
        campo_mapping = {
            "id": Persona.id,
            "user_id": Persona.user_id
        }

        if campo in campo_mapping:
            column = campo_mapping[campo]

            if operador == "equal":
                query = query.filter(column == valor)
            elif operador == "not_equal":
                query = query.filter(column != valor)
            elif operador == "greater":
                query = query.filter(column > valor)
            elif operador == "less":
                query = query.filter(column < valor)
            elif operador == "between" and valor_min is not None and valor_max is not None:
                query = query.filter(column.between(valor_min, valor_max))

        # Campo especial: edad calculada
        elif campo == "age" and valor is not None:
            from sqlalchemy import extract

            if operador == "equal":
                target_year = date.today().year - int(valor)
                query = query.filter(extract('year', Persona.birth_date) == target_year)
            elif operador == "greater":
                target_year = date.today().year - int(valor)
                query = query.filter(extract('year', Persona.birth_date) < target_year)
            elif operador == "less":
                target_year = date.today().year - int(valor)
                query = query.filter(extract('year', Persona.birth_date) > target_year)
            elif operador == "between" and valor_min is not None and valor_max is not None:
                year_max = date.today().year - int(valor_min)
                year_min = date.today().year - int(valor_max)
                query = query.filter(
                    extract('year', Persona.birth_date).between(year_min, year_max)
                )

    # Aplicar filtros de texto dinámicamente
    if texto_buscar:
        campo_texto_mapping = {
            "first_name": Persona.first_name,
            "last_name": Persona.last_name,
            "phone": Persona.phone,
            "address": Persona.address
        }

        if campo_texto in campo_texto_mapping:
            column = campo_texto_mapping[campo_texto]

            if busqueda_exacta:
                query = query.filter(column == texto_buscar)
            else:
                query = query.filter(column.ilike(f"%{texto_buscar}%"))

    personas = query.limit(100).all()

    return {
        "total_encontrados": len(personas),
        "filtros": {
            "numerico": f"{campo} {operador} {valor or f'{valor_min}-{valor_max}'}",
            "texto": f"{campo_texto} {'=' if busqueda_exacta else 'contiene'} '{texto_buscar}'" if texto_buscar else None
        },
        "resultados": [
            {
                "id": p.id,
                "nombre": f"{p.first_name} {p.last_name}",
                "telefono": p.phone,
                "direccion": p.address,
                "user_id": p.user_id
            }
            for p in personas
        ]
    }
```

### Ejemplo 3: Búsqueda Multi-Criterio Avanzada

```python
from sqlalchemy import and_, or_, not_

class FiltroAvanzado(BaseModel):
    # Filtros de texto
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

    # Filtros de fecha
    creado_desde: Optional[datetime] = None
    creado_hasta: Optional[datetime] = None
    nacido_desde: Optional[date] = None
    nacido_hasta: Optional[date] = None

    # Filtros numéricos
    edad_min: Optional[int] = None
    edad_max: Optional[int] = None

    # Filtros booleanos
    solo_activos: bool = True
    con_usuario: Optional[bool] = None

    # Opciones de búsqueda
    modo_busqueda: str = "AND"  # AND, OR
    incluir_eliminados: bool = False

@router.post("/personas/busqueda-avanzada")
def busqueda_multi_criterio(
    filtros: FiltroAvanzado,
    ordenar_por: List[str] = ["created_at"],
    orden: str = "desc",
    pagina: int = 1,
    limite: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(require_any_user)
):
    """
    Búsqueda multi-criterio con lógica AND/OR configurable.

    Ejemplo de payload:
    {
        "nombre": "Juan",
        "edad_min": 25,
        "edad_max": 40,
        "creado_desde": "2024-01-01T00:00:00",
        "solo_activos": true,
        "modo_busqueda": "AND"
    }
    """

    query = db.query(Persona)
    condiciones = []

    # Construir condiciones dinámicamente
    if filtros.nombre:
        condiciones.append(
            or_(
                Persona.first_name.ilike(f"%{filtros.nombre}%"),
                Persona.last_name.ilike(f"%{filtros.nombre}%")
            )
        )

    if filtros.telefono:
        condiciones.append(Persona.phone.ilike(f"%{filtros.telefono}%"))

    if filtros.direccion:
        condiciones.append(Persona.address.ilike(f"%{filtros.direccion}%"))

    # Filtros de fecha
    if filtros.creado_desde:
        condiciones.append(Persona.created_at >= filtros.creado_desde)

    if filtros.creado_hasta:
        condiciones.append(Persona.created_at <= filtros.creado_hasta)

    if filtros.nacido_desde:
        condiciones.append(Persona.birth_date >= filtros.nacido_desde)

    if filtros.nacido_hasta:
        condiciones.append(Persona.birth_date <= filtros.nacido_hasta)

    # Filtros de edad calculada
    if filtros.edad_min or filtros.edad_max:
        from sqlalchemy import extract

        if filtros.edad_min:
            year_max = date.today().year - filtros.edad_min
            condiciones.append(extract('year', Persona.birth_date) <= year_max)

        if filtros.edad_max:
            year_min = date.today().year - filtros.edad_max - 1
            condiciones.append(extract('year', Persona.birth_date) >= year_min)

    # Filtros booleanos
    if filtros.solo_activos:
        condiciones.append(Persona.is_active == True)

    if filtros.con_usuario is not None:
        if filtros.con_usuario:
            condiciones.append(Persona.user_id.isnot(None))
        else:
            condiciones.append(Persona.user_id.is_(None))

    # Aplicar lógica AND/OR
    if condiciones:
        if filtros.modo_busqueda.upper() == "OR":
            query = query.filter(or_(*condiciones))
        else:  # AND por defecto
            query = query.filter(and_(*condiciones))

    # Ordenamiento dinámico múltiple
    for campo_orden in ordenar_por:
        if campo_orden == "first_name":
            column = Persona.first_name
        elif campo_orden == "birth_date":
            column = Persona.birth_date
        elif campo_orden == "created_at":
            column = Persona.created_at
        else:
            continue

        if orden == "asc":
            query = query.order_by(column.asc())
        else:
            query = query.order_by(column.desc())

    # Ejecutar consulta con paginación
    total = query.count()
    offset = (pagina - 1) * limite
    personas = query.offset(offset).limit(limite).all()

    # Procesar resultados
    resultados = []
    for persona in personas:
        # Calcular edad
        edad = None
        if persona.birth_date:
            edad = date.today().year - persona.birth_date.year
            if (date.today().month, date.today().day) < (persona.birth_date.month, persona.birth_date.day):
                edad -= 1

        resultados.append({
            "id": persona.id,
            "nombre_completo": f"{persona.first_name} {persona.last_name}",
            "telefono": persona.phone,
            "direccion": persona.address,
            "edad": edad,
            "fecha_nacimiento": persona.birth_date,
            "tiene_usuario": persona.user_id is not None,
            "activo": persona.is_active,
            "creado_en": persona.created_at
        })

    return {
        "resultados": resultados,
        "metadata": {
            "total_encontrados": total,
            "pagina": pagina,
            "limite": limite,
            "total_paginas": (total + limite - 1) // limite,
            "filtros_aplicados": len([c for c in condiciones if c is not None]),
            "modo_busqueda": filtros.modo_busqueda
        }
    }
```

### Ejemplo 4: Estadísticas Dinámicas por Períodos

```python
@router.get("/estadisticas/dinamicas")
def estadisticas_por_periodo(
    # Parámetros de período
    tipo_periodo: str = "mensual",  # diario, semanal, mensual, anual, personalizado
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,

    # Métricas a calcular
    metricas: List[str] = ["total", "nuevos", "activos"],  # total, nuevos, activos, por_edad

    # Agrupaciones
    agrupar_por: Optional[str] = None,  # estado, edad_rango, mes_creacion

    db: Session = Depends(get_db),
    current_user = Depends(require_manager_or_admin)
):
    """
    Genera estadísticas dinámicas por diferentes períodos y criterios.

    Ejemplos:
    - /estadisticas/dinamicas?tipo_periodo=mensual&metricas=total,nuevos
    - /estadisticas/dinamicas?tipo_periodo=personalizado&fecha_inicio=2024-01-01&fecha_fin=2024-06-30
    """

    from sqlalchemy import func, extract, case

    # Definir rango de fechas según el tipo de período
    if tipo_periodo == "personalizado":
        if not fecha_inicio or not fecha_fin:
            raise HTTPException(status_code=400, detail="Para período personalizado se requieren fecha_inicio y fecha_fin")
    else:
        # Calcular fechas automáticamente
        hoy = date.today()
        if tipo_periodo == "diario":
            fecha_inicio = hoy - timedelta(days=30)
            fecha_fin = hoy
        elif tipo_periodo == "semanal":
            fecha_inicio = hoy - timedelta(weeks=12)
            fecha_fin = hoy
        elif tipo_periodo == "mensual":
            fecha_inicio = hoy.replace(month=1, day=1)
            fecha_fin = hoy
        elif tipo_periodo == "anual":
            fecha_inicio = date(hoy.year - 2, 1, 1)
            fecha_fin = hoy

    # Query base con filtro de fechas
    query = db.query(Persona).filter(
        Persona.created_at >= datetime.combine(fecha_inicio, datetime.min.time()),
        Persona.created_at <= datetime.combine(fecha_fin, datetime.max.time())
    )

    estadisticas = {}

    # Calcular métricas solicitadas
    if "total" in metricas:
        estadisticas["total_registros"] = query.count()
        estadisticas["total_activos"] = query.filter(Persona.is_active == True).count()
        estadisticas["total_inactivos"] = query.filter(Persona.is_active == False).count()

    if "nuevos" in metricas:
        # Registros por mes
        registros_por_mes = db.query(
            extract('year', Persona.created_at).label('año'),
            extract('month', Persona.created_at).label('mes'),
            func.count(Persona.id).label('cantidad')
        ).filter(
            Persona.created_at >= datetime.combine(fecha_inicio, datetime.min.time()),
            Persona.created_at <= datetime.combine(fecha_fin, datetime.max.time())
        ).group_by(
            extract('year', Persona.created_at),
            extract('month', Persona.created_at)
        ).order_by('año', 'mes').all()

        estadisticas["registros_por_mes"] = [
            {
                "año": int(r.año),
                "mes": int(r.mes),
                "cantidad": r.cantidad,
                "periodo": f"{int(r.año)}-{int(r.mes):02d}"
            }
            for r in registros_por_mes
        ]

    if "por_edad" in metricas:
        # Estadísticas por rangos de edad
        personas_con_edad = query.filter(Persona.birth_date.isnot(None)).all()

        rangos_edad = {
            "0-17": 0, "18-25": 0, "26-35": 0,
            "36-45": 0, "46-55": 0, "56+": 0
        }

        for persona in personas_con_edad:
            edad = date.today().year - persona.birth_date.year
            if (date.today().month, date.today().day) < (persona.birth_date.month, persona.birth_date.day):
                edad -= 1

            if edad < 18:
                rangos_edad["0-17"] += 1
            elif edad <= 25:
                rangos_edad["18-25"] += 1
            elif edad <= 35:
                rangos_edad["26-35"] += 1
            elif edad <= 45:
                rangos_edad["36-45"] += 1
            elif edad <= 55:
                rangos_edad["46-55"] += 1
            else:
                rangos_edad["56+"] += 1

        estadisticas["distribucion_por_edad"] = rangos_edad

    # Agrupaciones especiales
    if agrupar_por == "estado":
        por_estado = db.query(
            Persona.is_active,
            func.count(Persona.id).label('cantidad')
        ).filter(
            Persona.created_at >= datetime.combine(fecha_inicio, datetime.min.time()),
            Persona.created_at <= datetime.combine(fecha_fin, datetime.max.time())
        ).group_by(Persona.is_active).all()

        estadisticas["agrupado_por_estado"] = {
            "activos": next((r.cantidad for r in por_estado if r.is_active), 0),
            "inactivos": next((r.cantidad for r in por_estado if not r.is_active), 0)
        }

    return {
        "periodo": {
            "tipo": tipo_periodo,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "dias_incluidos": (fecha_fin - fecha_inicio).days + 1
        },
        "metricas_calculadas": metricas,
        "estadisticas": estadisticas,
        "generado_en": datetime.now(),
        "generado_por": current_user.email
    }
```

### Mejores Prácticas para Endpoints Dinámicos

1. **Validar parámetros de entrada** siempre
2. **Usar límites** para evitar consultas muy pesadas
3. **Implementar paginación** en resultados grandes
4. **Crear índices** en campos que se filtran frecuentemente
5. **Documentar ejemplos** de uso en docstrings
6. **Manejar errores** de parámetros inválidos
7. **Optimizar consultas** con JOINs cuando sea necesario

## Estructura del Proyecto

```
mi-proyecto/
├── main.py                    # Aplicación FastAPI principal
├── database.py               # Modelos base y configuración DB
├── auth.py                   # Autenticación y permisos
├── generate_secret_key.py    # Generador de claves seguras
├── requirements.txt          # Dependencias
├── .env                      # Configuración (opcional)
├── modules/                  # Módulos de entidades
│   └── personas/            # Ejemplo de nueva entidad
│       ├── __init__.py
│       ├── models.py        # Modelo SQLAlchemy
│       ├── schemas.py       # Esquemas Pydantic
│       └── routes.py        # Endpoints FastAPI
└── README.md                # Este archivo
```

## Deployment a Producción

1. **Generar claves seguras:**
```bash
python generate_secret_key.py
```

2. **Configurar variables de entorno** con valores de producción

3. **Usar servidor ASGI como Gunicorn:**
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Contribuciones

Para agregar nuevas entidades, seguir el patrón del módulo `personas` y consultar `MODULAR_GUIDE.md` para instrucciones detalladas.

## Licencia

Template libre para uso en proyectos personales y comerciales.