from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.booking_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=20 * 60,  # 20 минут
)

# Расписание периодических задач (если нужно)
celery_app.conf.beat_schedule = {
    # Пример: проверка истекших бронирований каждый час
    'check-expired-bookings': {
        'task': 'app.tasks.booking_tasks.check_expired_bookings',
        'schedule': crontab(minute=0, hour='*'),  # каждый час
    },
}