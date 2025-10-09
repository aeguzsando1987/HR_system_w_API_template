---

## ESPECIFICACIONES DETALLADAS POR ENTIDAD

### 1. BUSINESSGROUP (Grupo Empresarial/Holding)
**Prioridad: CRÍTICA**

**Propósito:**
Contenedor de múltiples empresas. Representa la matriz o grupo empresarial (holding). Es la entidad raíz de la jerarquía organizacional.

**Campos obligatorios:**
- `id` - Integer, PK, auto-increment
- `name` - String(200), NOT NULL, nombre del grupo empresarial
- `legal_name` - String(200), nullable, razón social completa
- `tax_id` - String(50), unique, nullable, identificación fiscal (RFC/RUT/NIT)
- `description` - Text, nullable, descripción del grupo
- `is_active` - Boolean, default=True, soft delete
- `created_at` - DateTime, timestamp automático
- `updated_at` - DateTime, timestamp automático

**Relaciones:**
- 1 BusinessGroup → N Company (un grupo tiene múltiples empresas)
- 1 BusinessGroup → N Employee (para tracking global)

**Validaciones de negocio:**
- name es obligatorio, mínimo 2 caracteres
- tax_id debe ser único si se proporciona
- No permitir eliminar si tiene companies activas asociadas

**Índices requeridos:**
- PRIMARY KEY en id
- UNIQUE en tax_id
- INDEX en is_active

**Endpoints REST:**
- POST /api/v1/business-groups
- GET /api/v1/business-groups (paginado con skip/limit)
- GET /api/v1/business-groups/{id}
- PUT /api/v1/business-groups/{id}
- DELETE /api/v1/business-groups/{id} (soft delete)

**Seed data obligatorio:**
- Mínimo 2 business groups:
  - "Corporativo Global SA"
  - "Grupo Empresarial Regional"

**Testing obligatorio:**
- Crear con todos los campos
- Crear solo con campos obligatorios
- Validar tax_id duplicado (400)
- Validar name vacío (422)
- Soft delete verificando is_active=False
- Listar con paginación
- Buscar por nombre (case-insensitive)

---

### 2. COMPANY (Empresa)
**Prioridad: CRÍTICA**

**Propósito:**
Empresas individuales que pertenecen a un BusinessGroup. Múltiples empresas pueden existir bajo un mismo grupo empresarial.

**Campos obligatorios:**
- `id` - Integer, PK
- `business_group_id` - Integer, FK(business_groups.id), NOT NULL, indexed
- `name` - String(200), NOT NULL, nombre comercial
- `legal_name` - String(200), nullable, razón social
- `tax_id` - String(50), unique, nullable
- `industry` - String(100), nullable, sector/industria
- `is_active` - Boolean, default=True
- `created_at`, `updated_at` - DateTime

**Relaciones:**
- N Company → 1 BusinessGroup
- 1 Company → N Branch
- 1 Company → N Department
- 1 Company → N Position
- 1 Company → N Employee

**Validaciones de negocio:**
- business_group_id debe existir y estar activo
- tax_id único globalmente si se proporciona
- name obligatorio
- No permitir eliminar si tiene branches, employees o departments activos

**Índices:**
- PK en id
- FK indexed en business_group_id
- UNIQUE en tax_id
- INDEX en is_active

**Endpoints:**
- POST /api/v1/companies
- GET /api/v1/companies?business_group_id={id}
- GET /api/v1/companies/{id}
- PUT /api/v1/companies/{id}
- DELETE /api/v1/companies/{id} (soft delete)

**Seed data:**
- 2 companies por business_group (4 total):
  - BG1: "Tech Solutions SA", "Retail Express"
  - BG2: "Servicios Globales", "Manufactura Industrial"

**Testing:**
- Crear vinculada a business_group existente
- Validar business_group_id inexistente (404)
- Validar tax_id duplicado (400)
- Listar por business_group específico
- Verificar separación entre diferentes grupos
- Intentar eliminar con employees activos

---

### 3. BRANCH (Sucursal/Sede)
**Prioridad: ALTA**

