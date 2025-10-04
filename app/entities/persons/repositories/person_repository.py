"""
Repository para la entidad Person

Este repository extiende BaseRepository con funcionalidades específicas
de Person, manteniendo compatibilidad con el comportamiento existente
del módulo modules/persons/.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.shared.base_repository import BaseRepository
from app.entities.persons.models.person import Person
from app.entities.persons.schemas.enums import PersonStatusEnum
from app.shared.exceptions import EntityNotFoundError, EntityAlreadyExistsError


class PersonRepository(BaseRepository[Person]):
    """
    Repository específico para Person con funcionalidades avanzadas.

    Mantiene compatibilidad total con el comportamiento existente
    en modules/persons/routes.py mientras añade nuevas capacidades.
    """

    def __init__(self, db: Session):
        super().__init__(Person, db)

    # ==================== MÉTODOS DE COMPATIBILIDAD ====================

    def get_active_persons(self) -> List[Person]:
        """
        Obtiene todas las personas activas.

        Mantiene compatibilidad con GET /persons/ existente.
        """
        return self.db.query(Person).filter(Person.is_active == True).all()

    def find_by_email(self, email: str) -> Optional[Person]:
        """
        Busca persona por email.

        Usado para validar unicidad de email.
        """
        return self.db.query(Person).filter(Person.email == email).first()

    def search_with_filters(
        self,
        name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 100,
        order_by: str = "id",
        order_desc: bool = False,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> List[Person]:
        """
        Búsqueda avanzada con filtros dinámicos.

        Mantiene compatibilidad total con GET /persons/search existente.
        Replica exactamente la lógica de modules/persons/routes.py
        """
        # Query base - solo personas activas
        query = self.db.query(Person).filter(Person.is_active == True)

        # Filtros específicos (compatibilidad con API existente)
        if name:
            query = query.filter(Person.first_name.ilike(f"%{name}%"))
        if last_name:
            query = query.filter(Person.last_name.ilike(f"%{last_name}%"))
        if email:
            query = query.filter(Person.email.ilike(f"%{email}%"))
        if phone:
            # Búsqueda en array de teléfonos del nuevo modelo
            query = query.filter(
                or_(
                    Person.phone_numbers.any(phone),  # Nuevo campo array
                    func.cast(Person.phone_numbers, str).ilike(f"%{phone}%")  # Fallback
                )
            )
        if status:
            query = query.filter(Person.status == status)
        if user_id:
            query = query.filter(Person.user_id == user_id)

        # Búsqueda global (compatibilidad exacta)
        if search:
            search_filter = or_(
                Person.first_name.ilike(f"%{search}%"),
                Person.last_name.ilike(f"%{search}%"),
                Person.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Filtros dinámicos adicionales (nueva funcionalidad)
        if additional_filters:
            for key, value in additional_filters.items():
                if hasattr(Person, key) and value:
                    attr = getattr(Person, key)
                    if key in ['id', 'user_id']:
                        query = query.filter(attr == int(value))
                    elif key in ['is_active', 'is_deleted']:
                        query = query.filter(attr == (str(value).lower() == 'true'))
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
        return query.offset(offset).limit(limit).all()

    def create_person_compatible(self, person_data: Dict[str, Any]) -> Person:
        """
        Crea persona manteniendo compatibilidad con estructura existente.

        Mapea campos del formato antiguo al nuevo modelo extendido.
        """
        # Validar email único
        if self.find_by_email(person_data.get('email')):
            raise EntityAlreadyExistsError("Person", "email", person_data.get('email'))

        # Mapear campos del formato antiguo al nuevo
        mapped_data = self._map_legacy_to_new_format(person_data)

        return self.create(mapped_data)

    def update_person_compatible(
        self,
        person_id: int,
        update_data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> Person:
        """
        Actualiza persona manteniendo compatibilidad.
        """
        person = self.get_by_id(person_id)
        if not person:
            raise EntityNotFoundError("Person", person_id)

        # Validar email único si se está cambiando
        if 'email' in update_data and update_data['email'] != person.email:
            if self.find_by_email(update_data['email']):
                raise EntityAlreadyExistsError("Person", "email", update_data['email'])

        # Mapear datos del formato antiguo
        mapped_data = self._map_legacy_to_new_format(update_data)

        # Agregar auditoría
        if updated_by:
            mapped_data['updated_by'] = updated_by

        return self.update(person_id, mapped_data)

    def soft_delete_person(self, person_id: int, deleted_by: Optional[int] = None) -> bool:
        """
        Soft delete manteniendo compatibilidad exacta con auditoría completa.
        """
        from datetime import datetime

        person = self.get_by_id(person_id)
        if not person:
            raise EntityNotFoundError("Person", person_id)

        # Soft delete con campos de auditoría completos
        update_data = {
            'is_active': False,
            'is_deleted': True,
            'deleted_at': datetime.utcnow(),
            'deleted_by': deleted_by,
            'updated_by': deleted_by  # También actualizar updated_by
        }

        self.update(person_id, update_data)
        return True

    # ==================== NUEVAS FUNCIONALIDADES EXTENDIDAS ====================

    def find_by_document(self, document_number: str) -> Optional[Person]:
        """Nueva funcionalidad: buscar por documento."""
        return self.db.query(Person).filter(
            Person.document_number == document_number
        ).first()

    def find_by_phone_array(self, phone: str) -> List[Person]:
        """Nueva funcionalidad: buscar en array de teléfonos."""
        return self.db.query(Person).filter(
            Person.phone_numbers.any(phone)
        ).all()

    def get_by_status_enum(self, status: PersonStatusEnum) -> List[Person]:
        """Nueva funcionalidad: filtrar por enum de status."""
        return self.db.query(Person).filter(
            Person.status == status,
            Person.is_active == True
        ).all()

    def get_persons_with_user(self) -> List[Person]:
        """Nueva funcionalidad: personas que tienen usuario asociado."""
        return self.db.query(Person).filter(
            Person.user_id.isnot(None),
            Person.is_active == True
        ).all()

    def get_verified_persons(self) -> List[Person]:
        """Nueva funcionalidad: personas verificadas."""
        return self.db.query(Person).filter(
            Person.is_verified == True,
            Person.is_active == True
        ).all()

    def search_by_skills(self, skill: str) -> List[Person]:
        """Nueva funcionalidad: buscar por habilidades en skill_details (JSONB)."""
        from sqlalchemy import cast, String
        return self.db.query(Person).filter(
            cast(Person.skill_details, String).ilike(f'%"name": "{skill}"%'),
            Person.is_active == True
        ).all()

    # ==================== MÉTODOS AVANZADOS DE SKILLS ====================

    def search_by_skill_category(self, category: str) -> List[Person]:
        """Buscar personas por categoría de skill."""
        return self.db.query(Person).filter(
            Person.skill_details.op('?')([{"category": category}]),
            Person.is_active == True
        ).all()

    def search_by_skill_level(self, skill_name: str, level: str) -> List[Person]:
        """Buscar personas con skill específica en nivel mínimo."""
        return self.db.query(Person).filter(
            Person.skill_details.op('@>')([{"name": skill_name, "level": level}]),
            Person.is_active == True
        ).all()

    def get_persons_with_expert_skills(self) -> List[Person]:
        """Obtener personas con al menos una skill de nivel EXPERT o MASTER."""
        return self.db.query(Person).filter(
            or_(
                Person.skill_details.op('@>')([{"level": "EXPERT"}]),
                Person.skill_details.op('@>')([{"level": "MASTER"}])
            ),
            Person.is_active == True
        ).all()

    def search_by_skill_and_experience(self, skill_name: str, min_years: int) -> List[Person]:
        """Buscar personas con skill y años mínimos de experiencia."""
        return self.db.query(Person).filter(
            Person.skill_details.op('@>')([{"name": skill_name}]),
            Person.skill_details.op('?')([{"years_experience": min_years}]),
            Person.is_active == True
        ).all()

    def get_skills_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas globales de skills."""
        total_persons = self.db.query(Person).filter(Person.is_active == True).count()
        persons_with_skills = self.db.query(Person).filter(
            Person.skills.isnot(None),
            func.array_length(Person.skills, 1) > 0,
            Person.is_active == True
        ).count()

        persons_with_detailed_skills = self.db.query(Person).filter(
            Person.skill_details.isnot(None),
            Person.is_active == True
        ).count()

        return {
            "total_persons": total_persons,
            "persons_with_skills": persons_with_skills,
            "persons_with_detailed_skills": persons_with_detailed_skills,
            "percentage_with_skills": round((persons_with_skills / total_persons * 100), 2) if total_persons > 0 else 0
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Nueva funcionalidad: estadísticas de personas."""
        total = self.db.query(Person).count()
        active = self.db.query(Person).filter(Person.is_active == True).count()
        verified = self.db.query(Person).filter(Person.is_verified == True).count()
        with_user = self.db.query(Person).filter(Person.user_id.isnot(None)).count()

        return {
            "total_persons": total,
            "active_persons": active,
            "verified_persons": verified,
            "persons_with_user": with_user,
            "inactive_persons": total - active
        }

    # ==================== MÉTODOS PRIVADOS ====================

    def _map_legacy_to_new_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapea datos del formato legacy al nuevo modelo extendido.

        Mantiene compatibilidad mapeando:
        - name -> first_name
        - Campos adicionales se mantienen igual
        """
        mapped = data.copy()

        # Mapear name del formato antiguo a first_name del nuevo
        if 'name' in mapped:
            mapped['first_name'] = mapped.pop('name')

        # Si viene phone como string, convertir a array
        if 'phone' in mapped and mapped['phone']:
            if not mapped.get('phone_numbers'):
                mapped['phone_numbers'] = [mapped['phone']]

        # Mapear status string a enum si es necesario
        if 'status' in mapped and isinstance(mapped['status'], str):
            try:
                # Convertir a mayúsculas para compatibilidad con enum
                mapped['status'] = PersonStatusEnum(mapped['status'].upper())
            except ValueError:
                # Si no es un enum válido, usar ACTIVE por defecto
                mapped['status'] = PersonStatusEnum.ACTIVE

        return mapped

    def _prepare_legacy_response(self, person: Person) -> Dict[str, Any]:
        """
        Prepara respuesta en formato legacy para mantener compatibilidad.
        """
        return {
            "id": person.id,
            "user_id": person.user_id,
            "name": person.first_name,  # Mapear de vuelta
            "last_name": person.last_name,
            "email": person.email,
            "phone": person.primary_phone,  # Primer teléfono del array
            "address": person.address_street,  # Campo principal de dirección
            "status": person.status.value if person.status else "active",
            "is_active": person.is_active,
            "created_at": person.created_at,
            "updated_at": person.updated_at
        }