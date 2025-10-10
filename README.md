# HR Management System - Sistema de Gestión de Recursos Humanos

> Sistema completo de gestión de RRHH desarrollado con FastAPI, arquitectura de 7 capas y sistema híbrido de permisos. Basado en plantilla API empresarial.

## Características Principales

- **Arquitectura de 7 Capas** - Router → Controller → Service → Repository → Model → Database
- **Autenticación JWT** con OAuth2 integrado en Swagger
- **BaseRepository Genérico** con TypeVar[T] reutilizable en todas las entidades
- **Configuración Híbrida** - config.toml (público) + .env (secretos)
- **HR Management System Completo** con 9 entidades principales:
  - **BusinessGroups** - Grupos empresariales (✅ COMPLETED)
  - **Companies** - Empresas dentro de grupos (✅ COMPLETED)
  - **Branches** - Sucursales/Oficinas por empresa (✅ COMPLETED)
  - **UserScopes** - Alcance organizacional por usuario (✅ COMPLETED)
  - **UserPermissions** - Permisos granulares por endpoint (✅ COMPLETED)
  - **Department** - Departamentos (jerarquía auto-referenciada) (⏳ PENDING)
  - **Position** - Puestos de trabajo (⏳ PENDING)
  - **Individual** - Personas (datos personales) (⏳ PENDING)
  - **Employee** - Empleados (relación laboral) (⏳ PENDING)
- **Sistema Híbrido de Permisos** - 3 capas (Role + Scope + Permission)
- **Auto-Discovery de Endpoints** - Detecta automáticamente nuevas rutas
- **Soft Delete** y campos de auditoría en todas las entidades
- **Inicialización Automática** de base de datos con datos geográficos
- **Sistema de Roles** de 5 niveles (Admin, Gerente, Gestor, Colaborador, Guest)
- **Tests Unitarios** incluidos
- **Documentación Completa** con ejemplos paso a paso

---

## Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- Git

---

## Instalación Rápida

### 1. Clonar Repositorio

```bash
git clone https://github.com/aeguzsando1987/HR_system_w_API_template.git
cd HR_system_w_API_template
```

### 2. Crear Ambiente Virtual

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
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

Editar `.env` con tu configuración (el template funciona sin .env con valores por defecto):

```env
# Base de datos
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/mi_proyecto_db

# JWT Security (generar con generate_secret_key.py)
SECRET_KEY=tu-clave-secreta-super-segura

# Admin por defecto
DEFAULT_ADMIN_EMAIL=admin@tuempresa.com
DEFAULT_ADMIN_PASSWORD=tu_password_seguro
```

### 6. Iniciar Aplicación

```bash
python main.py
```

### 7. Verificar Instalación

Abrir en el navegador:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

**Usuario Admin por Defecto:**
- Email: `admin@tuempresa.com`
- Password: `root`

---

## WebApp Demo Funcional

En la carpeta [webapp_demo/](../webapp_demo/) encontrarás aplicaciones web funcionales que consumen esta API:

