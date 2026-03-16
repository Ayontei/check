from datetime import datetime

from pydantic import BaseModel

from app.models.enums import BookingStatus


class BookingListFilters(BaseModel):
    status: BookingStatus | None = None
    start_from: datetime | None = None
    start_to: datetime | None = None

