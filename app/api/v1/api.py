from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import bookings
from app.api.v1.endpoints import rooms
from app.api.v1.endpoints import amenities
from app.api.v1.endpoints import admin

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(bookings.router)
api_router.include_router(rooms.router)
api_router.include_router(amenities.router)
api_router.include_router(admin.router)
