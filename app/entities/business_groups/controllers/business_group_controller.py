"""
Controller: BusinessGroup

Manejo de requests y responses para BusinessGroup.
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.business_groups.services.business_group_service import BusinessGroupService
from app.entities.business_groups.schemas.business_group_schemas import (
    BusinessGroupCreate,
    BusinessGroupUpdate,
    BusinessGroupResponse,
    BusinessGroupListResponse
)
from app.shared.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    EntityValidationError,
    BusinessRuleError
)


class BusinessGroupController:
    """Controller para BusinessGroup."""

    def __init__(self, db: Session):
        """Inicializa el controller con el servicio."""
        self.service = BusinessGroupService(db)

    def create_business_group(
        self,
        business_group_data: BusinessGroupCreate,
        current_user_id: Optional[int] = None
    ) -> BusinessGroupResponse:
        """
        Crea un nuevo BusinessGroup.

        Args:
            business_group_data: Datos del BusinessGroup
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            BusinessGroup creado

        Raises:
            HTTPException 422: Si hay errores de validación
            HTTPException 409: Si el tax_id ya existe
        """
        try:
            data = business_group_data.model_dump(exclude_unset=True)
            business_group = self.service.create_business_group(
                data,
                created_by=current_user_id
            )
            return BusinessGroupResponse.model_validate(business_group)

        except EntityValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": e.message,
                    "errors": e.details.get("validation_errors", {})
                }
            )
        except EntityAlreadyExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": e.message,
                    "details": e.details
                }
            )

    def get_business_group(self, business_group_id: int) -> BusinessGroupResponse:
        """
        Obtiene un BusinessGroup por ID.

        Args:
            business_group_id: ID del BusinessGroup

        Returns:
            BusinessGroup encontrado

        Raises:
            HTTPException 404: Si no se encuentra
        """
        try:
            business_group = self.service.get_business_group_by_id(business_group_id)
            return BusinessGroupResponse.model_validate(business_group)

        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )

    def get_all_business_groups(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> list[BusinessGroupResponse]:
        """
        Obtiene todos los BusinessGroups.

        Args:
            skip: Registros a saltar
            limit: Máximo de registros
            active_only: Solo activos

        Returns:
            Lista de BusinessGroups
        """
        business_groups = self.service.get_all_business_groups(skip, limit, active_only)
        return [
            BusinessGroupResponse.model_validate(bg)
            for bg in business_groups
        ]

    def update_business_group(
        self,
        business_group_id: int,
        business_group_data: BusinessGroupUpdate,
        current_user_id: Optional[int] = None
    ) -> BusinessGroupResponse:
        """
        Actualiza un BusinessGroup.

        Args:
            business_group_id: ID del BusinessGroup
            business_group_data: Datos a actualizar
            current_user_id: ID del usuario actual

        Returns:
            BusinessGroup actualizado

        Raises:
            HTTPException 404: Si no se encuentra
            HTTPException 422: Si hay errores de validación
            HTTPException 409: Si el tax_id ya existe
        """
        try:
            data = business_group_data.model_dump(exclude_unset=True)
            business_group = self.service.update_business_group(
                business_group_id,
                data,
                updated_by=current_user_id
            )
            return BusinessGroupResponse.model_validate(business_group)

        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except EntityValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": e.message,
                    "errors": e.details.get("validation_errors", {})
                }
            )
        except EntityAlreadyExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": e.message,
                    "details": e.details
                }
            )

    def delete_business_group(
        self,
        business_group_id: int,
        current_user_id: Optional[int] = None
    ) -> dict:
        """
        Elimina un BusinessGroup (soft delete).

        Args:
            business_group_id: ID del BusinessGroup
            current_user_id: ID del usuario actual

        Returns:
            Mensaje de confirmación

        Raises:
            HTTPException 404: Si no se encuentra
            HTTPException 400: Si tiene empresas activas asociadas
        """
        try:
            self.service.delete_business_group(
                business_group_id,
                deleted_by=current_user_id,
                soft_delete=True
            )
            return {
                "message": "BusinessGroup eliminado exitosamente",
                "id": business_group_id
            }

        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except BusinessRuleError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": e.message,
                    "details": e.details
                }
            )

    def search_business_groups(self, name: str, limit: int = 50) -> list[BusinessGroupResponse]:
        """
        Busca BusinessGroups por nombre.

        Args:
            name: Término de búsqueda
            limit: Máximo de resultados

        Returns:
            Lista de BusinessGroups que coinciden
        """
        business_groups = self.service.search_business_groups(name, limit)
        return [
            BusinessGroupResponse.model_validate(bg)
            for bg in business_groups
        ]

    def paginate_business_groups(
        self,
        page: int = 1,
        per_page: int = 20,
        active_only: bool = True,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> BusinessGroupListResponse:
        """
        Obtiene BusinessGroups paginados.

        Args:
            page: Número de página
            per_page: Registros por página
            active_only: Solo activos
            order_by: Campo de ordenamiento
            order_direction: Dirección de ordenamiento

        Returns:
            Respuesta paginada
        """
        filters = {"is_active": True} if active_only else None

        result = self.service.paginate_business_groups(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by=order_by,
            order_direction=order_direction
        )

        return BusinessGroupListResponse(
            items=[BusinessGroupResponse.model_validate(bg) for bg in result["items"]],
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
            pages=result["pages"]
        )
