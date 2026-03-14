from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base
from .room_amenity import RoomAmenity


class Amenity(Base):
    __tablename__ = "amenities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)

    rooms = relationship(
        "Room",
        secondary=RoomAmenity.__table__,
        back_populates="amenities",
        lazy="selectin",
    )
