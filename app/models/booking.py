from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
from .enums import BookingStatus


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default=BookingStatus.PENDING.value)
    purpose = Column(String, nullable=False)

    # Связи (relationships) — опционально, для удобства
    room = relationship("Room", backref="bookings")
    user = relationship("User", backref="bookings")
