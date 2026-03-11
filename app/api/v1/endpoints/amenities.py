from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_amenity_service, require_admin
from app.schemas.amenity import AmenityCreate, AmenityResponse, AmenityUpdate
from app.services.amenity import AmenityService

router = APIRouter(prefix="/amenities", tags=["amenities"])


@router.get("", response_model=list[AmenityResponse])
def list_amenities(service: AmenityService = Depends(get_amenity_service)):
    return service.list_all()


@router.post("", response_model=AmenityResponse, status_code=status.HTTP_201_CREATED)
def create_amenity(
    payload: AmenityCreate,
    service: AmenityService = Depends(get_amenity_service),
    _admin=Depends(require_admin),
):
    try:
        return service.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{amenity_id}", response_model=AmenityResponse)
def update_amenity(
    amenity_id: int,
    payload: AmenityUpdate,
    service: AmenityService = Depends(get_amenity_service),
    _admin=Depends(require_admin),
):
    try:
        amenity = service.update(amenity_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not amenity:
        raise HTTPException(status_code=404, detail="Amenity not found")
    return amenity


@router.delete("/{amenity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_amenity(
    amenity_id: int,
    service: AmenityService = Depends(get_amenity_service),
    _admin=Depends(require_admin),
):
    ok = service.delete(amenity_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Amenity not found")
    return None

