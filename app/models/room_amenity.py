from sqlalchemy import Column, ForeignKey, Integer

from .base import Base


class RoomAmenity(Base):
    """Ассоциативная таблица many-to-many Room <-> Amenity."""

    __tablename__ = "room_amenities"

    room_id = Column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        primary_key=True,
    )
    amenity_id = Column(
        Integer,
        ForeignKey("amenities.id", ondelete="CASCADE"),
        primary_key=True,
    )
