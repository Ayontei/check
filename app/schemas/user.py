from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional


# База с общими полями
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False


# Что присылает клиент при регистрации
class UserCreate(UserBase):
    password: str  # пароль (plain text)


# Что присылает клиент при обновлении (все поля опциональны)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


# Что возвращаем клиенту (без пароля!)
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# Для внутреннего использования (с хэшем)
class UserInDB(UserResponse):
    password_hash: str
