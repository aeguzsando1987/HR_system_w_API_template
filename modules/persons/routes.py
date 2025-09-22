from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func

from database import get_db, User
from auth import require_admin, require_manager_or_admin, require_collaborator_or_better, require_any_user
from .models import Person
from .schemas import PersonCreate, PersonUpdate, PersonWithUserCreate, PersonResponse

router = APIRouter(prefix="/persons", tags=["persons"])

@router.post("/", summary="Crear persona")
def create_person(person_data: PersonCreate, db: Session = Depends(get_db), current_user = Depends(require_collaborator_or_better)):
    # Verificar si el email ya existe
    if db.query(Person).filter(Person.email == person_data.email).first():
        raise HTTPException(status_code=400, detail="Email ya existe")

    # Crear persona
    person = Person(**person_data.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return {"id": person.id, "name": person.name, "last_name": person.last_name, "email": person.email}


# Listar personas
@router.get("/", response_model=List[PersonResponse], summary="Listar personas")
def get_persons(db: Session = Depends(get_db), current_user = Depends(require_any_user)):
    persons = db.query(Person).filter(Person.is_active == True).all()
    return persons


# Buscar personas con filtros dinámicos
@router.get("/search", response_model=List[PersonResponse], summary="Buscar personas con filtros dinámicos")
def search_persons(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_any_user),
    # Filtros específicos comunes
    name: Optional[str] = Query(None, description="Filtrar por nombre"),
    last_name: Optional[str] = Query(None, description="Filtrar por apellido"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    phone: Optional[str] = Query(None, description="Filtrar por teléfono"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    user_id: Optional[int] = Query(None, description="Filtrar por user_id"),
    # Filtros de búsqueda
    search: Optional[str] = Query(None, description="Búsqueda global en name, last_name, email"),
    # Paginación
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(100, ge=1, le=1000, description="Registros por página"),
    # Ordenamiento
    order_by: Optional[str] = Query("id", description="Campo para ordenar"),
    order_desc: bool = Query(False, description="Orden descendente")
):
    # Iniciar query base
    query = db.query(Person).filter(Person.is_active == True)

    # Aplicar filtros específicos
    if name:
        query = query.filter(Person.name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(Person.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Person.email.ilike(f"%{email}%"))
    if phone:
        query = query.filter(Person.phone.ilike(f"%{phone}%"))
    if status:
        query = query.filter(Person.status == status)
    if user_id:
        query = query.filter(Person.user_id == user_id)

    # Búsqueda global
    if search:
        search_filter = or_(
            Person.name.ilike(f"%{search}%"),
            Person.last_name.ilike(f"%{search}%"),
            Person.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Aplicar filtros dinámicos adicionales de query params
    for key, value in request.query_params.items():
        if key not in ['name', 'last_name', 'email', 'phone', 'status', 'user_id', 'search', 'page', 'limit', 'order_by', 'order_desc']:
            if hasattr(Person, key) and value:
                # Obtener el atributo de la clase
                attr = getattr(Person, key)
                # Aplicar filtro según el tipo
                if key in ['id', 'user_id']:
                    query = query.filter(attr == int(value))
                elif key in ['is_active', 'is_deleted']:
                    query = query.filter(attr == (value.lower() == 'true'))
                else:
                    query = query.filter(attr.ilike(f"%{value}%"))

    # Ordenamiento
    if order_by and hasattr(Person, order_by):
        order_attr = getattr(Person, order_by)
        if order_desc:
            query = query.order_by(order_attr.desc())
        else:
            query = query.order_by(order_attr)

    # Paginación
    offset = (page - 1) * limit
    persons = query.offset(offset).limit(limit).all()

    return persons


# Obtener persona específica
@router.get("/{person_id}", response_model=PersonResponse, summary="Obtener persona específica")
def get_person(person_id: int, db: Session = Depends(get_db), current_user = Depends(require_any_user)):
    person = db.query(Person).filter(Person.id == person_id, Person.is_active == True).first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return person

@router.put("/{person_id}", summary="Actualizar persona")
def update_person(person_id: int, person_data: PersonUpdate, db: Session = Depends(get_db), current_user = Depends(require_collaborator_or_better)):
    person = db.query(Person).filter(Person.id == person_id, Person.is_active == True).first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # Verificar email único si se está cambiando
    if person_data.email and person_data.email != person.email:
        if db.query(Person).filter(Person.email == person_data.email).first():
            raise HTTPException(status_code=400, detail="Email ya existe")

    # Actualizar campos
    update_data = person_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Validar user_id si se está actualizando
        if field == "user_id" and value is not None and value != 0:
            # Verificar que el usuario existe
            if not db.query(User).filter(User.id == value).first():
                raise HTTPException(status_code=400, detail="Usuario no encontrado")
        # Si user_id es 0, convertir a None para FK opcional
        if field == "user_id" and value == 0:
            value = None
        setattr(person, field, value)

    person.updated_by = current_user.id
    db.commit()
    db.refresh(person)
    return {"id": person.id, "name": person.name, "last_name": person.last_name, "email": person.email}

@router.delete("/{person_id}", summary="Eliminar persona (soft delete)")
def delete_person(person_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    person = db.query(Person).filter(Person.id == person_id, Person.is_active == True).first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # Soft delete
    person.is_active = False
    person.is_deleted = True
    person.updated_by = current_user.id
    db.commit()
    return {"message": "Persona eliminada correctamente"}

@router.post("/with-user", summary="Crear persona con usuario asociado")
def create_person_with_user(data: PersonWithUserCreate, db: Session = Depends(get_db), current_user = Depends(require_manager_or_admin)):
    # Verificar si el email del usuario ya existe
    if db.query(User).filter(User.email == data.user_email).first():
        raise HTTPException(status_code=400, detail="Email de usuario ya existe")

    # Verificar si el email de la persona ya existe
    if db.query(Person).filter(Person.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email de persona ya existe")

    try:
        # Crear usuario
        from auth import hash_password
        user = User(
            email=data.user_email,
            name=data.user_name,
            password_hash=hash_password(data.user_password),
            role=data.user_role
        )
        db.add(user)
        db.flush()  # Para obtener el ID sin hacer commit

        # Crear persona asociada al usuario
        person = Person(
            user_id=user.id,
            name=data.name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            address=data.address,
            status=data.status
        )
        db.add(person)
        db.commit()
        db.refresh(user)
        db.refresh(person)

        return {
            "user": {"id": user.id, "email": user.email, "name": user.name},
            "person": {"id": person.id, "name": person.name, "last_name": person.last_name, "email": person.email}
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando usuario y persona: {str(e)}")