**Propósito:**
Sucursales físicas o sedes de una empresa. Una empresa puede tener múltiples sucursales.

**Campos obligatorios:**
- `id` - Integer, PK
- `company_id` - Integer, FK(companies.id), NOT NULL, indexed
- `name` - String(200), NOT NULL
- `code` - String(50), NOT NULL, código interno
- `city` - String(100), nullable
- `state_id` - Integer, FK(states.id), nullable (usar State existente)
- `country_id` - Integer, FK(countries.id), nullable (usar Country existente)
- `address` - Text, nullable
- `postal_code` - String(20), nullable
- `phone` - String(20), nullable
- `is_headquarters` - Boolean, default=False
- `is_active` - Boolean, default=True
- `created_at`, `updated_at` - DateTime

**Constraints adicionales:**
- UNIQUE(company_id, code)

**Relaciones:**
- N Branch → 1 Company
- N Branch → 0..1 State (existente)
- N Branch → 0..1 Country (existente)
- 1 Branch → N Department
- 1 Branch → N Employee

**Validaciones de negocio:**
- company_id debe existir y estar activo
- code único dentro de la company
- Solo UNA branch con is_headquarters=True por company
- state_id debe existir si se proporciona
- country_id debe existir si se proporciona
- Consistencia entre state_id y country_id

**Índices:**
- PK en id
- FK indexed en company_id
- UNIQUE en (company_id, code)
- INDEX en is_active

**Endpoints:**
- POST /api/v1/branches
- GET /api/v1/branches?company_id={id}
- GET /api/v1/branches/{id}
- PUT /api/v1/branches/{id}
- DELETE /api/v1/branches/{id} (soft delete)

**Seed data:**
- 2 branches por company (8 total):
  - 1 headquarters + 1 sucursal por company
  - Usar countries/states existentes
  - Diferentes ciudades

**Testing:**
- Crear con state_id y country_id válidos
- Validar code duplicado en misma company (400)
- Validar múltiples is_headquarters=True (400)
- Validar company_id inexistente (404)
- Listar por company específica
- Verificar FK con Country/State

---

### 4. DEPARTMENT (Departamento)
**Prioridad: ALTA**

**Propósito:**
Departamentos organizacionales. Pueden ser a nivel empresa (corporativos) o por sucursal. Soporta jerarquía.

**Campos obligatorios:**
- `id` - Integer, PK
- `company_id` - Integer, FK(companies.id), NOT NULL, indexed
- `branch_id` - Integer, FK(branches.id), nullable, indexed (null = corporativo)
- `name` - String(200), NOT NULL
- `code` - String(50), nullable
- `parent_department_id` - Integer, FK(departments.id), nullable, indexed (jerarquía)
- `is_active` - Boolean, default=True
- `created_at`, `updated_at` - DateTime

**Relaciones:**
- N Department → 1 Company
- N Department → 0..1 Branch (nullable para corporativos)
- N Department → 0..1 Department (parent - auto-referencia)
- 1 Department → N Department (children)
- 1 Department → N Employee

**Validaciones de negocio:**
- company_id debe existir y estar activo
- branch_id debe pertenecer a la misma company si se proporciona
- parent_department_id debe pertenecer a la misma company
- NO permitir referencias circulares
- Profundidad máxima: 5 niveles
- branch_id null = departamento corporativo

**Índices:**
- PK en id
- FK indexed en company_id
- FK indexed en branch_id
- FK indexed en parent_department_id
- INDEX en is_active

**Endpoints:**
- POST /api/v1/departments
- GET /api/v1/departments?company_id={id}&branch_id={id}
- GET /api/v1/departments/{id}
- GET /api/v1/departments/{id}/children
- GET /api/v1/departments/{id}/hierarchy
- PUT /api/v1/departments/{id}
- DELETE /api/v1/departments/{id} (soft delete)

**Seed data:**
- 5-6 departments por company (20-24 total):
  - Algunos corporativos (branch_id=null)
  - Algunos por branch
  - 2-3 con parent_department_id (jerarquía 2 niveles)

