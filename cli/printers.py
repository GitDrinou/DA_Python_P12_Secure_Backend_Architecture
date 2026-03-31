from cli.console import console, error_console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def _to_text(value):
    if value is None:
        return "-"
    return str(value)


def print_success(message):
    console.print(Panel.fit(message, title="SUCCESS", border_style="green"))


def print_info(message):
    console.print(Panel.fit(message, title="INFO", border_style="cyan"))


def print_warning(message):
    console.print(Panel.fit(message, title="WARNIND", border_style="yellow"))


def print_error(message):
    error_console.print(Panel.fit(message, title="ERROR", border_style="red"))


def print_forbidden(message):
    console.print(
        Panel.fit(
            message,
            title="FORBIDDEN",
            border_style="magenta"
        )
    )


def print_row(data, title="DETAILS"):
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for key, value in data.items():
        table.add_row(str(key), _to_text(value))

    console.print(table)


def print_collection(rows, title="RESULTS"):
    if not rows:
        print_info("No results found")
        return

    columns = list(rows[0].keys())
    table = Table(title=title, show_header=True, header_style="bold cyan")

    for column in columns:
        table.add_column(str(column), overflow="fold")

    for row in rows:
        table.add_row(*[_to_text(row.get(column)) for column in columns])

    console.print(table)


def print_kv_panel(title, data):
    body = "\n".join(
        f"[bold]{key}[/bold]: {_to_text(value)}" for key, value in
        data.items()
    )
    console.print(Panel(body, title=title, border_style="blue"))


def print_auth_message(message):
    text = Text(message)
    console.print(Panel.fit(text, title="AUTH", border_style="green"))
