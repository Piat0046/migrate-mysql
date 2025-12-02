"""MySQL database exporter with filtering support."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection


@dataclass
class TableFilter:
    """Filter configuration for a specific table."""

    table_name: str
    where_clause: str | None = None  # e.g., "created_at > '2024-01-01'"
    columns: list[str] | None = None  # None means all columns


@dataclass
class ExportConfig:
    """Configuration for database export."""

    host: str
    port: int
    user: str
    password: str
    database: str
    output_path: Path
    tables: list[str] | None = None  # None means all tables
    table_filters: dict[str, TableFilter] = field(default_factory=dict)
    include_schema: bool = True
    include_data: bool = True


class MySQLExporter:
    """Export MySQL database to SQL file with filtering support."""

    def __init__(self, config: ExportConfig):
        self.config = config
        self.conn: MySQLConnection | None = None

    def connect(self) -> None:
        """Establish database connection."""
        self.conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
        )

    def disconnect(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_tables(self) -> list[str]:
        """Get list of tables to export."""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.cursor()
        cursor.execute("SHOW TABLES")
        all_tables = [row[0] for row in cursor.fetchall()]
        cursor.close()

        if self.config.tables:
            return [t for t in all_tables if t in self.config.tables]
        return all_tables

    def get_create_table(self, table_name: str) -> str:
        """Get CREATE TABLE statement for a table."""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.cursor()
        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        result = cursor.fetchone()
        cursor.close()

        return result[1] if result else ""

    def get_table_columns(self, table_name: str) -> list[str]:
        """Get column names for a table."""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        cursor = self.conn.cursor()
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()

        return columns

    def escape_value(self, value: Any) -> str:
        """Escape a value for SQL insertion."""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bytes):
            hex_str = value.hex()
            return f"X'{hex_str}'"
        else:
            escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
            return f"'{escaped}'"

    def export_table_data(
        self, table_name: str, file_handle, batch_size: int = 1000
    ) -> int:
        """Export data for a single table. Returns row count."""
        if not self.conn:
            raise RuntimeError("Not connected to database")

        table_filter = self.config.table_filters.get(table_name)

        # Determine columns to select
        if table_filter and table_filter.columns:
            columns = table_filter.columns
        else:
            columns = self.get_table_columns(table_name)

        columns_str = ", ".join(f"`{col}`" for col in columns)

        # Build query
        query = f"SELECT {columns_str} FROM `{table_name}`"
        if table_filter and table_filter.where_clause:
            query += f" WHERE {table_filter.where_clause}"

        cursor = self.conn.cursor()
        cursor.execute(query)

        row_count = 0
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break

            for row in rows:
                values = ", ".join(self.escape_value(v) for v in row)
                insert_stmt = (
                    f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({values});\n"
                )
                file_handle.write(insert_stmt)
                row_count += 1

        cursor.close()
        return row_count

    def export(self, progress_callback=None) -> dict[str, int]:
        """
        Export database to SQL file.

        Args:
            progress_callback: Optional callback function(table_name, row_count)

        Returns:
            Dictionary mapping table names to exported row counts
        """
        self.connect()
        try:
            tables = self.get_tables()
            stats: dict[str, int] = {}

            with open(self.config.output_path, "w", encoding="utf-8") as f:
                # Write header
                f.write(f"-- MySQL dump for database: {self.config.database}\n")
                f.write("-- Generated by migrate-mysql\n\n")
                f.write("SET NAMES utf8mb4;\n")
                f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

                for table_name in tables:
                    f.write(f"-- Table: {table_name}\n")
                    f.write(
                        "-- --------------------------------------------------------\n\n"
                    )

                    # Export schema
                    if self.config.include_schema:
                        f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
                        create_stmt = self.get_create_table(table_name)
                        f.write(f"{create_stmt};\n\n")

                    # Export data
                    if self.config.include_data:
                        row_count = self.export_table_data(table_name, f)
                        stats[table_name] = row_count
                        f.write("\n")

                        if progress_callback:
                            progress_callback(table_name, row_count)

                f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

            return stats

        finally:
            self.disconnect()
