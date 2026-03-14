from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.amenity import Amenity
from app.repositories.amenity import AmenityRepository
from app.schemas.amenity import AmenityCreate, AmenityUpdate


class AmenityService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AmenityRepository(db)

    def list_all(self) -> list[Amenity]:
        return self.repo.get_all()

    def create(self, data: AmenityCreate) -> Amenity:
        existing = self.repo.get_by_slug(data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug already exists",
            )
        return self.repo.create(**data.model_dump())

    def update(self, amenity_id: int, data: AmenityUpdate) -> Amenity | None:
        update = data.model_dump(exclude_unset=True)
        if "slug" in update:
            other = self.repo.get_by_slug(update["slug"])
            if other and other.id != amenity_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Slug already exists",
                )
        return self.repo.update(amenity_id, **update)

    def delete(self, amenity_id: int) -> bool:
        return self.repo.delete(amenity_id)

