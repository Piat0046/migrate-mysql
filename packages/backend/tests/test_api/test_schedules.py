"""Schedule API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from migrate_mysql.api.models import Schedule


class TestCreateSchedule:
    """Test schedule creation endpoint."""

    def test_create_schedule(
        self, client: TestClient, auth_headers: dict[str, str], db: Session
    ):
        """Test creating a new schedule."""
        response = client.post(
            "/api/schedules",
            json={
                "name": "Daily backup",
                "cron_expression": "0 0 * * *",
                "config": {
                    "source": {
                        "host": "localhost",
                        "port": 3306,
                        "user": "root",
                        "password": "password",
                        "database": "testdb",
                    },
                    "tables": ["users"],
                },
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Daily backup"
        assert data["cron_expression"] == "0 0 * * *"
        assert data["is_active"] is True


class TestGetSchedules:
    """Test schedule list endpoint."""

    def test_get_schedules(
        self, client: TestClient, auth_headers: dict[str, str], db: Session, test_user
    ):
        """Test getting schedule list."""
        # Create some schedules
        for i in range(3):
            schedule = Schedule(
                user_id=test_user.id,
                name=f"Schedule {i}",
                cron_expression=f"0 {i} * * *",
                config={"test": True},
            )
            db.add(schedule)
        db.commit()

        response = client.get(
            "/api/schedules",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestDeleteSchedule:
    """Test schedule deletion endpoint."""

    def test_delete_schedule(
        self, client: TestClient, auth_headers: dict[str, str], db: Session, test_user
    ):
        """Test deleting a schedule."""
        schedule = Schedule(
            user_id=test_user.id,
            name="To be deleted",
            cron_expression="0 0 * * *",
            config={"test": True},
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)

        response = client.delete(
            f"/api/schedules/{schedule.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        deleted = db.query(Schedule).filter(Schedule.id == schedule.id).first()
        assert deleted is None

    def test_delete_schedule_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test deleting non-existent schedule."""
        response = client.delete(
            "/api/schedules/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404
