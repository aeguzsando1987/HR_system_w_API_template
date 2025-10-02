"""
Controller para Person

Maneja la lógica de presentación y coordina entre
Service layer y Router layer. Mantiene compatibilidad
total con los endpoints existentes.
"""

from typing import List, Dict, Any, Optional
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.entities.persons.services.person_service import PersonService
from app.entities.persons.models.person import Person
from app.entities.persons.schemas.enums import PersonStatusEnum
from app.shared.exceptions import (
    BaseAppException,
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)


class PersonController:
    """
    Controller para manejar requests HTTP de Person.

    Coordina entre Router y Service layer, manejando:
    - Validación de input HTTP
    - Transformación de datos
    - Manejo de errores
    - Formateo de respuestas
    """

    def __init__(self, db: Session):
        self.db = db
        self.service = PersonService(db)

    # ==================== ENDPOINTS DE COMPATIBILIDAD ====================

    def create_person(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crear persona - Compatibilidad con POST /persons/

        Args:
            person_data: Datos en formato legacy

        Returns:
            Respuesta con ID, name, last_name, email
        """
        try:
            person = self.service.create_person_legacy(person_data)
            return {
                "id": person.id,
                "name": person.first_name,
                "last_name": person.last_name,
                "email": person.email
            }
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_persons(self) -> List[Dict[str, Any]]:
        """
        Listar personas activas - Compatibilidad con GET /persons/

        Returns:
            Lista de personas en formato PersonResponse
        """
        try:
            persons = self.service.get_all_active_persons()
            return [self._to_person_response(person) for person in persons]
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def search_persons(
        self,
        request: Request,
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
        order_desc: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda avanzada - Compatibilidad con GET /persons/search

        Mantiene exactamente la misma funcionalidad que el endpoint original
        incluyendo filtros dinámicos desde query parameters.
        """
        try:
            # Extraer filtros dinámicos adicionales del request
            additional_filters = {}
            excluded_params = {
                'name', 'last_name', 'email', 'phone', 'status', 'user_id',
                'search', 'page', 'limit', 'order_by', 'order_desc'
            }

            for key, value in request.query_params.items():
                if key not in excluded_params and value:
                    additional_filters[key] = value

            persons = self.service.search_persons(
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

            return [self._to_person_response(person) for person in persons]

        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_person(self, person_id: int) -> Dict[str, Any]:
        """
        Obtener persona específica - Compatibilidad con GET /persons/{person_id}
        """
        try:
            person = self.service.get_person_by_id(person_id)
            return self._to_person_response(person)
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def update_person(
        self,
        person_id: int,
        update_data: Dict[str, Any],
        current_user_id: int
    ) -> Dict[str, Any]:
        """
        Actualizar persona - Compatibilidad con PUT /persons/{person_id}
        """
        try:
            person = self.service.update_person_legacy(
                person_id, update_data, current_user_id
            )
            return {
                "id": person.id,
                "name": person.first_name,
                "last_name": person.last_name,
                "email": person.email
            }
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except EntityAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def delete_person(self, person_id: int, current_user_id: int) -> Dict[str, str]:
        """
        Eliminar persona (soft delete) - Compatibilidad con DELETE /persons/{person_id}
        """
        try:
            self.service.delete_person(person_id, current_user_id)
            return {"message": "Persona eliminada correctamente"}
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def create_person_with_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crear persona con usuario - Compatibilidad con POST /persons/with-user
        """
        try:
            # Separar datos de usuario y persona
            user_data = {
                'user_email': data.get('user_email'),
                'user_name': data.get('user_name'),
                'user_password': data.get('user_password'),
                'user_role': data.get('user_role', 4)
            }

            person_data = {
                'name': data.get('name'),  # Formato legacy
                'last_name': data.get('last_name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'address': data.get('address'),
                'status': data.get('status', 'active')
            }

            user_result, person_result = self.service.create_person_with_user(
                user_data, person_data
            )

            return {
                "user": user_result,
                "person": person_result
            }

        except EntityAlreadyExistsError as e:
            if "User" in e.message:
                raise HTTPException(status_code=400, detail="Email de usuario ya existe")
            else:
                raise HTTPException(status_code=400, detail="Email de persona ya existe")
        except EntityValidationError as e:
            # Incluir los detalles de validación en la respuesta
            raise HTTPException(
                status_code=e.status_code,
                detail={
                    "message": e.message,
                    "errors": e.details.get('validation_errors', {})
                }
            )
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creando usuario y persona: {str(e)}")

    # ==================== NUEVOS ENDPOINTS EXTENDIDOS ====================

    def create_person_extended(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crear persona con funcionalidades extendidas del nuevo modelo.
        """
        try:
            person = self.service.create_person_extended(person_data)
            return self._to_extended_response(person)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def find_by_document(self, document_number: str) -> Dict[str, Any]:
        """
        Buscar persona por número de documento.
        """
        try:
            person = self.service.find_by_document(document_number)
            if not person:
                raise HTTPException(status_code=404, detail="Persona no encontrada")
            return self._to_extended_response(person)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def find_by_phone(self, phone: str) -> List[Dict[str, Any]]:
        """
        Buscar personas por número de teléfono.
        """
        try:
            persons = self.service.find_by_phone_number(phone)
            return [self._to_extended_response(person) for person in persons]
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Obtener personas por status usando enum.
        """
        try:
            status_enum = PersonStatusEnum(status)
            persons = self.service.get_persons_by_status(status_enum)
            return [self._to_extended_response(person) for person in persons]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Status inválido: {status}")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_verified_persons(self) -> List[Dict[str, Any]]:
        """
        Obtener personas verificadas.
        """
        try:
            persons = self.service.get_verified_persons()
            return [self._to_extended_response(person) for person in persons]
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def verify_person(self, person_id: int, current_user_id: int) -> Dict[str, Any]:
        """
        Verificar persona.
        """
        try:
            person = self.service.verify_person(person_id, current_user_id)
            return {
                "message": "Persona verificada exitosamente",
                "person": self._to_extended_response(person)
            }
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BusinessRuleError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def search_by_skills(self, skill: str) -> List[Dict[str, Any]]:
        """
        Buscar personas por habilidad.
        """
        try:
            persons = self.service.search_by_skills(skill)
            return [self._to_extended_response(person) for person in persons]
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    # ==================== CONTROLADORES AVANZADOS DE SKILLS ====================

    def add_skill_to_person(
        self,
        person_id: int,
        skill_data: Dict[str, Any],
        current_user_id: int
    ) -> Dict[str, Any]:
        """
        Añadir skill detallada a persona.
        """
        try:
            self._validate_request_data(skill_data, ["name", "category", "level"])

            person = self.service.add_skill_to_person(
                person_id=person_id,
                skill_name=skill_data["name"],
                category=skill_data["category"],
                level=skill_data["level"],
                years_experience=skill_data.get("years_experience", 0),
                notes=skill_data.get("notes"),
                updated_by=current_user_id
            )

            return {
                "message": "Skill añadida exitosamente",
                "person_id": person_id,
                "skill_added": {
                    "name": skill_data["name"],
                    "category": skill_data["category"],
                    "level": skill_data["level"]
                },
                "skills_summary": person.get_skills_summary()
            }

        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BusinessRuleError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def remove_skill_from_person(
        self,
        person_id: int,
        skill_name: str,
        current_user_id: int
    ) -> Dict[str, Any]:
        """
        Eliminar skill de persona.
        """
        try:
            person = self.service.remove_skill_from_person(
                person_id=person_id,
                skill_name=skill_name,
                updated_by=current_user_id
            )

            return {
                "message": "Skill eliminada exitosamente",
                "person_id": person_id,
                "skill_removed": skill_name,
                "skills_summary": person.get_skills_summary()
            }

        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BusinessRuleError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def search_by_skill_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Buscar personas por categoría de skill.
        """
        try:
            persons = self.service.search_by_skill_category(category)
            return [self._to_extended_response(person) for person in persons]
        except BusinessRuleError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def search_by_skill_level(self, skill_name: str, level: str) -> List[Dict[str, Any]]:
        """
        Buscar personas con skill específica en nivel mínimo.
        """
        try:
            persons = self.service.search_by_skill_level(skill_name, level)
            return [self._to_extended_response(person) for person in persons]
        except BusinessRuleError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_persons_with_expert_skills(self) -> List[Dict[str, Any]]:
        """
        Obtener personas con skills de nivel experto.
        """
        try:
            persons = self.service.get_persons_with_expert_skills()
            return [self._to_extended_response(person) for person in persons]
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def search_by_skill_and_experience(self, skill_name: str, min_years: int) -> List[Dict[str, Any]]:
        """
        Buscar personas con skill y años mínimos de experiencia.
        """
        try:
            persons = self.service.search_by_skill_and_experience(skill_name, min_years)
            return [self._to_extended_response(person) for person in persons]
        except BusinessRuleError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_person_skills_summary(self, person_id: int) -> Dict[str, Any]:
        """
        Obtener resumen de skills de persona.
        """
        try:
            summary = self.service.get_person_skills_summary(person_id)
            return {
                "person_id": person_id,
                "skills_summary": summary
            }
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_person_skills_by_category(self, person_id: int, category: str) -> Dict[str, Any]:
        """
        Obtener skills de persona por categoría.
        """
        try:
            skills = self.service.get_person_skills_by_category(person_id, category)
            return {
                "person_id": person_id,
                "category": category,
                "skills": skills
            }
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BusinessRuleError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_person_expert_skills(self, person_id: int) -> Dict[str, Any]:
        """
        Obtener skills de nivel experto de persona.
        """
        try:
            expert_skills = self.service.get_person_expert_skills(person_id)
            return {
                "person_id": person_id,
                "expert_skills": expert_skills
            }
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def validate_person_skill_requirements(
        self,
        person_id: int,
        requirements: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Validar si persona cumple requisitos de skills.
        """
        try:
            # Validar formato de requisitos
            for req in requirements:
                if not req.get("name") or not req.get("level"):
                    raise HTTPException(
                        status_code=422,
                        detail="Cada requisito debe tener 'name' y 'level'"
                    )

            validation_result = self.service.validate_person_skill_requirements(
                person_id, requirements
            )
            return validation_result

        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def update_skill_level(
        self,
        person_id: int,
        skill_name: str,
        update_data: Dict[str, Any],
        current_user_id: int
    ) -> Dict[str, Any]:
        """
        Actualizar nivel de skill existente.
        """
        try:
            self._validate_request_data(update_data, ["level"])

            person = self.service.update_skill_level(
                person_id=person_id,
                skill_name=skill_name,
                new_level=update_data["level"],
                years_experience=update_data.get("years_experience"),
                notes=update_data.get("notes"),
                updated_by=current_user_id
            )

            return {
                "message": "Nivel de skill actualizado exitosamente",
                "person_id": person_id,
                "skill_name": skill_name,
                "new_level": update_data["level"],
                "skill_detail": person.get_skill_detail(skill_name)
            }

        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BusinessRuleError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_skills_global_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas globales de skills.
        """
        try:
            return self.service.get_skills_global_statistics()
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de personas.
        """
        try:
            return self.service.get_person_statistics()
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_person_age(self, person_id: int) -> Dict[str, Any]:
        """
        Calcular edad de persona.
        """
        try:
            age = self.service.calculate_person_age(person_id)
            return {"person_id": person_id, "age": age}
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def get_person_bmi(self, person_id: int) -> Dict[str, Any]:
        """
        Calcular BMI de persona.
        """
        try:
            bmi = self.service.get_person_bmi(person_id)
            return {"person_id": person_id, "bmi": bmi}
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def validate_person_consistency(self, person_id: int) -> Dict[str, Any]:
        """
        Validar consistencia de datos de persona.
        """
        try:
            errors = self.service.validate_person_consistency(person_id)
            return {
                "person_id": person_id,
                "is_consistent": len(errors) == 0,
                "validation_errors": errors
            }
        except EntityNotFoundError:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        except BaseAppException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    # ==================== MÉTODOS PRIVADOS DE TRANSFORMACIÓN ====================

    def _to_person_response(self, person: Person) -> Dict[str, Any]:
        """
        Convierte Person a formato PersonResponse para compatibilidad.
        """
        return {
            "id": person.id,
            "user_id": person.user_id,
            "name": person.first_name,  # Mapeo para compatibilidad
            "last_name": person.last_name,
            "email": person.email,
            "phone": person.primary_phone,  # Primer teléfono del array
            "address": person.address_street,  # Dirección principal
            "status": person.status.value if person.status else "active",
            "is_active": person.is_active,
            "created_at": person.created_at,
            "updated_at": person.updated_at
        }

    def _to_extended_response(self, person: Person) -> Dict[str, Any]:
        """
        Convierte Person a formato extendido con todas las propiedades.
        """
        return {
            "id": person.id,
            "user_id": person.user_id,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "full_name": person.full_name,
            "email": person.email,
            "document_type": person.document_type.value if person.document_type else None,
            "document_number": person.document_number,
            "phone_numbers": person.phone_numbers,
            "primary_phone": person.primary_phone,
            "address": {
                "street": person.address_street,
                "city": person.address_city,
                "state": person.address_state
            },
            "birth_info": {
                "birth_date": person.birth_date,
                "age": person.calculated_age,
                "birth_city": person.birth_city,
                "birth_state": person.birth_state,
                "birth_country": person.birth_country
            },
            "physical_info": {
                "height": float(person.height) if person.height else None,
                "weight": float(person.weight) if person.weight else None,
                "bmi": person.bmi
            },
            "status_info": {
                "status": person.status.value if person.status else None,
                "is_active": person.is_active,
                "is_verified": person.is_verified,
                "is_deleted": person.is_deleted
            },
            "personal_info": {
                "gender": person.gender.value if person.gender else None,
                "marital_status": person.marital_status.value if person.marital_status else None,
                "education_level": person.education_level.value if person.education_level else None,
                "employment_status": person.employment_status.value if person.employment_status else None
            },
            "skills": person.skills,
            "languages": person.languages,
            "preferences": person.preferences,
            "additional_data": person.additional_data,
            "audit_info": {
                "created_at": person.created_at,
                "updated_at": person.updated_at,
                "deleted_at": person.deleted_at,
                "created_by": person.created_by,
                "updated_by": person.updated_by,
                "deleted_by": person.deleted_by
            }
        }

    def _validate_request_data(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Valida que los campos requeridos estén presentes en el request.
        """
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise HTTPException(
                status_code=422,
                detail=f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            )