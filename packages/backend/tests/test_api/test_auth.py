"""Authentication API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from migrate_mysql.api.models import User
from migrate_mysql.api.auth import get_password_hash


class TestLogin:
    """Test login endpoint."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login returns JWT token."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpassword"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with wrong password returns 401."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_user_not_found(self, client: TestClient):
        """Test login with non-existent user returns 401."""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()


class TestGetMe:
    """Test get current user endpoint."""

    def test_get_me_authenticated(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test get current user with valid token returns user info."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
        assert "is_active" in data

    def test_get_me_unauthenticated(self, client: TestClient):
        """Test get current user without token returns 401."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client: TestClient):
        """Test get current user with invalid token returns 401."""
        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401


class TestLogout:
    """Test logout endpoint."""

    def test_logout(self, client: TestClient, auth_headers: dict[str, str]):
        """Test logout returns success message."""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
