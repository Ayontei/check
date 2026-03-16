from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


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
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None


# Что возвращаем клиенту (без пароля!)
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# Для внутреннего использования (с хэшем)
class UserInDB(UserResponse):
    password_hash: str
