"""SQLAlchemy models."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    migrations: Mapped[list["MigrationHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class MigrationHistory(Base):
    """Migration history model."""

    __tablename__ = "migration_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(20))  # 'export' or 'import'
    source_host: Mapped[str] = mapped_column(String(255))
    source_port: Mapped[int] = mapped_column(Integer)
    source_database: Mapped[str] = mapped_column(String(255))
    target_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_database: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tables: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    filters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, running, completed, failed, cancelled
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="migrations")


class Schedule(Base):
    """Schedule model for recurring migrations."""

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100))
    cron_expression: Mapped[str] = mapped_column(String(100))
    config: Mapped[dict] = mapped_column(JSON)  # Migration configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="schedules")
