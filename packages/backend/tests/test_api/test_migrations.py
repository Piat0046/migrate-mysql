"""Migration API tests."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from migrate_mysql.api.models import MigrationHistory


class TestExport:
    """Test export endpoint."""

    @patch("migrate_mysql.api.routes.migrations.run_export")
    def test_export_start(
        self, mock_run_export, client: TestClient, auth_headers: dict[str, str], db: Session
    ):
        """Test starting an export returns job ID."""
        response = client.post(
            "/api/migrations/export",
            json={
                "source": {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "password",
                    "database": "testdb",
                },
                "tables": ["users", "orders"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"

    @patch("migrate_mysql.api.routes.migrations.run_export")
    def test_export_with_filter(
        self, mock_run_export, client: TestClient, auth_headers: dict[str, str], db: Session
    ):
        """Test export with table filters."""
        response = client.post(
            "/api/migrations/export",
            json={
                "source": {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "password",
                    "database": "testdb",
                },
                "tables": ["users"],
                "filters": [
                    {
                        "table_name": "users",
                        "where_clause": "created_at > '2024-01-01'",
                        "columns": ["id", "name", "email"],
                    }
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data


class TestImport:
    """Test import endpoint."""

    @patch("migrate_mysql.api.routes.migrations.run_import")
    def test_import_start(
        self, mock_run_import, client: TestClient, auth_headers: dict[str, str], db: Session, tmp_path
    ):
        """Test starting an import returns job ID."""
        # Create a temporary file
        test_file = tmp_path / "dump.sql"
        test_file.write_text("-- test sql")

        response = client.post(
            "/api/migrations/import",
            json={
                "target": {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "password",
                    "database": "targetdb",
                },
                "file_path": str(test_file),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"


class TestMigrationStatus:
    """Test migration status endpoint."""

    def test_get_migration_status(
        self, client: TestClient, auth_headers: dict[str, str], db: Session, test_user
    ):
        """Test getting migration status."""
        # Create a migration record
        migration = MigrationHistory(
            user_id=test_user.id,
            type="export",
            source_host="localhost",
            source_port=3306,
            source_database="testdb",
            status="running",
            row_count=100,
        )
        db.add(migration)
        db.commit()
        db.refresh(migration)

        response = client.get(
            f"/api/migrations/{migration.id}/status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == migration.id
        assert data["status"] == "running"
        assert data["row_count"] == 100

    def test_get_migration_status_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test getting non-existent migration status."""
        response = client.get(
            "/api/migrations/99999/status",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestCancelMigration:
    """Test cancel migration endpoint."""

    def test_cancel_migration(
        self, client: TestClient, auth_headers: dict[str, str], db: Session, test_user
    ):
        """Test cancelling a running migration."""
        migration = MigrationHistory(
            user_id=test_user.id,
            type="export",
            source_host="localhost",
            source_port=3306,
            source_database="testdb",
            status="running",
        )
        db.add(migration)
        db.commit()
        db.refresh(migration)

        response = client.delete(
            f"/api/migrations/{migration.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
