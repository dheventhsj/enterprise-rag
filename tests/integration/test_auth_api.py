"""Integration tests for authentication API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_returns_user_and_token(client: AsyncClient) -> None:
    """POST /auth/register creates account and returns JWT."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "register@example.com",
            "password": "securepass123",
            "full_name": "Register User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "register@example.com"
    assert data["user"]["full_name"] == "Register User"
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    """Duplicate email registration returns conflict."""
    payload = {"email": "dup@example.com", "password": "securepass123"}
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["error"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_weak_password_returns_422(client: AsyncClient) -> None:
    """Password shorter than 8 characters is rejected."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_returns_token(client: AsyncClient) -> None:
    """POST /auth/login returns JWT for valid credentials."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401(client: AsyncClient) -> None:
    """Invalid login returns unauthorized."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "securepass123"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_me_requires_authentication(client: AsyncClient) -> None:
    """GET /auth/me without token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(client: AsyncClient, auth_headers) -> None:
    """GET /auth/me returns authenticated user profile."""
    headers = await auth_headers(email="me@example.com", full_name="Me User")
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "Me User"
    assert data["is_active"] is True
