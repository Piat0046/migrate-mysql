"""WebSocket handler for real-time migration progress."""

import asyncio
from typing import Any, Callable

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from .models import MigrationHistory

# Session factory - can be overridden for testing
_session_factory: Callable[[], Session] | None = None


def get_session_factory():
    """Get the session factory."""
    global _session_factory
    if _session_factory is None:
        from .database import SessionLocal
        return SessionLocal
    return _session_factory


def set_session_factory(factory: Callable[[], Session] | None):
    """Set the session factory (for testing)."""
    global _session_factory
    _session_factory = factory

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, migration_id: int):
        """Connect a WebSocket for a migration."""
        await websocket.accept()
        if migration_id not in self.active_connections:
            self.active_connections[migration_id] = []
        self.active_connections[migration_id].append(websocket)

    def disconnect(self, websocket: WebSocket, migration_id: int):
        """Disconnect a WebSocket."""
        if migration_id in self.active_connections:
            if websocket in self.active_connections[migration_id]:
                self.active_connections[migration_id].remove(websocket)
            if not self.active_connections[migration_id]:
                del self.active_connections[migration_id]

    async def send_message(self, migration_id: int, message: dict[str, Any]):
        """Send a message to all connections for a migration."""
        if migration_id in self.active_connections:
            for connection in self.active_connections[migration_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


def get_migration_status(db: Session, migration_id: int) -> dict[str, Any] | None:
    """Get current migration status."""
    migration = db.query(MigrationHistory).filter(
        MigrationHistory.id == migration_id
    ).first()

    if not migration:
        return None

    return {
        "type": "status",
        "migration_id": migration.id,
        "status": migration.status,
        "row_count": migration.row_count,
        "error_message": migration.error_message,
        "started_at": migration.started_at.isoformat() if migration.started_at else None,
        "completed_at": migration.completed_at.isoformat() if migration.completed_at else None,
    }


@router.websocket("/ws/migrations/{migration_id}")
async def websocket_endpoint(websocket: WebSocket, migration_id: int):
    """WebSocket endpoint for migration progress."""
    await manager.connect(websocket, migration_id)

    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        # Send initial status
        status = get_migration_status(db, migration_id)
        if status:
            await websocket.send_json(status)

        # Poll for updates
        while True:
            # Check for status changes
            db.expire_all()  # Refresh from database
            status = get_migration_status(db, migration_id)

            if status:
                await websocket.send_json(status)

                # If migration is complete, send final status and close
                if status["status"] in ("completed", "failed", "cancelled"):
                    break

            await asyncio.sleep(1)  # Poll every second

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, migration_id)
        db.close()


async def broadcast_progress(migration_id: int, status: str, row_count: int):
    """Broadcast progress update to all connected clients."""
    message = {
        "type": "progress",
        "migration_id": migration_id,
        "status": status,
        "row_count": row_count,
    }
    await manager.send_message(migration_id, message)
