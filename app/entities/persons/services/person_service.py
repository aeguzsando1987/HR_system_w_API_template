"""
Service Layer para Person

Contiene la lógica de negocio y coordina operaciones entre
Repository y Controller, manteniendo compatibilidad con el
comportamiento existente.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.entities.persons.repositories.person_repository import PersonRepository
from app.entities.persons.models.person import Person
from app.entities.persons.schemas.enums import PersonStatusEnum
from app.entities.states.repositories.state_repository import StateRepository
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    BusinessRuleError,
    EntityValidationError
)
from app.shared.validators import (
    validate_email,
    validate_phone,
    validate_non_empty_string,
    validate_phone_list,
    validate_age,
    validate_birth_date
)


class PersonService:
    """
    Service para manejar lógica de negocio de Person.

    Coordina operaciones entre Repository y Controllers,
    aplicando validaciones de negocio y manteniendo
    compatibilidad con endpoints existentes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = PersonRepository(db)
        self.state_repository = StateRepository(db)

    # ==================== VALIDACIONES GEOGRÁFICAS ====================

    def _validate_state_country_consistency(self, country_id: Optional[int], state_id: Optional[int]) -> None:
        """
        Valida que el estado pertenezca al pais seleccionado.

        Raises:
            BusinessRuleError: Si el estado no pertenece al pais
        """
        # Si no hay state_id, no hay nada que validar
        if not state_id:
            return

        # Si hay state_id, debe haber country_id
        if state_id and not country_id:
            raise BusinessRuleError("Si especifica un estado, debe especificar tambien un pais")

        # Verificar que el estado existe y pertenece al pais
        state = self.state_repository.get_by_id(state_id)
        if not state:
            raise EntityNotFoundError(f"Estado con ID {state_id} no encontrado")

        if state.country_id != country_id:
            raise BusinessRuleError(
                f"El estado '{state.name}' no pertenece al pais seleccionado. "
                f"El estado pertenece al pais con ID {state.country_id}"
            )

    # ==================== MÉTODOS DE COMPATIBILIDAD ====================

    def get_all_active_persons(self) -> List[Person]:
        """
        Obtiene todas las personas activas.

        Compatibilidad: GET /persons/
        """
        return self.repository.get_active_persons()

    def search_persons(
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
        Búsqueda avanzada con filtros.

        Compatibilidad: GET /persons/search
        """
        # Validar parámetros de paginación
        if page < 1:
            raise BusinessRuleError("El número de página debe ser mayor a 0")
        if limit < 1 or limit > 1000:
            raise BusinessRuleError("El límite debe estar entre 1 y 1000")

        return self.repository.search_with_filters(
            name=name,
            last_name=last_name,
            email=email,
            phone=phone,
            status=status,
            user_id=user_id,
            search=search,
            page=page,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc,
            additional_filters=additional_filters
        )

    def get_person_by_id(self, person_id: int) -> Person:
        """
        Obtiene persona por ID.

        Compatibilidad: GET /persons/{person_id}
        """
        person = self.repository.get_by_id(person_id)
        if not person or not person.is_active:
            raise EntityNotFoundError("Person", person_id)
        return person

    def create_person_legacy(self, person_data: Dict[str, Any]) -> Person:
        """
        Crea persona manteniendo compatibilidad con formato legacy.

        Compatibilidad: POST /persons/
        """
        # Validaciones de negocio
        self._validate_person_data(person_data)

        # Validar email único
        if self.repository.find_by_email(person_data.get('email')):
            raise EntityAlreadyExistsError("Person", "email", person_data.get('email'))

        # Validar user_id si se proporciona
        if person_data.get('user_id'):
            self._validate_user_exists(person_data['user_id'])

        # Validar consistencia geografica (state pertenece a country)
        self._validate_state_country_consistency(
            person_data.get('country_id'),
            person_data.get('state_id')
        )

        return self.repository.create_person_compatible(person_data)

    def update_person_legacy(
        self,
        person_id: int,
        update_data: Dict[str, Any],
        updated_by: Optional[int] = None
    ) -> Person:
        """
        Actualiza persona manteniendo compatibilidad.

        Compatibilidad: PUT /persons/{person_id}
        """
        # Verificar que la persona existe y está activa
        person = self.get_person_by_id(person_id)

        # Validar datos si se proporcionan
        if update_data:
            self._validate_person_data(update_data, is_update=True)

        # Validar email único si se está cambiando
        if 'email' in update_data and update_data['email'] != person.email:
            if self.repository.find_by_email(update_data['email']):
                raise EntityAlreadyExistsError("Person", "email", update_data['email'])

        # Validar consistencia geografica si se actualizan country/state
        country_id = update_data.get('country_id', person.country_id)
        state_id = update_data.get('state_id', person.state_id)
        self._validate_state_country_consistency(country_id, state_id)

        # Validar user_id si se está actualizando
        if 'user_id' in update_data:
            if update_data['user_id'] == 0:
                update_data['user_id'] = None  # Compatibilidad: 0 -> None
            elif update_data['user_id']:
                self._validate_user_exists(update_data['user_id'])

        return self.repository.update_person_compatible(person_id, update_data, updated_by)

    def delete_person(self, person_id: int, deleted_by: Optional[int] = None) -> bool:
        """
        Elimina persona (soft delete).

        Compatibilidad: DELETE /persons/{person_id}
        """
        # Verificar que existe y está activa
        self.get_person_by_id(person_id)

        # Aplicar reglas de negocio para eliminación (elimina usuario asociado si existe)
        self._validate_deletion_rules(person_id, deleted_by)

        return self.repository.soft_delete_person(person_id, deleted_by)

    def create_person_with_user(
        self,
        user_data: Dict[str, Any],
        person_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Crea persona con usuario asociado en transacción atómica.

        Compatibilidad: POST /persons/with-user
        """
        # Validar datos de usuario
        self._validate_user_data(user_data)

        # Validar datos de persona
        self._validate_person_data(person_data)

        # Validar emails únicos
        if self._email_exists_in_users(user_data['user_email']):
            raise EntityAlreadyExistsError("User", "email", user_data['user_email'])

        if self.repository.find_by_email(person_data['email']):
            raise EntityAlreadyExistsError("Person", "email", person_data['email'])

        try:
            # Crear usuario primero
            from database import User
            from auth import hash_password

            user = User(
                email=user_data['user_email'],
                name=user_data['user_name'],
                password_hash=hash_password(user_data['user_password']),
                role=user_data.get('user_role', 4)
            )
            self.db.add(user)
            self.db.flush()  # Obtener ID sin commit

            # Crear persona asociada
            person_data['user_id'] = user.id
            person = self.repository.create_person_compatible(person_data)

            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(person)

            return (
                {"id": user.id, "email": user.email, "name": user.name},
                {"id": person.id, "name": person.first_name, "last_name": person.last_name, "email": person.email}
            )

        except Exception as e:
            self.db.rollback()
            raise BusinessRuleError(f"Error creando usuario y persona: {str(e)}")

    # ==================== NUEVAS FUNCIONALIDADES EXTENDIDAS ====================

    def create_person_extended(self, person_data: Dict[str, Any]) -> Person:
        """
        Crear persona con todas las funcionalidades extendidas del nuevo modelo.
        """
        # Validaciones extendidas
        self._validate_extended_person_data(person_data)

        # Validaciones de unicidad
        if person_data.get('email') and self.repository.find_by_email(person_data['email']):
            raise EntityAlreadyExistsError("Person", "email", person_data['email'])

        if person_data.get('document_number') and self.repository.find_by_document(person_data['document_number']):
            raise EntityAlreadyExistsError("Person", "document_number", person_data['document_number'])

        return self.repository.create(person_data)

    def find_by_document(self, document_number: str) -> Optional[Person]:
        """Nueva funcionalidad: buscar por documento."""
        return self.repository.find_by_document(document_number)

    def find_by_phone_number(self, phone: str) -> List[Person]:
        """Nueva funcionalidad: buscar por teléfono en array."""
        validated_phone = validate_phone(phone)
        return self.repository.find_by_phone_array(validated_phone)

    def get_persons_by_status(self, status: PersonStatusEnum) -> List[Person]:
        """Nueva funcionalidad: filtrar por enum de status."""
        return self.repository.get_by_status_enum(status)

    def get_verified_persons(self) -> List[Person]:
        """Nueva funcionalidad: obtener personas verificadas."""
        return self.repository.get_verified_persons()

    def verify_person(self, person_id: int, verified_by: int) -> Person:
        """Nueva funcionalidad: verificar persona."""
        person = self.get_person_by_id(person_id)

        # Validar que tiene los datos mínimos para verificación
        if not person.document_number:
            raise BusinessRuleError("No se puede verificar persona sin número de documento")

        if not person.email and not person.phone_numbers:
            raise BusinessRuleError("No se puede verificar persona sin email o teléfono")

        update_data = {
            'is_verified': True,
            'updated_by': verified_by
        }

        return self.repository.update(person_id, update_data)

    def search_by_skills(self, skill: str) -> List[Person]:
        """Nueva funcionalidad: buscar por habilidades."""
        return self.repository.search_by_skills(skill)

    # ==================== SERVICIOS AVANZADOS DE SKILLS ====================

    def add_skill_to_person(
        self,
        person_id: int,
        skill_name: str,
        category: str,
        level: str,
        years_experience: int = 0,
        notes: Optional[str] = None,
        updated_by: Optional[int] = None
    ) -> Person:
        """
        Añadir skill detallada a una persona.
        """
        person = self.get_person_by_id(person_id)

        # Validar enums
        from app.entities.persons.schemas.enums import SkillCategoryEnum, SkillLevelEnum
        try:
            SkillCategoryEnum(category)
            SkillLevelEnum(level)
        except ValueError as e:
            raise BusinessRuleError(f"Categoría o nivel de skill inválido: {str(e)}")

        # Validar años de experiencia
        if years_experience < 0:
            raise BusinessRuleError("Los años de experiencia no pueden ser negativos")

        # Añadir skill usando método del modelo
        person.add_skill_detail(skill_name, category, level, years_experience, notes)

        # Actualizar auditoría
        if updated_by:
            person.updated_by = updated_by

        self.db.commit()
        self.db.refresh(person)
        return person

    def remove_skill_from_person(
        self,
        person_id: int,
        skill_name: str,
        updated_by: Optional[int] = None
    ) -> Person:
        """
        Eliminar skill de una persona.
        """
        person = self.get_person_by_id(person_id)

        # Eliminar skill usando método del modelo
        removed = person.remove_skill(skill_name)

        if not removed:
            raise BusinessRuleError(f"La persona no tiene la skill '{skill_name}'")

        # Actualizar auditoría
        if updated_by:
            person.updated_by = updated_by

        self.db.commit()
        self.db.refresh(person)
        return person

    def search_by_skill_category(self, category: str) -> List[Person]:
        """Buscar personas por categoría de skill."""
        # Validar categoría
        from app.entities.persons.schemas.enums import SkillCategoryEnum
        try:
            SkillCategoryEnum(category)
        except ValueError:
            raise BusinessRuleError(f"Categoría de skill inválida: {category}")

        return self.repository.search_by_skill_category(category)

    def search_by_skill_level(self, skill_name: str, level: str) -> List[Person]:
        """Buscar personas con skill específica en nivel mínimo."""
        # Validar nivel
        from app.entities.persons.schemas.enums import SkillLevelEnum
        try:
            SkillLevelEnum(level)
        except ValueError:
            raise BusinessRuleError(f"Nivel de skill inválido: {level}")

        return self.repository.search_by_skill_level(skill_name, level)

    def get_persons_with_expert_skills(self) -> List[Person]:
        """Obtener personas con skills de nivel experto."""
        return self.repository.get_persons_with_expert_skills()

    def search_by_skill_and_experience(self, skill_name: str, min_years: int) -> List[Person]:
        """Buscar personas con skill y años mínimos de experiencia."""
        if min_years < 0:
            raise BusinessRuleError("Los años mínimos de experiencia no pueden ser negativos")

        return self.repository.search_by_skill_and_experience(skill_name, min_years)

    def get_person_skills_summary(self, person_id: int) -> Dict[str, Any]:
        """Obtener resumen de skills de una persona."""
        person = self.get_person_by_id(person_id)
        return person.get_skills_summary()

    def get_person_skills_by_category(self, person_id: int, category: str) -> List[Dict[str, Any]]:
        """Obtener skills de una persona filtradas por categoría."""
        person = self.get_person_by_id(person_id)

        # Validar categoría
        from app.entities.persons.schemas.enums import SkillCategoryEnum
        try:
            SkillCategoryEnum(category)
        except ValueError:
            raise BusinessRuleError(f"Categoría de skill inválida: {category}")

        return person.get_skills_by_category(category)

    def get_person_expert_skills(self, person_id: int) -> List[Dict[str, Any]]:
        """Obtener skills de nivel experto de una persona."""
        person = self.get_person_by_id(person_id)
        return person.get_expert_skills()

    def validate_person_skill_requirements(
        self,
        person_id: int,
        required_skills: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Validar si una persona cumple con requisitos de skills.

        Args:
            person_id: ID de la persona
            required_skills: Lista de skills requeridas con nivel mínimo
                [{"name": "Python", "level": "ADVANCED"}, ...]

        Returns:
            Diccionario con resultado de validación
        """
        person = self.get_person_by_id(person_id)

        validation_result = {
            "person_id": person_id,
            "person_name": person.full_name,
            "meets_requirements": True,
            "skills_validation": [],
            "missing_skills": [],
            "insufficient_level_skills": []
        }

        for required_skill in required_skills:
            skill_name = required_skill.get("name")
            required_level = required_skill.get("level")

            skill_validation = {
                "skill_name": skill_name,
                "required_level": required_level,
                "has_skill": False,
                "current_level": None,
                "meets_requirement": False
            }

            # Verificar si tiene la skill
            skill_detail = person.get_skill_detail(skill_name)

            if skill_detail:
                skill_validation["has_skill"] = True
                skill_validation["current_level"] = skill_detail.get("level")

                # Verificar nivel
                if person.has_skill_at_level(skill_name, required_level):
                    skill_validation["meets_requirement"] = True
                else:
                    skill_validation["meets_requirement"] = False
                    validation_result["insufficient_level_skills"].append(skill_name)
                    validation_result["meets_requirements"] = False
            else:
                validation_result["missing_skills"].append(skill_name)
                validation_result["meets_requirements"] = False

            validation_result["skills_validation"].append(skill_validation)

        return validation_result

    def get_skills_global_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas globales de skills."""
        return self.repository.get_skills_statistics()

    def update_skill_level(
        self,
        person_id: int,
        skill_name: str,
        new_level: str,
        years_experience: Optional[int] = None,
        notes: Optional[str] = None,
        updated_by: Optional[int] = None
    ) -> Person:
        """
        Actualizar nivel de una skill existente.
        """
        person = self.get_person_by_id(person_id)

        # Verificar que la skill existe
        skill_detail = person.get_skill_detail(skill_name)
        if not skill_detail:
            raise BusinessRuleError(f"La persona no tiene la skill '{skill_name}'")

        # Validar nuevo nivel
        from app.entities.persons.schemas.enums import SkillLevelEnum
        try:
            SkillLevelEnum(new_level)
        except ValueError:
            raise BusinessRuleError(f"Nivel de skill inválido: {new_level}")

        # Actualizar skill (eliminar y volver a agregar con nuevos datos)
        category = skill_detail.get("category")
        updated_years = years_experience if years_experience is not None else skill_detail.get("years_experience", 0)
        updated_notes = notes if notes is not None else skill_detail.get("notes")

        person.remove_skill(skill_name)
        person.add_skill_detail(skill_name, category, new_level, updated_years, updated_notes)

        # Actualizar auditoría
        if updated_by:
            person.updated_by = updated_by

        self.db.commit()
        self.db.refresh(person)
        return person

    def get_person_statistics(self) -> Dict[str, Any]:
        """Nueva funcionalidad: obtener estadísticas."""
        return self.repository.get_statistics()

    def calculate_person_age(self, person_id: int) -> Optional[int]:
        """Nueva funcionalidad: calcular edad desde fecha de nacimiento."""
        person = self.get_person_by_id(person_id)
        return person.calculated_age

    def get_person_bmi(self, person_id: int) -> Optional[float]:
        """Nueva funcionalidad: calcular BMI."""
        person = self.get_person_by_id(person_id)
        return person.bmi

    def validate_person_consistency(self, person_id: int) -> List[str]:
        """Nueva funcionalidad: validar consistencia de datos."""
        person = self.get_person_by_id(person_id)
        return person.validate_consistency()

    # ==================== MÉTODOS DE VALIDACIÓN PRIVADOS ====================

    def _validate_person_data(self, data: Dict[str, Any], is_update: bool = False) -> None:
        """Validaciones básicas de datos de persona (compatibilidad)."""
        errors = {}

        # Validaciones requeridas para creación
        if not is_update:
            if not data.get('name') and not data.get('first_name'):
                errors['name'] = "Nombre es requerido"
            if not data.get('last_name'):
                errors['last_name'] = "Apellido es requerido"
            if not data.get('email'):
                errors['email'] = "Email es requerido"

        # Validaciones de formato si los datos están presentes
        if data.get('email'):
            try:
                validate_email(data['email'])
            except ValueError as e:
                errors['email'] = str(e)

        if data.get('name'):
            try:
                validate_non_empty_string(data['name'], "Nombre")
            except ValueError as e:
                errors['name'] = str(e)

        if data.get('last_name'):
            try:
                validate_non_empty_string(data['last_name'], "Apellido")
            except ValueError as e:
                errors['last_name'] = str(e)

        if data.get('phone'):
            try:
                validate_phone(data['phone'])
            except ValueError as e:
                errors['phone'] = str(e)

        if errors:
            raise EntityValidationError("Person", errors)

    def _validate_extended_person_data(self, data: Dict[str, Any]) -> None:
        """Validaciones extendidas para el nuevo modelo."""
        errors = {}

        # Validaciones básicas
        self._validate_person_data(data)

        # Validaciones extendidas
        if data.get('age'):
            try:
                validate_age(data['age'])
            except ValueError as e:
                errors['age'] = str(e)

        if data.get('birth_date'):
            try:
                validate_birth_date(data['birth_date'])
            except ValueError as e:
                errors['birth_date'] = str(e)

        if data.get('phone_numbers'):
            try:
                validate_phone_list(data['phone_numbers'])
            except ValueError as e:
                errors['phone_numbers'] = str(e)

        if errors:
            raise EntityValidationError("Person", errors)

    def _validate_user_exists(self, user_id: int) -> None:
        """Valida que el usuario existe."""
        from database import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise EntityNotFoundError("User", user_id)

    def _validate_user_data(self, user_data: Dict[str, Any]) -> None:
        """Valida datos de usuario para creación."""
        errors = {}

        if not user_data.get('user_email'):
            errors['user_email'] = "Email de usuario es requerido"
        else:
            try:
                validate_email(user_data['user_email'])
            except ValueError as e:
                errors['user_email'] = str(e)

        if not user_data.get('user_name'):
            errors['user_name'] = "Nombre de usuario es requerido"

        if not user_data.get('user_password'):
            errors['user_password'] = "Contraseña es requerida"
        elif len(user_data['user_password']) < 6:
            errors['user_password'] = "Contraseña debe tener al menos 6 caracteres"

        if errors:
            raise EntityValidationError("UserData", errors)

    def _email_exists_in_users(self, email: str) -> bool:
        """Verifica si el email existe en la tabla de usuarios."""
        from database import User
        return self.db.query(User).filter(User.email == email).first() is not None

    def _validate_deletion_rules(self, person_id: int, deleted_by: Optional[int] = None) -> None:
        """
        Valida reglas de negocio para eliminación.

        Si la persona tiene un usuario asociado (creada con /persons/with-user),
        también elimina el usuario con soft delete.
        """
        from datetime import datetime
        from database import User

        # Obtener la persona para verificar si tiene usuario asociado
        person = self.repository.get_by_id(person_id)
        if not person:
            return

        # Si la persona tiene usuario asociado, eliminarlo también
        if person.user_id:
            user = self.db.query(User).filter(User.id == person.user_id).first()
            if user and not user.is_deleted:
                # Soft delete del usuario
                user.is_active = False
                user.is_deleted = True
                user.deleted_at = datetime.utcnow()
                user.deleted_by = deleted_by
                user.updated_by = deleted_by
                user.updated_at = datetime.utcnow()
                # No hacer commit aquí, será parte de la transacción del delete de Person

    # ==================== MÉTODOS DE MAPEO PARA COMPATIBILIDAD ====================

    def get_legacy_response(self, person: Person) -> Dict[str, Any]:
        """
        Convierte Person al formato de respuesta legacy.

        Para mantener compatibilidad con endpoints existentes.
        """
        return {
            "id": person.id,
            "user_id": person.user_id,
            "name": person.first_name,
            "last_name": person.last_name,
            "email": person.email,
            "phone": person.primary_phone,
            "address": person.address_street,
            "status": person.status.value if person.status else "active",
            "is_active": person.is_active,
            "created_at": person.created_at,
            "updated_at": person.updated_at
        }