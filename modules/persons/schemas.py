from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PersonCreate(BaseModel):
    user_id: Optional[int] = None  # FK opcional
    name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    status: str = "active"

class PersonUpdate(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class PersonWithUserCreate(BaseModel):
    # Datos del usuario
    user_email: str
    user_name: str
    user_password: str
    user_role: int = 4  # Default: Lector
    # Datos de la persona
    name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    status: str = "active"

class PersonResponse(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    last_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True