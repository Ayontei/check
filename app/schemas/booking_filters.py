from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import BookingStatus


class BookingListFilters(BaseModel):
    status: Optional[BookingStatus] = None
    start_from: Optional[datetime] = None
    start_to: Optional[datetime] = None

