"""Ключи и инвалидация Redis-кэша для rooms и availability."""

from app.core.redis_client import redis_client


def invalidate_rooms_cache() -> None:
    """Сброс кэша списка комнат (при изменении комнаты)."""
    try:
        redis_client.delete("rooms:list")
    except Exception:
        pass


def invalidate_availability_cache() -> None:
    """Сброс кэша доступности (при изменении бронирований или комнат)."""
    try:
        for key in redis_client.scan_iter("rooms:avail:*"):
            redis_client.delete(key)
    except Exception:
        pass
