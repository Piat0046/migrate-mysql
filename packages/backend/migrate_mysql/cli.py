"""CLI interface for MySQL migration tool."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .exporter import ExportConfig, MySQLExporter, TableFilter
from .importer import ImportConfig, MySQLImporter

console = Console()


@click.group()
@click.version_option()
def main():
    """MySQL database migration tool with filtering support."""
    pass


@main.command()
@click.option("--host", "-h", default="localhost", help="MySQL host")
@click.option("--port", "-P", default=3306, type=int, help="MySQL port")
@click.option("--user", "-u", required=True, help="MySQL user")
@click.option("--password", "-p", required=True, help="MySQL password")
@click.option("--database", "-d", required=True, help="Database to export")
@click.option("--output", "-o", required=True, type=click.Path(), help="Output SQL file")
@click.option(
    "--tables", "-t", multiple=True, help="Tables to export (can specify multiple)"
)
@click.option(
    "--filter",
    "-f",
    "filters",
    multiple=True,
    help='Table filter in format: table_name:where_clause (e.g., "users:created_at > \'2024-01-01\'")',
)
@click.option(
    "--columns",
    "-c",
    "column_specs",
    multiple=True,
    help='Column filter in format: table_name:col1,col2,col3 (e.g., "users:id,name,email")',
)
@click.option("--schema-only", is_flag=True, help="Export schema only, no data")
@click.option("--data-only", is_flag=True, help="Export data only, no schema")
@click.option(
    "--filter-file",
    type=click.Path(exists=True),
    help="JSON file containing filter configuration",
)
def export(
    host,
    port,
    user,
    password,
    database,
    output,
    tables,
    filters,
    column_specs,
    schema_only,
    data_only,
    filter_file,
):
    """Export MySQL database to SQL file."""
    table_filters = {}

    # Parse filter file if provided
    if filter_file:
        with open(filter_file, "r") as f:
            filter_config = json.load(f)
            for table_name, config in filter_config.items():
                table_filters[table_name] = TableFilter(
                    table_name=table_name,
                    where_clause=config.get("where"),
                    columns=config.get("columns"),
                )

    # Parse command-line filters
    for filter_spec in filters:
        if ":" in filter_spec:
            table_name, where_clause = filter_spec.split(":", 1)
            if table_name not in table_filters:
                table_filters[table_name] = TableFilter(table_name=table_name)
            table_filters[table_name].where_clause = where_clause

    # Parse column specifications
    for col_spec in column_specs:
        if ":" in col_spec:
            table_name, cols = col_spec.split(":", 1)
            columns = [c.strip() for c in cols.split(",")]
            if table_name not in table_filters:
                table_filters[table_name] = TableFilter(table_name=table_name)
            table_filters[table_name].columns = columns

    config = ExportConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        output_path=Path(output),
        tables=list(tables) if tables else None,
        table_filters=table_filters,
        include_schema=not data_only,
        include_data=not schema_only,
    )

    exporter = MySQLExporter(config)

    console.print(f"[bold blue]Exporting database:[/] {database}")
    console.print(f"[bold blue]Output file:[/] {output}")

    if table_filters:
        console.print("[bold blue]Filters:[/]")
        for name, tf in table_filters.items():
            filter_info = []
            if tf.where_clause:
                filter_info.append(f"WHERE {tf.where_clause}")
            if tf.columns:
                filter_info.append(f"columns: {', '.join(tf.columns)}")
            console.print(f"  - {name}: {'; '.join(filter_info)}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Exporting...", total=None)

        def on_progress(table_name, row_count):
            progress.update(task, description=f"Exported {table_name}: {row_count} rows")

        try:
            stats = exporter.export(progress_callback=on_progress)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise click.Abort()

    # Show results
    table = Table(title="Export Results")
    table.add_column("Table", style="cyan")
    table.add_column("Rows", justify="right", style="green")

    total_rows = 0
    for table_name, row_count in stats.items():
        table.add_row(table_name, str(row_count))
        total_rows += row_count

    table.add_row("[bold]Total[/]", f"[bold]{total_rows}[/]")
    console.print(table)
    console.print(f"[bold green]Export completed:[/] {output}")


@main.command("import")
@click.option("--host", "-h", default="localhost", help="MySQL host")
@click.option("--port", "-P", default=3306, type=int, help="MySQL port")
@click.option("--user", "-u", required=True, help="MySQL user")
@click.option("--password", "-p", required=True, help="MySQL password")
@click.option("--database", "-d", required=True, help="Target database")
@click.option("--input", "-i", "input_file", required=True, type=click.Path(exists=True), help="Input SQL file")
@click.option(
    "--no-create-db",
    is_flag=True,
    help="Don't create database if it doesn't exist",
)
def import_cmd(host, port, user, password, database, input_file, no_create_db):
    """Import SQL file into MySQL database."""
    config = ImportConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        input_path=Path(input_file),
        create_database=not no_create_db,
    )

    importer = MySQLImporter(config)

    console.print(f"[bold blue]Importing to database:[/] {database}")
    console.print(f"[bold blue]From file:[/] {input_file}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Importing...", total=None)

        def on_progress(stmt_count):
            progress.update(task, description=f"Executed {stmt_count} statements")

        try:
            stats = importer.import_data(progress_callback=on_progress)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise click.Abort()

    # Show results
    table = Table(title="Import Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Statements executed", str(stats["statements"]))
    table.add_row("Tables created", str(stats["tables_created"]))
    table.add_row("Rows inserted", str(stats["rows_inserted"]))

    console.print(table)
    console.print("[bold green]Import completed![/]")


if __name__ == "__main__":
    main()
