import typer
import asyncio
import logging
from .monitor import monitor

app = typer.Typer(help="Network-uptime monitor CLI")


def _configure_logging(log_level: str) -> None:
    """Configure root logger with the given log level."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(level=numeric_level, format='%(levelname)s: %(message)s')


@app.command()
def run(
    log_level: str = typer.Option(
        "WARNING",
        "--log-level",
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        show_default=True,
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Pass -v to ping for verbose output (overrides log level mapping)",
    ),
    quiet: bool = typer.Option(
        False,
        "-q",
        "--quiet",
        help="Pass -q to ping for quiet output (overrides log level mapping)",
    ),
    extra_ping_args: str = typer.Option(
        "",
        "--ping-args",
        help="Extra arguments to pass to ping (as a single string)",
    ),
) -> None:
    """Run the ping monitor in foreground (CLI).

    Args:
        log_level: Logging level for output (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        verbose: Pass -v to ping for verbose output.
        quiet: Pass -q to ping for quiet output.
        extra_ping_args: Extra arguments to pass to ping.
    """
    _configure_logging(log_level)
    logging.info("Starting network monitor")
    try:
        asyncio.run(monitor(verbose=verbose, quiet=quiet, extra_ping_args=extra_ping_args))
    except KeyboardInterrupt:
        typer.echo("Bye!")


if __name__ == "__main__":
    app()
