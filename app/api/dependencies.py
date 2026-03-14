from fastapi import Depends
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user import UserService
from app.services.booking import BookingService
from app.services.room import RoomService
from app.services.amenity import AmenityService
from app.core.security import decode_token, validate_token_type

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Зависимость для UserService"""
    return UserService(db)


def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    """Зависимость для BookingService"""
    return BookingService(db)


def get_room_service(db: Session = Depends(get_db)) -> RoomService:
    return RoomService(db)


def get_amenity_service(db: Session = Depends(get_db)) -> AmenityService:
    return AmenityService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = decode_token(token)
        validate_token_type(payload, "access")
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = user_service.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user


def require_admin(user=Depends(get_current_user)):
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin only")
    return user