**Testing:**
- Crear corporativo (branch_id=null)
- Crear vinculado a branch
- Crear con parent_department_id
- Validar parent de diferente company (400)
- Validar referencia circular (400)
- Obtener children
- Obtener hierarchy path
- Intentar eliminar con children activos

---

### 5. POSITION (Puesto/Cargo)
**Prioridad: MEDIA**

**Propósito:**
Catálogo de puestos de trabajo por empresa.

**Campos obligatorios:**
- `id` - Integer, PK
- `company_id` - Integer, FK(companies.id), NOT NULL, indexed
- `title` - String(200), NOT NULL
- `level` - String(50), nullable (junior, senior, manager, director, executive)
- `description` - Text, nullable
- `is_active` - Boolean, default=True
- `created_at`, `updated_at` - DateTime

**Relaciones:**
- N Position → 1 Company
- 1 Position → N Employee

**Validaciones de negocio:**
- company_id debe existir y estar activo
- title obligatorio
- No permitir eliminar si tiene employees activos

**Índices:**
- PK en id
- FK indexed en company_id
- INDEX en is_active

**Endpoints:**
- POST /api/v1/positions
- GET /api/v1/positions?company_id={id}
- GET /api/v1/positions/{id}
- PUT /api/v1/positions/{id}
- DELETE /api/v1/positions/{id} (soft delete)

**Seed data:**
- 6-8 positions por company (24-32 total):
  - Diferentes levels
  - Variedad según industry

**Testing:**
- Crear vinculada a company
- Validar company_id inexistente (404)
- Listar por company
- Verificar separación entre companies
- Intentar eliminar con employees activos

---

### 6. INDIVIDUAL (Datos Personales Base)
**Prioridad: ALTA**

**Propósito:**
Entidad base para datos personales de cualquier individuo. Reemplaza "Person". Un Individual puede o no tener un User asociado.

**IMPORTANTE:** Se llama "Individual" (NO "Person") para evitar confusión con entidades ejemplo previas.

**Campos obligatorios:**
- `id` - Integer, PK
- `first_name` - String(100), NOT NULL
- `last_name` - String(100), NOT NULL
- `second_last_name` - String(100), nullable
- `email` - String(255), unique, NOT NULL, indexed
- `phone` - String(20), nullable
- `mobile_phone` - String(20), nullable
- `birth_date` - Date, nullable
- `gender` - String(20), nullable
- `identification_type` - String(50), nullable
- `identification_number` - String(50), nullable, indexed
- `address` - Text, nullable
- `city` - String(100), nullable
- `state_id` - Integer, FK(states.id), nullable (usar State existente)
- `country_id` - Integer, FK(countries.id), nullable (usar Country existente)
- `postal_code` - String(20), nullable
- `individual_type` - String(20), default='employee'
- `is_active` - Boolean, default=True
- `created_at`, `updated_at` - DateTime

**Modificación a User existente:**
- Agregar campo: `individual_id` - Integer, FK(individuals.id), nullable, UNIQUE

**Relaciones:**
- 1 Individual → 0..1 User
- 1 Individual → 0..N Employee
- N Individual → 0..1 State (existente)
- N Individual → 0..1 Country (existente)

**Validaciones de negocio:**
- email único globalmente
- identification_number único si se proporciona
- Si vincula a User, verificar User no tenga otro Individual
- state_id debe existir si se proporciona
- country_id debe existir si se proporciona

**Índices:**
- PK en id
- UNIQUE en email
- INDEX en identification_number
- INDEX en individual_type
- INDEX en is_active

**Endpoints especiales:**

Dos formas de crear Individual:

1. **POST /api/v1/individuals** (común - sin user)
   - Crea solo Individual
   - Para personas sin acceso al sistema
   - Retorna Individual creado

2. **POST /api/v1/individuals/with-user** (con user)
   - Crea Individual + User en transacción
   - Requiere: username, password, role
   - Vincula automáticamente User.individual_id
   - Retorna Individual + User

