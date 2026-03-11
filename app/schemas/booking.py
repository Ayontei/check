from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

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
    room_id: Optional[int] = None
    user_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    purpose: Optional[str] = None


class BookingResponse(BookingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
