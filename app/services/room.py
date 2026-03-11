from datetime import datetime
import json
import re
from typing import Any, Sequence

from sqlalchemy.orm import Session

from app.core.cache import invalidate_availability_cache, invalidate_rooms_cache
from app.core.config import get_settings
from app.core.redis_client import redis_client
from app.models.room import Room
from app.repositories.booking import BookingRepository
from app.repositories.room import RoomRepository
from app.schemas.room import RoomCreate, RoomUpdate


def _room_capacity_max(capacity_str: str) -> int:
    """Из строки '2-4' или '8' извлекает максимальную вместимость."""
    if not capacity_str:
        return 0
    parts = re.split(r"[-–]", capacity_str.strip())
    try:
        return max(int(p.strip()) for p in parts if p.strip().isdigit())
    except (ValueError, TypeError):
        return 0


def _room_to_cache_dict(room: Room) -> dict[str, Any]:
    return {
        "id": room.id,
        "name": room.name,
        "floor": room.floor,
        "capacity": room.capacity,
        "is_active": room.is_active,
        "created_at": room.created_at.isoformat() if getattr(room, "created_at", None) else None,
    }


class RoomService:
    def __init__(self, db: Session):
        self.db = db
        self.room_repo = RoomRepository(db)
        self.booking_repo = BookingRepository(db)
        self.settings = get_settings()

    def list_active(self) -> list[Room]:
        key = "rooms:list"
        try:
            cached = redis_client.get(key)
        except Exception:
            cached = None

        if cached:
            data = json.loads(cached)
            # Возвращаем как dict? Для response_model это ок, но сервис пусть отдаёт ORM.
            # Поэтому кэш используем только на уровне роутера/ответов: здесь же вернём ORM.
            # Фоллбек: игнорируем кэш, если нужен ORM.
            # (оставляем кэш для будущей оптимизации без ломания слоёв)
            pass

        rooms = self.room_repo.filter(is_active=True)
        try:
            redis_client.setex(
                key,
                self.settings.CACHE_TTL_ROOMS_LIST,
                json.dumps([_room_to_cache_dict(r) for r in rooms], ensure_ascii=False),
            )
        except Exception:
            pass
        return rooms

    def get(self, room_id: int) -> Room | None:
        return self.room_repo.get(room_id)

    def create(self, data: RoomCreate) -> Room:
        room = self.room_repo.create(**data.model_dump())
        invalidate_rooms_cache()
        invalidate_availability_cache()
        return room

    def update(self, room_id: int, data: RoomUpdate) -> Room | None:
        room = self.room_repo.update(room_id, **data.model_dump(exclude_unset=True))
        if room:
            invalidate_rooms_cache()
            invalidate_availability_cache()
        return room

    def deactivate(self, room_id: int) -> Room | None:
        room = self.room_repo.update(room_id, is_active=False)
        if room:
            invalidate_rooms_cache()
            invalidate_availability_cache()
        return room

    def availability(
        self,
        start_at: datetime,
        end_at: datetime,
        *,
        capacity_min: int | None = None,
        amenity_ids: Sequence[int] | None = None,
        floor: int | None = None,
    ) -> list[Room]:
        cache_key = (
            f"rooms:avail:{start_at.isoformat()}:{end_at.isoformat()}:"
            f"cap={capacity_min}:floor={floor}:amenities={','.join(map(str, amenity_ids or []))}"
        )
        try:
            cached = redis_client.get(cache_key)
        except Exception:
            cached = None
        if cached:
            # Аналогично list_active: чтобы не смешивать слои, кэш держим как ускорение,
            # но возвращаем ORM из БД. Поэтому кэш сейчас только записываем.
            pass

        rooms = self.list_active()
        if floor is not None:
            rooms = [r for r in rooms if r.floor == floor]
        if amenity_ids:
            aid_set = set(amenity_ids)
            rooms = [r for r in rooms if aid_set <= {a.id for a in (r.amenities or [])}]
        available: list[Room] = []
        for room in rooms:
            overlaps = self.booking_repo.find_overlaps(
                room_id=room.id, start_at=start_at, end_at=end_at
            )
            if not overlaps:
                if capacity_min is not None and _room_capacity_max(room.capacity or "") < capacity_min:
                    continue
                available.append(room)
        try:
            redis_client.setex(
                cache_key,
                self.settings.CACHE_TTL_AVAILABILITY,
                json.dumps([_room_to_cache_dict(r) for r in available], ensure_ascii=False),
            )
        except Exception:
            pass
        return available

