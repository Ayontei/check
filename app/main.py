from fastapi import FastAPI
from app.api.v1.api import api_router
import uvicorn


app = FastAPI(
    title="Room Booking API",
    description="API для бронирования переговорных комнат",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Room Booking API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
