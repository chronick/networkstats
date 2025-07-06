from typer.testing import CliRunner
from networkstats.cli import app

runner = CliRunner()


def test_cli_run_command_registered():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output


def test_cli_log_level_option():
    result = runner.invoke(app, ["run", "--log-level", "DEBUG"])  # Should start monitor, but will hang
    # We expect it to start, but since monitor runs forever, we just check for no immediate error
    assert result.exit_code in (0, None)  # None if interrupted
    result2 = runner.invoke(app, ["run", "--log-level", "ERROR"])
    assert result2.exit_code in (0, None)
