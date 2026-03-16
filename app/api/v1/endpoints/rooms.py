from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_room_service, require_admin
from app.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from app.services.room import RoomService

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
def list_rooms(service: RoomService = Depends(get_room_service)):
    return service.list_active()


@router.get("/availability", response_model=list[RoomResponse])
def availability(
    start_at: datetime = Query(..., description="Начало интервала (ISO 8601)"),
    end_at: datetime = Query(..., description="Конец интервала (ISO 8601)"),
    capacity_min: int | None = Query(None, description="Минимальная вместимость"),
    amenity_ids: list[int] | None = Query(None, description="ID удобств (комната должна содержать все)"),
    floor: int | None = Query(None, description="Этаж"),
    service: RoomService = Depends(get_room_service),
):
    if end_at <= start_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid interval")
    return service.availability(
        start_at, end_at,
        capacity_min=capacity_min,
        amenity_ids=amenity_ids or None,
        floor=floor,
    )


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, service: RoomService = Depends(get_room_service)):
    room = service.get(room_id)
    if not room or not room.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room not found")
    return room


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    service: RoomService = Depends(get_room_service),
    _admin=Depends(require_admin),
):
    return service.create(payload)


@router.patch("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    payload: RoomUpdate,
    service: RoomService = Depends(get_room_service),
    _admin=Depends(require_admin),
):
    room = service.update(room_id, payload)
    if not room:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room not found")
    return room


@router.delete("/{room_id}", response_model=RoomResponse)
def deactivate_room(
    room_id: int,
    service: RoomService = Depends(get_room_service),
    _admin=Depends(require_admin),
):
    room = service.deactivate(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room not found")
    return room

