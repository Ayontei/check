from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin
from .room_amenity import room_amenities


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(String, nullable=False)  # например "2-4", "5-8"
    is_active = Column(Boolean, default=True)

    amenities = relationship(
        "Amenity",
        secondary=room_amenities,
        back_populates="rooms",
        lazy="selectin",
    )
