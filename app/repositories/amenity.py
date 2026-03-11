from sqlalchemy.orm import Session

from app.models.amenity import Amenity
from app.repositories.base import BaseRepository


class AmenityRepository(BaseRepository[Amenity]):
    def __init__(self, db: Session):
        super().__init__(Amenity, db)

    def get_by_slug(self, slug: str) -> Amenity | None:
        return self.db.query(Amenity).filter(Amenity.slug == slug).first()

