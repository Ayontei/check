from pydantic import BaseModel, ConfigDict
from typing import Optional


class AmenityBase(BaseModel):
    name: str
    slug: str


class AmenityCreate(AmenityBase):
    pass  # все поля из AmenityBase обязательны


class AmenityUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class AmenityResponse(AmenityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
