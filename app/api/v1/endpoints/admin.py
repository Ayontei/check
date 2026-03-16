from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_service, require_admin
from app.schemas.booking import BookingResponse
from app.services.booking import BookingService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/bookings", response_model=list[BookingResponse])
def list_all_bookings(
    service: BookingService = Depends(get_booking_service),
    _admin=Depends(require_admin),
):
    return service.list_all_bookings()

