from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200


def test_register_login_refresh_me_smoke(client: TestClient):
    email = "smoke@example.com"
    password = "secret123"

    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "is_active": True, "is_admin": False},
    )
    assert r.status_code in {201, 400}  # 400 if already exists

    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r.status_code == 200
    assert r.json()["email"] == email

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_create_booking_validation_smoke(client: TestClient):
    # this test only verifies request-level validation and auth wiring.
    email = "booking_smoke@example.com"
    password = "secret123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "is_active": True, "is_admin": False},
    )
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    tokens = r.json()

    now = datetime.now(timezone.utc)
    start_at = (now + timedelta(hours=1)).isoformat()
    end_at = (now + timedelta(hours=1, minutes=10)).isoformat()
    # room_id might not exist in a blank DB -> expect 400 from service
    r = client.post(
        "/api/v1/bookings",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"room_id": 1, "start_at": start_at, "end_at": end_at, "purpose": "smoke"},
    )
    assert r.status_code in {400, 201}

