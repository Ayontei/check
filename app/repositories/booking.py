from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    def __init__(self, db: Session):
        super().__init__(Booking, db)

    def list_pending_older_than(self, minutes: int) -> list[Booking]:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return (
            self.db.query(Booking)
            .filter(Booking.status == BookingStatus.PENDING.value)
            .filter(Booking.created_at <= cutoff)
            .all()
        )

    def find_overlaps(
        self,
        room_id: int,
        start_at: datetime,
        end_at: datetime,
        *,
        exclude_booking_id: int | None = None,
        statuses: set[str] | None = None,
    ) -> list[Booking]:
        """
        Ищет пересечения по интервалу [start_at, end_at) для комнаты.
        Пересечение: existing.start < end AND existing.end > start.
        """
        if statuses is None:
            statuses = {BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value}

        q = (
            self.db.query(Booking)
            .filter(Booking.room_id == room_id)
            .filter(Booking.status.in_(list(statuses)))
            .filter(and_(Booking.start_at < end_at, Booking.end_at > start_at))
        )
        if exclude_booking_id is not None:
            q = q.filter(Booking.id != exclude_booking_id)
        return q.all()

    def list_for_user(self, user_id: int) -> list[Booking]:
        return (
            self.db.query(Booking)
            .filter(Booking.user_id == user_id)
            .order_by(Booking.start_at.desc())
            .all()
        )

    def list_all(self) -> list[Booking]:
        return self.db.query(Booking).order_by(Booking.start_at.desc()).all()

