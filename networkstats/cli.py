import typer
import asyncio
from .monitor import monitor

app = typer.Typer(help="Network-uptime monitor CLI")


@app.command()
def run():
    """Run the ping monitor in foreground (CLI)."""
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        typer.echo("Bye!")


if __name__ == "__main__":
    app()
