"""History API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from migrate_mysql.api.models import MigrationHistory


class TestGetHistoryList:
    """Test history list endpoint."""

    def test_get_history_list(
        self, client: TestClient, auth_headers: dict[str, str], db: Session, test_user
    ):
        """Test getting paginated history list."""
        # Create some migration records
        for i in range(5):
            migration = MigrationHistory(
                user_id=test_user.id,
                type="export",
                source_host="localhost",
                source_port=3306,
                source_database=f"testdb{i}",
                status="completed",
                row_count=100 * (i + 1),
            )
            db.add(migration)
        db.commit()

        response = client.get(
            "/api/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 5
        assert data["total"] == 5

    def test_get_history_list_pagination(
        self, client: TestClient, auth_headers: dict[str, str], db: Session, test_user
    ):
        """Test history list pagination."""
        # Create 15 records
        for i in range(15):
            migration = MigrationHistory(
                user_id=test_user.id,
                type="export",
                source_host="localhost",
                source_port=3306,
                source_database=f"testdb{i}",
                status="completed",
            )
            db.add(migration)
        db.commit()

        # Get first page
        response = client.get(
            "/api/history?page=1&page_size=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["total_pages"] == 2


class TestGetHistoryDetail:
    """Test history detail endpoint."""

    def test_get_history_detail(
        self, client: TestClient, auth_headers: dict[str, str], db: Session, test_user
    ):
        """Test getting history detail."""
        migration = MigrationHistory(
            user_id=test_user.id,
            type="export",
            source_host="localhost",
            source_port=3306,
            source_database="testdb",
            status="completed",
            row_count=500,
            tables={"tables": ["users", "orders"]},
        )
        db.add(migration)
        db.commit()
        db.refresh(migration)

        response = client.get(
            f"/api/history/{migration.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == migration.id
        assert data["source_database"] == "testdb"
        assert data["row_count"] == 500

    def test_get_history_detail_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test getting non-existent history."""
        response = client.get(
            "/api/history/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404