### Vanilla JS Demo (95% Completo)
- Login con JWT y manejo de roles
- CRUD completo de Personas con modales
- Dual View Mode (Dashboard cards y Tabla)
- Sistema de skills (backend listo)
- 10 bugs corregidos durante desarrollo
- Interfaz oscura con colores guindas (#8B1538)

Ver [webapp_demo/README.md](../webapp_demo/README.md) para instrucciones de uso.

---

## Documentación Completa

### Para Comenzar a Desarrollar

1. **[PATRON_DESARROLLO.md](PATRON_DESARROLLO.md)** - **LECTURA OBLIGATORIA**
   - Ejemplo completo con entidades Técnico y Actividad
   - Patrón de 7 capas explicado paso a paso
   - POST común vs POST with user (para entidades de personal)
   - 8 ejemplos de Enums comunes
   - Código completo de las 6 capas por entidad
   - Pruebas en Swagger con ejemplos de requests/responses
   - Validaciones y transacciones atómicas

2. **[ADDING_ENTITIES.md](ADDING_ENTITIES.md)** - Guía paso a paso
   - Cómo agregar nuevas entidades al proyecto
   - Estructura de archivos necesarios
   - Ejemplos con Person, Country, State
   - Checklist de implementación

3. **[CLAUDE.md](CLAUDE.md)** - Estado del proyecto
   - Progreso actual y entidades implementadas
   - Problemas resueltos y soluciones
   - Comandos útiles
   - Próximos pasos

### Arquitectura del Proyecto

```
app/
├── entities/              # Entidades del negocio
│   ├── persons/          # Ejemplo completo (40+ campos)
│   ├── countries/        # Países con ISO codes
│   ├── states/           # Estados por país
│   └── users/            # Usuarios del sistema
│
├── shared/               # Código compartido
│   ├── base_repository.py        # Repository genérico
│   ├── exceptions.py              # Excepciones custom
│   ├── dependencies.py            # Dependencias FastAPI
│   ├── init_db.py                 # Auto-inicialización BD
│   └── data/                      # Datos precargados
│
└── tests/                # Tests unitarios
    ├── test_persons/
    └── test_users/
```

---

## Agregar Nueva Entidad - Resumen Rápido

**Para agregar una nueva entidad (ej: Producto):**

1. Leer **[PATRON_DESARROLLO.md](PATRON_DESARROLLO.md)** - Tiene el ejemplo completo
2. Crear carpeta `app/entities/productos/`
3. Crear 6 archivos siguiendo el patrón:
   - `models/producto.py` - Modelo SQLAlchemy
   - `schemas/producto_schemas.py` - Schemas Pydantic
   - `repositories/producto_repository.py` - Operaciones BD
   - `services/producto_service.py` - Lógica de negocio
   - `controllers/producto_controller.py` - Manejo de requests
   - `routers/producto_router.py` - Endpoints FastAPI
4. Registrar router en `main.py`
5. Probar en Swagger

**Consulta [PATRON_DESARROLLO.md](PATRON_DESARROLLO.md) para ver el código completo de cada archivo.**

---

## Endpoints Disponibles

### Autenticación
- `POST /token` - Obtener token JWT
- `POST /login` - Login alternativo

### Usuarios
- `POST /users` - Crear usuario
- `GET /users` - Listar usuarios
- `GET /users/me` - Perfil actual
- `GET /users/roles` - Lista de roles disponibles
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario

### BusinessGroups (✅ COMPLETED)
- `POST /api/v1/business-groups` - Crear grupo empresarial
- `GET /api/v1/business-groups` - Listar grupos
- `GET /api/v1/business-groups/paginated` - Listar con paginación avanzada
- `GET /api/v1/business-groups/search?name=` - Buscar por nombre
- `GET /api/v1/business-groups/{id}` - Obtener por ID
- `PUT /api/v1/business-groups/{id}` - Actualizar
- `DELETE /api/v1/business-groups/{id}` - Eliminar (soft delete)

### Companies (✅ COMPLETED)
- `POST /api/v1/companies` - Crear empresa
- `GET /api/v1/companies` - Listar empresas
- `GET /api/v1/companies/paginated` - Listar con paginación avanzada
- `GET /api/v1/companies/search?q=` - Buscar empresas
- `GET /api/v1/companies/{id}` - Obtener por ID
- `PUT /api/v1/companies/{id}` - Actualizar
- `DELETE /api/v1/companies/{id}` - Eliminar (soft delete)

### Branches (✅ COMPLETED)
- `POST /api/v1/branches/` - Crear sucursal
- `GET /api/v1/branches/` - Listar sucursales
- `GET /api/v1/branches/paginated` - Listar con paginación
- `GET /api/v1/branches/search?q=` - Buscar sucursales
- `GET /api/v1/branches/by-company/{company_id}` - Sucursales por empresa
- `GET /api/v1/branches/{id}` - Obtener por ID
- `PUT /api/v1/branches/{id}` - Actualizar
- `DELETE /api/v1/branches/{id}` - Eliminar (soft delete)

### UserScopes (✅ COMPLETED)
- `POST /api/v1/user-scopes` - Asignar alcance a usuario
- `GET /api/v1/user-scopes` - Listar alcances
- `GET /api/v1/user-scopes/by-user/{user_id}` - Alcances de un usuario
- `GET /api/v1/user-scopes/{id}` - Obtener por ID
- `PUT /api/v1/user-scopes/{id}` - Actualizar
- `DELETE /api/v1/user-scopes/{id}` - Eliminar

### UserPermissions (✅ COMPLETED)
- `POST /api/v1/user-permissions` - Crear permiso
- `GET /api/v1/user-permissions` - Listar permisos
- `GET /api/v1/user-permissions/by-user/{user_id}` - Permisos de usuario
- `GET /api/v1/user-permissions/{id}` - Obtener por ID
- `PUT /api/v1/user-permissions/{id}` - Actualizar
- `DELETE /api/v1/user-permissions/{id}` - Eliminar
- `GET /api/v1/admin/permissions/endpoints` - Auto-discovery (lista todos los endpoints)
- `PUT /api/v1/admin/permissions/bulk-update/{user_id}` - Actualización masiva (para app móvil)

### Persons (Ejemplo completo)
- 25+ endpoints con CRUD, skills, búsquedas, cálculos

### Countries & States
- `GET /countries/` - Listar países (3 precargados)
- `GET /states/by-country/{id}` - Estados por país (114 precargados)

---

## Sistema de Permisos Híbrido (3 Capas)

El sistema implementa un modelo híbrido de permisos con 3 capas complementarias:

### 1. Jerarquía de Roles (Capa Base)

| Rol | Nivel | Descripción | Permisos |
|-----|-------|-------------|----------|
| Admin | 1 | Administrador | Acceso total al sistema |
| Gerente | 2 | Manager | CRUD usuarios y entidades |
| Gestor | 3 | Gestor de área | CRUD entidades asignadas |
| Colaborador | 4 | Collaborator | CRUD entidades limitadas |
| Guest | 5 | Invitado | Solo lectura |

### 2. UserScopes (Alcance Organizacional)

Define el **alcance** de las operaciones de un usuario dentro de la jerarquía organizacional:

| Scope | Descripción | Ejemplo |
|-------|-------------|---------|
| GLOBAL | Acceso a toda la organización | CEO, CFO |
| BUSINESS_GROUP | Limitado a un grupo empresarial | Director de Grupo |
| COMPANY | Limitado a una empresa | Gerente General |
| BRANCH | Limitado a una sucursal | Gerente de Sucursal |
| DEPARTMENT | Limitado a un departamento | Jefe de Departamento |

**Ejemplo:**
```python
# Usuario: Juan Pérez
# Role: Gerente (nivel 2)
# Scope: COMPANY
# Company ID: 5
# → Puede gestionar SOLO empleados, departamentos, posiciones de la empresa ID=5
```

### 3. UserPermissions (Permisos Granulares)

Permisos específicos por **endpoint** y **método HTTP**:

```json
{
  "/api/v1/employees": {
    "GET": true,
    "POST": true,
    "PUT": false,
    "DELETE": false
  },
  "/api/v1/employees/with-user": {
    "POST": false
  }
}
```

**Características:**
- ✅ Auto-discovery: Detecta automáticamente nuevos endpoints
- ✅ Bulk update: Actualización masiva desde app móvil
- ✅ Validación híbrida: Verifica permiso específico + fallback a ruta base
- ✅ Middleware automático: Valida permisos en cada request

### Usar en Endpoints

```python
from app.shared.dependencies import get_current_user

# Validación por Role
@router.delete("/recurso/{id}")
def delete_recurso(current_user = Depends(get_current_user)):
    if current_user.role > 2:  # Solo Admin y Gerente
        raise HTTPException(403, "Permisos insuficientes")
```

Ver **[PATRON_DESARROLLO.md](PATRON_DESARROLLO.md)** para ejemplos completos de autorización.

---

## Comandos Útiles

### Servidor
```bash
python main.py
```

### Ver Documentación
```
http://localhost:8001/docs
```

### Truncar Base de Datos
```bash
python truncate_db.py
```

### Ejecutar Tests
```bash
pytest app/tests/ -v
```

### Generar Secret Key
```bash
python generate_secret_key.py
```

---

## Configuración Híbrida

**config.toml** - Valores públicos (versionado en git):
- Configuración de features
- Límites de paginación
- Validaciones de negocio
- Pool de conexiones

**.env** - Valores secretos (NO versionar):
- DATABASE_URL
- SECRET_KEY
- Credenciales de admin

El sistema usa `.env` con fallback a `config.toml` para máxima flexibilidad.

---

## Estructura de Archivos

```
mi-proyecto/
├── app/
│   ├── entities/              # Entidades del negocio
│   ├── shared/                # Código compartido
│   └── tests/                 # Tests unitarios
├── main.py                    # Aplicación FastAPI
├── database.py               # Configuración DB
├── config.toml               # Config pública
├── .env                      # Config secreta
├── requirements.txt          # Dependencias
├── README.md                 # Este archivo
├── PATRON_DESARROLLO.md      # Guía de desarrollo
├── ADDING_ENTITIES.md        # Cómo agregar entidades
└── CLAUDE.md                 # Estado del proyecto
```

---

## Entidades Precargadas

Al iniciar el servidor por primera vez, se cargan automáticamente:

### Countries (3)
- United States (US/USA/840)
- Mexico (MX/MEX/484)
- Colombia (CO/COL/170)

### States (114)
- USA: 50 estados
- Mexico: 32 estados
- Colombia: 32 departamentos

---

## Próximos Pasos Después de Instalar

1. ✅ **Leer [PATRON_DESARROLLO.md](PATRON_DESARROLLO.md)** - Entender el patrón completo
2. ✅ Explorar las 3 entidades base en `app/entities/`
3. ✅ Probar endpoints en Swagger (http://localhost:8001/docs)
4. ✅ Crear tu primera entidad siguiendo el patrón
5. ✅ Personalizar configuración en `config.toml` y `.env`

---

## Deployment a Producción

1. **Generar claves seguras:**
   ```bash
   python generate_secret_key.py
   ```

2. **Configurar .env** con valores de producción

3. **Usar servidor ASGI:**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

---

## Características Técnicas Avanzadas

- **BaseRepository Genérico** - Reutilizable con TypeVar[T]
- **Soft Delete** - No eliminación física de datos
- **Campos de Auditoría** - created_at, updated_at, updated_by
- **Validaciones en Múltiples Capas** - Pydantic + Lógica de Negocio
- **Transacciones Atómicas** - flush() + commit() para operaciones múltiples
- **Relaciones Bidireccionales** - SQLAlchemy relationships configuradas
- **Inicialización Idempotente** - No duplica datos en reinicios

---

## Soporte y Documentación

- **¿Cómo agregar una entidad?** → Ver [PATRON_DESARROLLO.md](PATRON_DESARROLLO.md)
- **¿Cómo funciona la arquitectura?** → Ver [ADDING_ENTITIES.md](ADDING_ENTITIES.md)
- **¿Problemas con la instalación?** → Revisar logs en consola

---

## Licencia

Template libre para uso en proyectos personales y comerciales.

---

**Última actualización:** 2025-10-10
**Versión:** 2.1.0
**Estado:** HR Management System - 5 entidades core completadas (BusinessGroups, Companies, Branches, UserScopes, UserPermissions). Siguiente: Department.
**Repositorio:** [https://github.com/aeguzsando1987/HR_system_w_API_template.git](https://github.com/aeguzsando1987/HR_system_w_API_template.git)
**Autor:** E. Guzman