"""Cumpiler utilities."""

import sys
from rich.console import Console

console = Console()

EXIT_SUCCESS: int = 0
EXIT_ERROR: int = 1

RICH_COLOR_ORANGE = "color(208)"


def log(*args, end: str | None = "\n", file=sys.stderr, **kwargs):
    """Prints log messages to stderr."""
    # Note that stderr is unbuffered: always flush.
    print(file=sys.stderr, *args, end=end, **kwargs)


def log_info(
    message: str = "", *args, end: str | None = "\n", file=sys.stderr, **kwargs
):
    """Prints an informational message to stderr in terminal blue-tint."""
    # Note that stderr is unbuffered: always flush.

    with console.capture() as capture:
        console.print(f"[blue]{message}[/blue]")

    output = capture.get()
    print(output, *args, end=end, file=file, **kwargs)


def log_warning(
    message: str = "", *args, end: str | None = "\n", file=sys.stderr, **kwargs
):
    """Prints a warning message to stderr in terminal yellow-tint."""
    # Note that stderr is unbuffered: always flush.

    with console.capture() as capture:
        console.print(f"[yellow]{message}[/yellow]")

    output = capture.get()
    print(output, *args, end=end, file=file, **kwargs)


def log_success(
    message: str = "", *args, end: str | None = "\n", file=sys.stderr, **kwargs
):
    """Prints a success message to stderr in terminal green-tint."""
    # Note that stderr is unbuffered: always flush.

    with console.capture() as capture:
        console.print(f"[green]{message}[/green]")

    output = capture.get()
    print(output, *args, end=end, file=file, **kwargs)


def log_error(
    message: str = "", *args, end: str | None = "\n", file=sys.stderr, **kwargs
):
    """Prints an error message to stderr in terminal red-tint."""
    # Note that stderr is unbuffered: always flush.

    with console.capture() as capture:
        console.print(f"[red]{message}[/red]")

    output = capture.get()
    print(output, *args, end=end, file=file, **kwargs)
