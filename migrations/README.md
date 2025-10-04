# Migraciones de Base de Datos

## Aplicar Migración: Add User Soft Delete Fields

Esta migración agrega los campos `deleted_at` y `deleted_by` a la tabla `users` para completar la auditoría del soft delete.

### Opción 1: Con psql (recomendado)

```bash
psql -U postgres -d bapta_simple_template -f migrations/add_user_soft_delete_fields.sql
```

### Opción 2: Con Python

```python
from database import engine
from sqlalchemy import text

with open('migrations/add_user_soft_delete_fields.sql', 'r') as f:
    sql = f.read()

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()
```

### Opción 3: Desde Python (ejecutar este script)

```bash
python -c "
from database import engine
from sqlalchemy import text

with open('migrations/add_user_soft_delete_fields.sql', 'r') as f:
    sql = f.read()

with engine.begin() as conn:
    for statement in sql.split(';'):
        if statement.strip():
            conn.execute(text(statement))

print('Migración aplicada exitosamente')
"
```

## Verificar Migración

```sql
-- Ver estructura de la tabla users
\d users

-- O con SQL
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN ('deleted_at', 'deleted_by');
```

## Cambios Realizados

1. **Modelo User** (`database.py`):
   - Agregado `deleted_at = Column(DateTime, nullable=True)`
   - Agregado `deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)`
   - Agregado relación `deleted_by_user`

2. **PersonRepository** (`person_repository.py`):
   - `soft_delete_person()` ahora actualiza `deleted_at` y `deleted_by`

3. **PersonService** (`person_service.py`):
   - `_validate_deletion_rules()` ahora elimina el usuario asociado (si existe)
   - Al eliminar Person con usuario, ambos se eliminan con soft delete

## Funcionalidad Nueva

Al eliminar una persona:
1. Se actualiza `is_deleted = True`
2. Se actualiza `deleted_at = ahora()`
3. Se actualiza `deleted_by = current_user_id`
4. Si tiene usuario asociado, el usuario también se elimina con soft delete