Endpoints regulares:
- GET /api/v1/individuals?individual_type={type}&search={q}
- GET /api/v1/individuals/{id}
- PUT /api/v1/individuals/{id}
- DELETE /api/v1/individuals/{id} (soft delete)

**Seed data:**
- 30-35 individuals:
  - 25 tipo 'employee' sin user
  - 5 tipo 'employee' vinculados a Users existentes
  - Usar countries/states existentes
  - Datos realistas

**Testing:**
- Crear individual común sin user
- Crear individual con user vía /with-user
- Validar email duplicado (400)
- Validar identification_number duplicado (400)
- Buscar por nombre
- Buscar por email
- Filtrar por individual_type
- Vincular individual existente a user
- Verificar uso de Country/State
- Validar no vincular mismo Individual a dos Users

---

### 7. EMPLOYEE (Empleado - ENTIDAD CORE)
**Prioridad: CRÍTICA**

**Propósito:**
Entidad central. Vincula Individual con estructura organizacional completa. Incluye jerarquía de supervisión.

**Campos obligatorios:**
- `id` - Integer, PK
- `individual_id` - Integer, FK(individuals.id), NOT NULL, indexed
- `user_id` - Integer, FK(users.id), nullable, indexed
- `business_group_id` - Integer, FK(business_groups.id), NOT NULL, indexed
- `company_id` - Integer, FK(companies.id), NOT NULL, indexed
- `branch_id` - Integer, FK(branches.id), nullable, indexed
- `department_id` - Integer, FK(departments.id), nullable, indexed
- `position_id` - Integer, FK(positions.id), nullable, indexed
- `supervisor_id` - Integer, FK(employees.id), nullable, indexed (auto-referencia)
- `employee_code` - String(50), NOT NULL
- `hire_date` - Date, NOT NULL
- `employment_status` - String(20), default='active'
- `employment_type` - String(20), nullable
- `base_salary` - Numeric(12,2), nullable
- `currency` - String(10), default='USD'
- `is_active` - Boolean, default=True
- `created_at`, `updated_at` - DateTime
- `created_by` - Integer, FK(users.id), nullable

**Constraints adicionales:**
- UNIQUE(company_id, employee_code)

**Relaciones:**
- N Employee → 1 Individual
- N Employee → 0..1 User
- N Employee → 1 BusinessGroup
- N Employee → 1 Company
- N Employee → 0..1 Branch
- N Employee → 0..1 Department
- N Employee → 0..1 Position
- N Employee → 0..1 Employee (supervisor)
- 1 Employee → N Employee (subordinates)

**Validaciones de negocio complejas:**
- individual_id debe existir y estar activo
- business_group_id debe existir y estar activo
- company_id debe existir, estar activo Y pertenecer al business_group_id
- branch_id debe existir, estar activo Y pertenecer a company_id
- department_id debe existir, estar activo Y pertenecer a company_id
- position_id debe existir, estar activo Y pertenecer a company_id
- supervisor_id debe ser employee de la MISMA company_id
- employee_code único dentro de company (no globalmente)
- NO supervisor circular
- NO auto-supervisión
- Si user_id, verificar User.individual_id == Employee.individual_id
- Si terminated, no debe tener subordinates activos

**Índices:**
- PK en id
- FK indexed en individual_id
- FK indexed en business_group_id
- FK indexed en company_id
- FK indexed en branch_id
- FK indexed en department_id
- FK indexed en supervisor_id
- UNIQUE en (company_id, employee_code)
- INDEX en employment_status
- INDEX en is_active

**Endpoints:**
- POST /api/v1/employees
- GET /api/v1/employees?business_group_id={id}&company_id={id}&branch_id={id}&department_id={id}&status={status}&search={q}&skip={n}&limit={n}
- GET /api/v1/employees/{id}
- PUT /api/v1/employees/{id}
- DELETE /api/v1/employees/{id} (soft delete)
- GET /api/v1/employees/{id}/subordinates
- GET /api/v1/employees/{id}/team-tree

