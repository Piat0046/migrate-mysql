"""Connection API tests."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestConnectionTest:
    """Test connection test endpoint."""

    @patch("migrate_mysql.api.routes.connections.mysql.connector.connect")
    def test_connection_success(
        self, mock_connect, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("users",), ("orders",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.post(
            "/api/connections/test",
            json={
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "password",
                "database": "testdb",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tables" in data
        assert len(data["tables"]) == 2

    @patch("migrate_mysql.api.routes.connections.mysql.connector.connect")
    def test_connection_failure(
        self, mock_connect, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test failed database connection."""
        import mysql.connector

        mock_connect.side_effect = mysql.connector.Error("Connection refused")

        response = client.post(
            "/api/connections/test",
            json={
                "host": "invalid-host",
                "port": 3306,
                "user": "root",
                "password": "password",
                "database": "testdb",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "message" in data


class TestGetTables:
    """Test get tables endpoint."""

    @patch("migrate_mysql.api.routes.connections.mysql.connector.connect")
    def test_get_tables(
        self, mock_connect, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test getting table list from database."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("users",),
            ("orders",),
            ("products",),
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.post(
            "/api/connections/tables",
            json={
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "password",
                "database": "testdb",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert "users" in data


class TestGetColumns:
    """Test get columns endpoint."""

    @patch("migrate_mysql.api.routes.connections.mysql.connector.connect")
    def test_get_columns(
        self, mock_connect, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test getting column list from table."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("id", "int", "NO", "PRI", None, "auto_increment"),
            ("name", "varchar(100)", "NO", "", None, ""),
            ("email", "varchar(255)", "YES", "UNI", None, ""),
            ("created_at", "datetime", "YES", "", "CURRENT_TIMESTAMP", ""),
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        response = client.post(
            "/api/connections/columns",
            json={
                "connection": {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "password",
                    "database": "testdb",
                },
                "table": "users",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4
        assert data[0]["name"] == "id"
        assert data[0]["type"] == "int"
        assert data[0]["key"] == "PRI"
