"""Database connection routes."""

import mysql.connector
from fastapi import APIRouter, Depends

from ..auth import get_current_active_user
from ..models import User
from ..schemas import (
    ColumnInfo,
    ConnectionConfig,
    ConnectionTestResponse,
    TableColumnsRequest,
)

router = APIRouter(prefix="/api/connections", tags=["connections"])


@router.post("/test", response_model=ConnectionTestResponse)
async def test_connection(
    config: ConnectionConfig,
    current_user: User = Depends(get_current_active_user),
):
    """Test database connection and return table list on success."""
    try:
        conn = mysql.connector.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return ConnectionTestResponse(
            success=True,
            message="Connection successful",
            tables=tables,
        )
    except mysql.connector.Error as e:
        return ConnectionTestResponse(
            success=False,
            message=str(e),
            tables=None,
        )


@router.post("/tables", response_model=list[str])
async def get_tables(
    config: ConnectionConfig,
    current_user: User = Depends(get_current_active_user),
):
    """Get list of tables from database."""
    conn = mysql.connector.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables


@router.post("/columns", response_model=list[ColumnInfo])
async def get_columns(
    request: TableColumnsRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Get list of columns from a table."""
    config = request.connection
    conn = mysql.connector.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE `{request.table}`")
    columns = []
    for row in cursor.fetchall():
        columns.append(
            ColumnInfo(
                name=row[0],
                type=row[1],
                nullable=row[2] == "YES",
                key=row[3] if row[3] else None,
                default=str(row[4]) if row[4] is not None else None,
            )
        )
    cursor.close()
    conn.close()
    return columns
