"""
Individual Repository - Operaciones de base de datos
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.entities.individuals.models.individual import Individual


class IndividualRepository(BaseRepository[Individual]):
    """Repository para operaciones de Individual"""

    def __init__(self, db: Session):
        super().__init__(Individual, db)

    def get_by_email(self, email: str) -> Optional[Individual]:
        """
        Obtiene un Individual por email.

        Args:
            email: Email del individual

        Returns:
            Individual o None si no existe
        """
        return self.db.query(Individual).filter(
            Individual.email == email,
            Individual.is_deleted == False
        ).first()

    def get_by_document(self, document_number: str) -> Optional[Individual]:
        """
        Obtiene un Individual por número de documento.

        Args:
            document_number: Número de documento

        Returns:
            Individual o None si no existe
        """
        return self.db.query(Individual).filter(
            Individual.document_number == document_number,
            Individual.is_deleted == False
        ).first()

    def get_by_curp(self, curp: str) -> Optional[Individual]:
        """
        Obtiene un Individual por CURP.

        Args:
            curp: CURP del individual

        Returns:
            Individual o None si no existe
        """
        return self.db.query(Individual).filter(
            Individual.curp == curp.upper(),
            Individual.is_deleted == False
        ).first()

    def get_by_payroll_number(self, payroll_number: str) -> Optional[Individual]:
        """
        Obtiene un Individual por número de nómina.

        Args:
            payroll_number: Número de nómina

        Returns:
            Individual o None si no existe
        """
        return self.db.query(Individual).filter(
            Individual.payroll_number == payroll_number,
            Individual.is_deleted == False
        ).first()

    def get_by_user_id(self, user_id: int) -> Optional[Individual]:
        """
        Obtiene un Individual por su user_id asociado.

        Args:
            user_id: ID del usuario asociado

        Returns:
            Individual o None si no existe
        """
        return self.db.query(Individual).filter(
            Individual.user_id == user_id,
            Individual.is_deleted == False
        ).first()

    def search(
        self,
        query: str,
        limit: int = 50
    ) -> List[Individual]:
        """
        Busca Individuals por nombre, apellido o email.

        Args:
            query: Texto a buscar
            limit: Número máximo de resultados

        Returns:
            Lista de Individuals que coinciden con la búsqueda
        """
        search_pattern = f"%{query}%"
        return self.db.query(Individual).filter(
            Individual.is_deleted == False,
            (
                Individual.first_name.ilike(search_pattern) |
                Individual.last_name.ilike(search_pattern) |
                Individual.email.ilike(search_pattern)
            )
        ).order_by(
            Individual.last_name.asc(),
            Individual.first_name.asc()
        ).limit(limit).all()

    def get_by_country(self, country_id: int, active_only: bool = True) -> List[Individual]:
        """
        Obtiene todos los Individuals de un país.

        Args:
            country_id: ID del país
            active_only: Si True, solo retorna activos

        Returns:
            Lista de Individuals del país
        """
        query = self.db.query(Individual).filter(Individual.country_id == country_id)

        if active_only:
            query = query.filter(
                Individual.is_active == True,
                Individual.is_deleted == False
            )

        return query.order_by(
            Individual.last_name.asc(),
            Individual.first_name.asc()
        ).all()

    def get_by_state(self, state_id: int, active_only: bool = True) -> List[Individual]:
        """
        Obtiene todos los Individuals de un estado.

        Args:
            state_id: ID del estado
            active_only: Si True, solo retorna activos

        Returns:
            Lista de Individuals del estado
        """
        query = self.db.query(Individual).filter(Individual.state_id == state_id)

        if active_only:
            query = query.filter(
                Individual.is_active == True,
                Individual.is_deleted == False
            )

        return query.order_by(
            Individual.last_name.asc(),
            Individual.first_name.asc()
        ).all()

    def has_active_employees(self, individual_id: int) -> bool:
        """
        Verifica si un Individual tiene employees activos asociados.

        Args:
            individual_id: ID del individual

        Returns:
            True si tiene employees activos, False en caso contrario

        Note:
            TODO: Implementar cuando Employee entity exista.
            Por ahora retorna False para permitir eliminaciones.
        """
        # TODO: Implementar cuando Employee exista
        # from app.entities.employees.models.employee import Employee
        # count = self.db.query(Employee).filter(
        #     Employee.individual_id == individual_id,
        #     Employee.is_active == True,
        #     Employee.is_deleted == False
        # ).count()
        # return count > 0
        return False

    def get_with_user(self, individual_id: int) -> Optional[Individual]:
        """
        Obtiene un Individual con su User asociado (eager loading).

        Args:
            individual_id: ID del individual

        Returns:
            Individual con User cargado, o None si no existe
        """
        from sqlalchemy.orm import joinedload

        return self.db.query(Individual).options(
            joinedload(Individual.user)
        ).filter(
            Individual.id == individual_id,
            Individual.is_deleted == False
        ).first()