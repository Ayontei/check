from datetime import datetime, timedelta
import logging

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.models.enums import BookingStatus

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="app.tasks.booking_tasks.expire_pending_booking")
def expire_pending_booking(booking_id: int):
    """
    Через N минут переводит PENDING -> EXPIRED (если не подтверждено) и инвалидирует кэш.
    """
    db = SessionLocal()
    try:
        from app.repositories.booking import BookingRepository

        repo = BookingRepository(db)
        booking = repo.get(booking_id)
        if not booking:
            return {"status": "error", "message": "Booking not found"}

        if booking.status != BookingStatus.PENDING.value:
            return {"status": "skipped", "message": f"Booking already {booking.status}"}

        # Страховочная проверка по времени (на случай ручного запуска/ретраев)
        if booking.created_at and datetime.utcnow() - booking.created_at < timedelta(
            minutes=settings.BOOKING_EXPIRE_MINUTES
        ):
            return {"status": "skipped", "message": "Booking not expired yet"}

        repo.update(booking_id, status=BookingStatus.EXPIRED.value)

        redis_client.delete(f"booking:{booking_id}")
        redis_client.delete(f"room_availability:{booking.room_id}")

        logger.info("Booking %s expired", booking_id)
        return {"status": "success", "booking_id": booking_id, "new_status": "expired"}
    except Exception as e:
        logger.exception("Expire booking failed: %s", booking_id)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.booking_tasks.send_booking_reminder")
def send_booking_reminder(booking_id: int):
    """
    За M минут до start_at отправляет напоминание пользователю (пока логом).
    """
    db = SessionLocal()
    try:
        from app.models.room import Room
        from app.repositories.base import BaseRepository
        from app.repositories.booking import BookingRepository
        from app.repositories.user import UserRepository

        booking_repo = BookingRepository(db)
        user_repo = UserRepository(db)
        room_repo = BaseRepository(Room, db)

        booking = booking_repo.get(booking_id)
        if not booking:
            return {"status": "error", "message": "Booking not found"}

        if booking.status != BookingStatus.CONFIRMED.value:
            return {"status": "skipped", "message": "Booking not confirmed"}

        user = user_repo.get(booking.user_id)
        room = room_repo.get(booking.room_id)

        # Здесь можно подключить реальную отправку email/telegram.
        logger.info(
            "Reminder: user=%s room=%s start_at=%s booking_id=%s",
            getattr(user, "email", None),
            getattr(room, "name", None),
            booking.start_at,
            booking_id,
        )

        return {
            "status": "success",
            "booking_id": booking_id,
            "user_email": getattr(user, "email", None),
            "room_name": getattr(room, "name", None),
            "start_at": str(booking.start_at),
        }
    except Exception as e:
        logger.exception("Reminder failed: %s", booking_id)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.booking_tasks.check_expired_bookings")
def check_expired_bookings():
    """
    Периодическая страховка: находит просроченные PENDING и переводит их в EXPIRED.
    """
    db = SessionLocal()
    try:
        from app.repositories.booking import BookingRepository

        repo = BookingRepository(db)
        expired = repo.list_pending_older_than(settings.BOOKING_EXPIRE_MINUTES)
        count = 0
        for booking in expired:
            repo.update(booking.id, status=BookingStatus.EXPIRED.value)
            redis_client.delete(f"booking:{booking.id}")
            redis_client.delete(f"room_availability:{booking.room_id}")
            count += 1
        return {"status": "success", "expired": count}
    except Exception as e:
        logger.exception("Periodic expire failed")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

