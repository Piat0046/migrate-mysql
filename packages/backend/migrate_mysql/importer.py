"""MySQL database importer."""

from dataclasses import dataclass
from pathlib import Path

import mysql.connector
from mysql.connector import MySQLConnection


@dataclass
class ImportConfig:
    """Configuration for database import."""

    host: str
    port: int
    user: str
    password: str
    database: str
    input_path: Path
    create_database: bool = True


class MySQLImporter:
    """Import SQL file into MySQL database."""

    def __init__(self, config: ImportConfig):
        self.config = config
        self.conn: MySQLConnection | None = None

    def connect(self, use_database: bool = True) -> None:
        """Establish database connection."""
        conn_params = {
            "host": self.config.host,
            "port": self.config.port,
            "user": self.config.user,
            "password": self.config.password,
        }

        if use_database:
            conn_params["database"] = self.config.database

        self.conn = mysql.connector.connect(**conn_params)

    def disconnect(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_database_if_needed(self) -> None:
        """Create the target database if it doesn't exist."""
        if not self.config.create_database:
            return

        self.connect(use_database=False)
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.config.database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.close()
            self.conn.commit()
        finally:
            self.disconnect()

    def execute_sql_file(self, progress_callback=None) -> dict[str, int]:
        """
        Execute SQL file on target database.

        Args:
            progress_callback: Optional callback function(statement_count)

        Returns:
            Statistics about the import
        """
        stats = {
            "statements": 0,
            "tables_created": 0,
            "rows_inserted": 0,
        }

        self.connect()
        try:
            cursor = self.conn.cursor()

            with open(self.config.input_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split into statements
            statements = self._split_statements(content)

            for stmt in statements:
                stmt = stmt.strip()
                if not stmt or stmt.startswith("--"):
                    continue

                try:
                    cursor.execute(stmt)
                    stats["statements"] += 1

                    if stmt.upper().startswith("CREATE TABLE"):
                        stats["tables_created"] += 1
                    elif stmt.upper().startswith("INSERT"):
                        stats["rows_inserted"] += cursor.rowcount

                    if progress_callback and stats["statements"] % 100 == 0:
                        progress_callback(stats["statements"])

                except mysql.connector.Error as e:
                    # Log but continue on non-critical errors
                    if "Duplicate entry" in str(e):
                        continue
                    raise

            self.conn.commit()
            cursor.close()

            return stats

        finally:
            self.disconnect()

    def _split_statements(self, content: str) -> list[str]:
        """Split SQL content into individual statements."""
        statements = []
        current = []
        in_string = False
        string_char = None
        i = 0

        while i < len(content):
            char = content[i]

            # Handle string literals
            if char in ("'", '"') and (i == 0 or content[i - 1] != "\\"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None

            # Handle statement delimiter
            if char == ";" and not in_string:
                current.append(char)
                stmt = "".join(current).strip()
                if stmt and not stmt.startswith("--"):
                    statements.append(stmt)
                current = []
            else:
                current.append(char)

            i += 1

        # Handle any remaining content
        if current:
            stmt = "".join(current).strip()
            if stmt and not stmt.startswith("--"):
                statements.append(stmt)

        return statements

    def import_data(self, progress_callback=None) -> dict[str, int]:
        """
        Import SQL file into database.

        Args:
            progress_callback: Optional callback function(statement_count)

        Returns:
            Statistics about the import
        """
        self.create_database_if_needed()
        return self.execute_sql_file(progress_callback)
