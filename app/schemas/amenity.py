from pydantic import BaseModel, ConfigDict


class AmenityBase(BaseModel):
    name: str
    slug: str


class AmenityCreate(AmenityBase):
    pass  # все поля из AmenityBase обязательны


class AmenityUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None


class AmenityResponse(AmenityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
