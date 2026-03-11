from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.redis_client import redis_client
from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.repositories.booking import BookingRepository
from app.repositories.room import RoomRepository
from app.repositories.user import UserRepository
from app.schemas.booking import BookingCreate


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BookingRepository(db)
        self.room_repo = RoomRepository(db)
        self.user_repo = UserRepository(db)
        self.settings = get_settings()

    def get_booking_by_id(self, booking_id: int) -> Booking | None:
        return self.repo.get(booking_id)

    def list_my_bookings(self, user_id: int) -> list[Booking]:
        return self.repo.list_for_user(user_id)

    def list_all_bookings(self) -> list[Booking]:
        return self.repo.list_all()

    def create_booking(self, user_id: int, data: BookingCreate) -> Booking:
        if data.end_at <= data.start_at:
            raise ValueError("Invalid interval: end_at must be after start_at")

        if not self.room_repo.get(data.room_id):
            raise ValueError("Room not found")
        if not self.user_repo.get(user_id):
            raise ValueError("User not found")

        if data.start_at <= datetime.utcnow():
            raise ValueError("Cannot create booking in the past")

        if data.end_at - data.start_at < timedelta(minutes=15):
            raise ValueError("Minimum booking duration is 15 minutes")

        overlaps = self.repo.find_overlaps(
            room_id=data.room_id, start_at=data.start_at, end_at=data.end_at
        )
        if overlaps:
            raise ValueError("Time slot is not available")

        booking = self.repo.create(
            room_id=data.room_id,
            user_id=user_id,
            start_at=data.start_at,
            end_at=data.end_at,
            purpose=data.purpose,
            status=BookingStatus.PENDING.value,
        )

        # Кэш
        redis_client.delete(f"booking:{booking.id}")
        redis_client.delete(f"room_availability:{booking.room_id}")

        # Celery: планируем авто-истечение через N минут
        from app.tasks.booking_tasks import expire_pending_booking

        expire_pending_booking.apply_async(
            args=[booking.id], countdown=self.settings.BOOKING_EXPIRE_MINUTES * 60
        )
        return booking

    def get_booking_for_user(self, booking_id: int, user_id: int, *, is_admin: bool) -> Booking | None:
        booking = self.repo.get(booking_id)
        if not booking:
            return None
        if is_admin or booking.user_id == user_id:
            return booking
        return None

    def confirm_booking(self, booking_id: int, user_id: int, *, is_admin: bool) -> Booking | None:
        booking = self.repo.get(booking_id)
        if not booking:
            return None
        if not is_admin and booking.user_id != user_id:
            raise ValueError("Forbidden")

        if booking.status != BookingStatus.PENDING.value:
            raise ValueError("Only PENDING bookings can be confirmed")

        overlaps = self.repo.find_overlaps(
            room_id=booking.room_id,
            start_at=booking.start_at,
            end_at=booking.end_at,
            exclude_booking_id=booking.id,
        )
        if overlaps:
            raise ValueError("Time slot is not available")

        booking = self.repo.update(booking_id, status=BookingStatus.CONFIRMED.value)

        # Кэш
        redis_client.delete(f"booking:{booking.id}")
        redis_client.delete(f"room_availability:{booking.room_id}")

        # Celery: планируем напоминание за M минут до start_at
        from app.tasks.booking_tasks import send_booking_reminder

        reminder_at = booking.start_at - timedelta(
            minutes=self.settings.BOOKING_REMINDER_MINUTES
        )
        eta = reminder_at if reminder_at > datetime.utcnow() else None
        if eta:
            send_booking_reminder.apply_async(args=[booking.id], eta=eta)
        return booking

    def cancel_booking(self, booking_id: int, user_id: int, *, is_admin: bool) -> Booking | None:
        booking = self.repo.get(booking_id)
        if not booking:
            return None
        if not is_admin and booking.user_id != user_id:
            raise ValueError("Forbidden")

        if booking.status in {BookingStatus.CANCELLED.value, BookingStatus.EXPIRED.value}:
            return booking

        booking = self.repo.update(booking_id, status=BookingStatus.CANCELLED.value)
        redis_client.delete(f"booking:{booking.id}")
        redis_client.delete(f"room_availability:{booking.room_id}")
        return booking

