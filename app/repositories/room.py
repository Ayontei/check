from sqlalchemy.orm import Session

from app.models.room import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    def __init__(self, db: Session):
        super().__init__(Room, db)

