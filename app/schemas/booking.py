from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import BookingStatus


class BookingBase(BaseModel):
    room_id: int
    user_id: int
    start_at: datetime
    end_at: datetime
    status: BookingStatus = BookingStatus.PENDING
    purpose: str


class BookingCreate(BaseModel):
    room_id: int
    start_at: datetime
    end_at: datetime
    purpose: str


class BookingUpdate(BaseModel):
    room_id: int | None = None
    user_id: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    status: BookingStatus | None = None
    purpose: str | None = None


class BookingResponse(BookingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
