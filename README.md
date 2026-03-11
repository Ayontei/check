# Room Booking API

REST API для бронирования переговорных комнат. Пользователи просматривают комнаты и доступность, создают и отменяют бронирования; администратор управляет справочниками и видит все бронирования.

**Стек:** FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery + RabbitMQ, Docker.

---

## Описание проекта, функционал, роли

### Функционал

- **Комнаты и удобства** — список активных комнат, детали комнаты, поиск доступных комнат по интервалу (с фильтрами: этаж, вместимость, удобства).
- **Бронирования** — создание (статус PENDING), подтверждение, отмена; запрет пересечений по времени для одной комнаты; автоистечение неподтверждённых бронирований через N минут; напоминание за M минут до начала (лог/email).
- **Аутентификация** — JWT (access + refresh), регистрация, логин, обновление токена, профиль текущего пользователя.

### Роли

| Роль | Доступ |
|------|--------|
| **Anonymous** | Просмотр списка комнат, деталей комнаты, доступности по интервалу (без персональных данных). |
| **Authenticated** | Всё выше + создание/просмотр/отмена своих бронирований, подтверждение своих бронирований. |
| **Admin** | Всё выше + CRUD комнат и удобств, просмотр и модерация всех бронирований (`GET /admin/bookings`). |

---

## Команды запуска (docker-compose / Makefile)

### Требования

- Docker и Docker Compose
- Файл `.env` в корне проекта (скопируйте из `.env.example` и при необходимости отредактируйте)

### Запуск

```bash
# Поднять все сервисы (api, db, rabbitmq, redis, worker, beat)
make up

# Остановить
make down

# Логи
make logs
```

Без Makefile:

```bash
docker compose up -d --build
docker compose down
docker compose logs -f --tail=200
```

После запуска API доступен по адресу: **http://localhost:8000**.

---

## Миграции и создание админа

### Миграции

Применить миграции (после первого `make up`, когда БД уже поднята):

```bash
make migrate
```

Без Makefile:

```bash
poetry run alembic upgrade head
```

Для запуска миграций внутри контейнера (если БД в Docker, а команда выполняется на хосте) убедитесь, что в `.env` указаны `DB_HOST=localhost` при запуске с хоста или используйте `docker compose run api poetry run alembic upgrade head` (тогда `DB_HOST=db`).

### Создание администратора

Админ — пользователь с полем `is_admin: true`. Создать его можно через API:

1. Зарегистрировать пользователя с флагом администратора:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "secret", "is_active": true, "is_admin": true}'
```

2. Далее входить через `POST /api/v1/auth/login` и использовать выданный `access_token` в заголовке `Authorization: Bearer <token>` для доступа к эндпоинтам администратора (комнаты, удобства, `GET /admin/bookings`).

---

## Документация API (/docs и /redoc)

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Откройте в браузере после запуска сервиса `api` (`make up`).

---

## Запуск тестов (pytest)

```bash
make test
```

Без Makefile:

```bash
poetry run pytest -q
```

Для подробного вывода:

```bash
poetry run pytest -v
```

Перед запуском тестов должна быть доступна БД (и при необходимости Redis/RabbitMQ), либо в тестах подменяются зависимости на тестовые/моки.

---

## Структура слоёв (API / Service / Repository)

Архитектура трёх слоёв: тонкий API, бизнес-логика в сервисах, доступ к данным в репозиториях.

```
app/
├── api/
│   ├── dependencies.py      # Depends: get_db, get_*_service, get_current_user, require_admin
│   └── v1/
│       ├── api.py           # Роутер /api/v1, подключение эндпоинтов
│       └── endpoints/       # Роутеры по доменам
│           ├── auth.py      # /auth: register, login, refresh, me
│           ├── rooms.py     # /rooms: list, availability, by id, CRUD (admin)
│           ├── amenities.py # /amenities: list, CRUD (admin)
│           ├── bookings.py  # /bookings: list, get, create, confirm, cancel
│           └── admin.py     # /admin: bookings (list all)
├── schemas/                 # Pydantic-модели (запросы/ответы)
├── services/                # Бизнес-логика
│   ├── user.py
│   ├── room.py              # Пересечения, кэш, фильтры availability
│   ├── amenity.py
│   └── booking.py           # Правила бронирований, кэш, вызов Celery
├── repositories/            # SQLAlchemy: CRUD, выборки по интервалам
│   ├── base.py
│   ├── user.py
│   ├── room.py
│   ├── amenity.py
│   └── booking.py
├── models/                  # Модели SQLAlchemy (User, Room, Amenity, Booking, M2M)
├── core/                    # Конфиг, БД, Redis, Celery, JWT
└── tasks/                   # Celery-задачи (expire, reminder, check_expired)
```

| Слой | Назначение |
|------|------------|
| **API** | FastAPI-роутеры (`APIRouter`), Pydantic-схемы, зависимости (`Depends`). Только приём запросов и возврат ответов, маппинг ошибок в HTTP. |
| **Service** | Проверки (пересечения, права), создание/подтверждение/отмена бронирований, работа с кэшем (Redis), постановка фоновых задач (Celery). |
| **Repository** | SQLAlchemy-запросы: CRUD, выборки по интервалам (например, пересечения бронирований), транзакции. |
