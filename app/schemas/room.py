from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RoomBase(BaseModel):
    name: str
    floor: int
    capacity: str
    is_active: bool


class RoomCreate(RoomBase):
    pass  # все поля обязательны


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[str] = None
    is_active: Optional[bool] = None


class RoomResponse(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
