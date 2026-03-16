from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoomBase(BaseModel):
    name: str
    floor: int
    capacity: str
    is_active: bool


class RoomCreate(RoomBase):
    pass  # все поля обязательны


class RoomUpdate(BaseModel):
    name: str | None = None
    floor: int | None = None
    capacity: str | None = None
    is_active: bool | None = None


class RoomResponse(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
