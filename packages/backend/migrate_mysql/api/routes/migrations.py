"""Migration routes."""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_active_user
from ..database import get_db
from ..models import MigrationHistory, User
from ..schemas import (
    ExportRequest,
    ImportRequest,
    MigrationResponse,
    MigrationStatus,
)
from ...exporter import ExportConfig, MySQLExporter, TableFilter
from ...importer import ImportConfig, MySQLImporter

router = APIRouter(prefix="/api/migrations", tags=["migrations"])

# Store for tracking active migrations
active_migrations: dict[int, bool] = {}


def run_export(migration_id: int, config: ExportConfig, db_url: str):
    """Background task to run export."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        migration = db.query(MigrationHistory).filter(
            MigrationHistory.id == migration_id
        ).first()
        if not migration:
            return

        migration.status = "running"
        migration.started_at = datetime.utcnow()
        db.commit()

        exporter = MySQLExporter(config)

        def progress_callback(table_name: str, row_count: int):
            if not active_migrations.get(migration_id, True):
                raise Exception("Migration cancelled")
            migration.row_count += row_count
            db.commit()

        stats = exporter.export(progress_callback=progress_callback)

        migration.status = "completed"
        migration.completed_at = datetime.utcnow()
        migration.row_count = sum(stats.values())
        db.commit()

    except Exception as e:
        migration.status = "failed"
        migration.error_message = str(e)
        migration.completed_at = datetime.utcnow()
        db.commit()
    finally:
        active_migrations.pop(migration_id, None)
        db.close()


def run_import(migration_id: int, config: ImportConfig, db_url: str):
    """Background task to run import."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        migration = db.query(MigrationHistory).filter(
            MigrationHistory.id == migration_id
        ).first()
        if not migration:
            return

        migration.status = "running"
        migration.started_at = datetime.utcnow()
        db.commit()

        importer = MySQLImporter(config)

        def progress_callback(stmt_count: int):
            if not active_migrations.get(migration_id, True):
                raise Exception("Migration cancelled")
            migration.row_count = stmt_count
            db.commit()

        stats = importer.import_data(progress_callback=progress_callback)

        migration.status = "completed"
        migration.completed_at = datetime.utcnow()
        migration.row_count = stats.get("rows_inserted", 0)
        db.commit()

    except Exception as e:
        migration.status = "failed"
        migration.error_message = str(e)
        migration.completed_at = datetime.utcnow()
        db.commit()
    finally:
        active_migrations.pop(migration_id, None)
        db.close()


@router.post("/export", response_model=MigrationResponse)
async def start_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start a database export."""
    # Generate output file path
    output_file = Path(f"/tmp/export_{uuid.uuid4().hex}.sql")

    # Build table filters
    table_filters = {}
    if request.filters:
        for f in request.filters:
            table_filters[f.table_name] = TableFilter(
                table_name=f.table_name,
                where_clause=f.where_clause,
                columns=f.columns,
            )

    # Create export config
    config = ExportConfig(
        host=request.source.host,
        port=request.source.port,
        user=request.source.user,
        password=request.source.password,
        database=request.source.database,
        output_path=output_file,
        tables=request.tables,
        table_filters=table_filters,
    )

    # Create migration record
    migration = MigrationHistory(
        user_id=current_user.id,
        type="export",
        source_host=request.source.host,
        source_port=request.source.port,
        source_database=request.source.database,
        tables={"tables": request.tables} if request.tables else None,
        filters={f.table_name: {"where": f.where_clause, "columns": f.columns} for f in request.filters} if request.filters else None,
        status="pending",
        file_path=str(output_file),
    )
    db.add(migration)
    db.commit()
    db.refresh(migration)

    # Track active migration
    active_migrations[migration.id] = True

    # Get database URL for background task
    from ..config import settings
    background_tasks.add_task(run_export, migration.id, config, settings.database_url)

    return MigrationResponse(
        id=migration.id,
        status="pending",
        message="Export started",
    )


@router.post("/import", response_model=MigrationResponse)
async def start_import(
    request: ImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start a database import."""
    # Verify file exists
    file_path = Path(request.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File not found: {request.file_path}",
        )

    # Create import config
    config = ImportConfig(
        host=request.target.host,
        port=request.target.port,
        user=request.target.user,
        password=request.target.password,
        database=request.target.database,
        input_path=file_path,
    )

    # Create migration record
    migration = MigrationHistory(
        user_id=current_user.id,
        type="import",
        source_host=request.target.host,
        source_port=request.target.port,
        source_database=request.target.database,
        target_host=request.target.host,
        target_port=request.target.port,
        target_database=request.target.database,
        status="pending",
        file_path=request.file_path,
    )
    db.add(migration)
    db.commit()
    db.refresh(migration)

    # Track active migration
    active_migrations[migration.id] = True

    # Get database URL for background task
    from ..config import settings
    background_tasks.add_task(run_import, migration.id, config, settings.database_url)

    return MigrationResponse(
        id=migration.id,
        status="pending",
        message="Import started",
    )


@router.get("/{migration_id}/status", response_model=MigrationStatus)
async def get_migration_status(
    migration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get migration status."""
    migration = db.query(MigrationHistory).filter(
        MigrationHistory.id == migration_id,
        MigrationHistory.user_id == current_user.id,
    ).first()

    if not migration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Migration not found",
        )

    return MigrationStatus(
        id=migration.id,
        type=migration.type,
        status=migration.status,
        row_count=migration.row_count,
        error_message=migration.error_message,
        started_at=migration.started_at,
        completed_at=migration.completed_at,
    )


@router.delete("/{migration_id}", response_model=MigrationStatus)
async def cancel_migration(
    migration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel a running migration."""
    migration = db.query(MigrationHistory).filter(
        MigrationHistory.id == migration_id,
        MigrationHistory.user_id == current_user.id,
    ).first()

    if not migration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Migration not found",
        )

    if migration.status not in ("pending", "running"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel migration with status: {migration.status}",
        )

    # Signal cancellation
    active_migrations[migration_id] = False

    migration.status = "cancelled"
    migration.completed_at = datetime.utcnow()
    db.commit()

    return MigrationStatus(
        id=migration.id,
        type=migration.type,
        status=migration.status,
        row_count=migration.row_count,
        error_message=migration.error_message,
        started_at=migration.started_at,
        completed_at=migration.completed_at,
    )
