from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import LoginRequest, RefreshRequest, TokenPair
from app.services.user import UserService
from app.api.dependencies import get_current_user, get_user_service
from app.core.config import get_settings
from app.core.security import create_token, decode_token, validate_token_type

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    """Регистрация нового пользователя"""
    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, user_service: UserService = Depends(get_user_service)):
    user = user_service.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    settings = get_settings()
    access = create_token(
        subject=str(user.id),
        token_type="access",
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TTL_MIN),
    )
    refresh = create_token(
        subject=str(user.id),
        token_type="refresh",
        expires_delta=timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
    )
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    try:
        token_payload = decode_token(payload.refresh_token)
        validate_token_type(token_payload, "refresh")
        user_id = str(token_payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    settings = get_settings()
    access = create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TTL_MIN),
    )
    refresh_new = create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
    )
    return TokenPair(access_token=access, refresh_token=refresh_new)


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user
