import pytest
from typer.testing import CliRunner
from networkstats.cli import app

runner = CliRunner()


def test_cli_run_command_registered():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
