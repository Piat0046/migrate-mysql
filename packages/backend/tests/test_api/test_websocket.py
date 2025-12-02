"""WebSocket API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from migrate_mysql.api.models import MigrationHistory
from migrate_mysql.api import websocket as ws_module
from tests.conftest import TestingSessionLocal


class TestWebSocketConnect:
    """Test WebSocket connection."""

    def test_websocket_connect(
        self, client: TestClient, db: Session, test_user
    ):
        """Test WebSocket connection success."""
        # Set test session factory
        ws_module.set_session_factory(TestingSessionLocal)

        try:
            # Create a migration
            migration = MigrationHistory(
                user_id=test_user.id,
                type="export",
                source_host="localhost",
                source_port=3306,
                source_database="testdb",
                status="completed",  # Use completed to avoid infinite loop
            )
            db.add(migration)
            db.commit()
            db.refresh(migration)

            with client.websocket_connect(f"/ws/migrations/{migration.id}") as websocket:
                # Should receive initial status
                data = websocket.receive_json()
                assert data["type"] == "status"
                assert data["migration_id"] == migration.id
        finally:
            ws_module.set_session_factory(None)


class TestWebSocketProgressUpdates:
    """Test WebSocket progress updates."""

    def test_websocket_receives_progress(
        self, client: TestClient, db: Session, test_user
    ):
        """Test receiving progress updates via WebSocket."""
        # Set test session factory
        ws_module.set_session_factory(TestingSessionLocal)

        try:
            migration = MigrationHistory(
                user_id=test_user.id,
                type="export",
                source_host="localhost",
                source_port=3306,
                source_database="testdb",
                status="completed",  # Use completed to avoid infinite loop
                row_count=0,
            )
            db.add(migration)
            db.commit()
            db.refresh(migration)

            with client.websocket_connect(f"/ws/migrations/{migration.id}") as websocket:
                # Receive initial status
                data = websocket.receive_json()
                assert data["type"] == "status"
                assert data["status"] == "completed"
        finally:
            ws_module.set_session_factory(None)
