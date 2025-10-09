"""
Enumeraciones para UserScope

Define los tipos de scope disponibles para control de acceso granular.
"""

from enum import Enum


class ScopeTypeEnum(str, Enum):
    """
    Tipos de scope para control de acceso.

    - GLOBAL: Acceso total a toda la organización (solo Admin)
    - BUSINESS_GROUP: Acceso limitado a un BusinessGroup específico
    - COMPANY: Acceso limitado a una Company específica
    - BRANCH: Acceso limitado a un Branch específico
    - DEPARTMENT: Acceso limitado a un Department específico
    """
    GLOBAL = "GLOBAL"
    BUSINESS_GROUP = "BUSINESS_GROUP"
    COMPANY = "COMPANY"
    BRANCH = "BRANCH"
    DEPARTMENT = "DEPARTMENT"