**Métodos especiales Repository:**
- `get_by_business_group(bg_id)`
- `get_by_company(company_id)`
- `get_by_branch(branch_id)`
- `get_by_department(department_id)`
- `get_subordinates(supervisor_id)` (directos)
- `get_subordinates_recursive(supervisor_id)` (recursivo)
- `search(company_id, query)`
- `get_by_user(user_id)`

**Seed data:**
- 20-25 employees por company (80-100 total):
  - Usar individuals del seed
  - Distribuir en branches/departments
  - Jerarquía: 1 CEO → 3 Directors → 8 Managers → resto
  - Algunos con user_id
  - business_group_id correcto

**Testing exhaustivo:**
- Crear con todas las relaciones válidas
- Validar business_group_id - company_id consistencia (400)
- Validar branch_id - company_id consistencia (400)
- Validar department_id - company_id consistencia (400)
- Validar position_id - company_id consistencia (400)
- Validar employee_code duplicado en misma company (400)
- Validar employee_code duplicado en diferente company (debe permitir)
- Validar supervisor_id de diferente company (400)
- Validar supervisor circular directo (400)
- Validar supervisor circular indirecto (400)
- Validar auto-supervisión (400)
- Obtener subordinados directos
- Obtener árbol recursivo
- Buscar por nombre de individual
- Buscar por employee_code
- Filtrar por business_group
- Filtrar por company
- Filtrar por branch
- Filtrar por department
- Filtrar por employment_status
- Combinar múltiples filtros
- Verificar user_id - individual_id consistencia

---

### 8. USERSCOPE (Sistema de Permisos con Scope)
**Prioridad: CRÍTICA**

**Propósito:**
Asigna scope (ámbito de acceso) a Users según su rol existente. Permite control granular de acceso a employees.

**Campos obligatorios:**
- `id` - Integer, PK
- `user_id` - Integer, FK(users.id), NOT NULL, indexed
- `scope_type` - String(20), NOT NULL (business_group, company, branch, department)
- `scope_id` - Integer, NOT NULL
- `is_active` - Boolean, default=True
- `assigned_by` - Integer, FK(users.id), nullable
- `assigned_date` - DateTime
- `created_at`, `updated_at` - DateTime

**Constraints adicionales:**
- UNIQUE(user_id, scope_type, scope_id)
- INDEX(user_id, scope_type, scope_id)

**Relaciones:**
- N UserScope → 1 User
- N UserScope → 1 User (assigned_by)

**Validaciones de negocio:**
- user_id debe existir y estar activo
- Si scope_type='business_group', scope_id en business_groups
- Si scope_type='company', scope_id en companies
- Si scope_type='branch', scope_id en branches
- Si scope_type='department', scope_id en departments
- No duplicar scope para mismo user
- Solo 'admin' puede tener scope_type='business_group' o no tener UserScope
- 'gerente' debe tener scope_type='company' o 'branch'
- 'gestor' debe tener scope_type='department'
- 'colaborador' NO debe tener UserScope
- 'guest' NO debe tener UserScope

**Índices:**
- PK en id
- FK indexed en user_id
- UNIQUE en (user_id, scope_type, scope_id)
- INDEX en (scope_type, scope_id)
- INDEX en is_active

**Lógica de permisos por rol:**

**ADMIN:**
- Sin UserScope → Acceso GLOBAL (ve todos los business_groups)
- Con UserScope business_group → Ve solo ese BusinessGroup
- Con UserScope company → Ve solo esa Company
- Permisos: crear, editar, eliminar en su scope

**GERENTE:**
- Requiere UserScope obligatorio
- Con scope company → Ve toda la Company (todas sus branches)
- Con scope branch → Ve solo esa Branch
- Permisos: crear, editar en su scope (NO eliminar)

**GESTOR:**
- Requiere UserScope obligatorio
- Con scope department → Ve solo ese Department
- Permisos: editar en su scope (NO crear, NO eliminar)

**COLABORADOR:**
- Sin UserScope
- Solo ve employee vinculado a su user_id
- Permisos: solo lectura de sus propios datos

