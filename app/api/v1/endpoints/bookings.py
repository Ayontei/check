from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_booking_service, get_current_user
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingResponse])
def list_my_bookings(
    service: BookingService = Depends(get_booking_service),
    user=Depends(get_current_user),
):
    return service.list_my_bookings(user.id)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    user=Depends(get_current_user),
):
    booking = service.get_booking_for_user(
        booking_id, user.id, is_admin=getattr(user, "is_admin", False)
    )
    if not booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking not found")
    return booking


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    service: BookingService = Depends(get_booking_service),
    user=Depends(get_current_user),
):
    try:
        return service.create_booking(user.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{booking_id}/confirm",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
)
def confirm_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    user=Depends(get_current_user),
):
    try:
        booking = service.confirm_booking(
            booking_id, user.id, is_admin=getattr(user, "is_admin", False)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking not found")
    return booking


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
)
def cancel_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    user=Depends(get_current_user),
):
    try:
        booking = service.cancel_booking(
            booking_id, user.id, is_admin=getattr(user, "is_admin", False)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking not found")
    return booking

