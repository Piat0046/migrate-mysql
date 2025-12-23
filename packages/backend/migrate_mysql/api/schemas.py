"""Pydantic schemas for API request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Auth schemas
class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    username: str | None = None


class UserBase(BaseModel):
    """Base user schema."""

    username: str


class UserCreate(UserBase):
    """User creation schema."""

    password: str


class UserResponse(UserBase):
    """User response schema."""

    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


# Connection schemas
class ConnectionConfig(BaseModel):
    """Database connection configuration."""

    host: str
    port: int = 3306
    user: str
    password: str
    database: str


class ConnectionTestResponse(BaseModel):
    """Connection test response."""

    success: bool
    message: str
    tables: list[str] | None = None


class TableColumnsRequest(BaseModel):
    """Request for table columns."""

    connection: ConnectionConfig
    table: str


class ColumnInfo(BaseModel):
    """Column information."""

    name: str
    type: str
    nullable: bool
    key: str | None = None
    default: str | None = None


# Filter schemas
class TableFilter(BaseModel):
    """Filter configuration for a table."""

    table_name: str
    where_clause: str | None = None
    columns: list[str] | None = None


# Migration schemas
class ExportRequest(BaseModel):
    """Export request schema."""

    source: ConnectionConfig
    tables: list[str] | None = None
    filters: list[TableFilter] | None = None


class ImportRequest(BaseModel):
    """Import request schema."""

    target: ConnectionConfig
    file_path: str


class MigrationResponse(BaseModel):
    """Migration response schema."""

    id: int
    status: str
    message: str


class MigrationStatus(BaseModel):
    """Migration status schema."""

    id: int
    type: str
    status: str
    row_count: int
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class MigrationHistoryResponse(BaseModel):
    """Migration history response."""

    id: int
    type: str
    source_host: str
    source_database: str
    target_host: str | None = None
    target_database: str | None = None
    tables: dict | None = None
    status: str
    row_count: int
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schedule schemas
class ScheduleCreate(BaseModel):
    """Schedule creation schema."""

    name: str
    cron_expression: str
    config: dict


class ScheduleResponse(BaseModel):
    """Schedule response schema."""

    id: int
    name: str
    cron_expression: str
    config: dict
    is_active: bool
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Pagination
class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