**GUEST:**
- Sin acceso a employees

**Funciones en core/permissions.py:**

**can_access_employee(user, employee) → bool:**
Verifica si user puede acceder al employee según su rol y scope

**get_user_scope(user) → dict:**
Retorna scope del user

**filter_employees_by_user(user, query) → query:**
Aplica filtro automático según scope

**can_create_employee(user, company_id) → bool:**
Verifica si user puede crear employee en esa company

**can_edit_employee(user, employee) → bool:**
Verifica si user puede editar ese employee

**can_delete_employee(user, employee) → bool:**
Verifica si user puede eliminar ese employee

**Endpoints:**
- POST /api/v1/users/{user_id}/scope
- GET /api/v1/users/{user_id}/scope
- PUT /api/v1/users/{user_id}/scope
- DELETE /api/v1/users/{user_id}/scope
- GET /api/v1/auth/me/scope

**Seed data:**
- 1 admin sin scope (global)
- 1 admin con scope business_group
- 2 gerentes con scope company
- 2 gestores con scope department
- 3 colaboradores sin scope

**Testing:**
- Asignar scope válido según rol
- Validar scope inválido para rol (400)
- Validar scope_id inexistente (404)
- Probar can_access_employee con cada rol
- Probar filtrado automático por scope
- Verificar admin global ve todo
- Verificar gerente solo ve su company
- Verificar gestor solo ve su department
- Verificar colaborador solo ve sus datos
- Probar permisos de crear/editar/eliminar por rol

---

## MATRIZ DE PERMISOS RESUMIDA

| Rol | Scope requerido | Ve | Crear | Editar | Eliminar |
|-----|-----------------|-----|-------|--------|----------|
| admin | No (global) / business_group / company | Todo en su scope | ✅ | ✅ | ✅ |
| gerente | company / branch | Su company/branch | ✅ | ✅ | ❌ |
| gestor | department | Su department | ❌ | ✅ | ❌ |
| colaborador | No | Solo sus datos | ❌ | ✅ (sus datos) | ❌ |
| guest | No | Nada | ❌ | ❌ | ❌ |

---

## CICLO DE DESARROLLO POR ENTIDAD

**Pasos obligatorios:**

1. **Model** - Crear archivo en models/
2. **Migration** - alembic revision + upgrade
3. **Seed** - Script de datos de prueba
4. **Schemas** - Create, Update, Response
5. **Repository** - CRUD + métodos especiales
6. **Service** - Validaciones de negocio
7. **Controller** - Endpoints REST
8. **Testing** - cURL + Swagger (todos los casos)

---

## CRITERIOS DE ÉXITO MVP

**Funcional:**
- ✅ Admin global ve todos los employees
- ✅ Admin de business_group ve solo su grupo
- ✅ Gerente de company ve solo su company
- ✅ Gestor de department ve solo su department
- ✅ Colaborador solo ve sus datos
- ✅ Búsqueda respeta scopes
- ✅ Jerarquía de supervisión funciona

**Técnico:**
- ✅ 8 entidades creadas con seed data
- ✅ Migraciones aplicadas
- ✅ Endpoints funcionando con permisos
- ✅ Filtrado automático por scope
- ✅ Validaciones correctas

**Testing:**
- ✅ Probado con cada rol
- ✅ Verificado filtrado en BD
- ✅ Probado con cURL y Swagger

---

## NOTAS FINALES

- Usar siempre soft delete (is_active)
- Todas las FKs deben tener ON DELETE RESTRICT
- Timestamps automáticos en created_at/updated_at
- Índices en todas las FKs
- Paginación obligatoria en listados (skip/limit)
- Búsquedas case-insensitive
- Validar permisos en TODOS los endpoints de Employee
- Individual se llama así para diferenciarse de Person (entidad ejemplo previa)
- BusinessGroup es nueva entidad (no existe previamente)

---

**Este prompt define claramente las 8 entidades a crear, sus especificaciones completas, validaciones, relaciones, endpoints y sistema de permisos. Listo para implementación incremental.**