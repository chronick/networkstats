from typer.testing import CliRunner
from networkstats.cli import app, run

runner = CliRunner()


def test_cli_run_command_registered():
    result = runner.invoke(app, ["--help"])
    print("HELP OUTPUT:\n", result.output)
    assert result.exit_code == 0
    assert "run" in result.output


def test_cli_log_level_option():
    import asyncio
    async def fake_monitor(*args, **kwargs):
        return None
    from unittest.mock import patch
    with patch("networkstats.cli.monitor", fake_monitor):
        result = runner.invoke(app, ["--log-level", "DEBUG"])
        if result.exit_code not in (0, None):
            print("STDOUT:\n", result.stdout)
            print("EXCEPTION:\n", result.exception)
        assert result.exit_code in (0, None)  # None if interrupted
        result2 = runner.invoke(app, ["--log-level", "ERROR"])
        assert result2.exit_code in (0, None)


def test_cli_run_once_flag(monkeypatch):
    async def fake_monitor(*args, **kwargs):
        return None
    from unittest.mock import patch
    with patch("networkstats.cli.monitor", fake_monitor):
        result = runner.invoke(app, ["--once"])
        print("OUTPUT:\n", result.output)
        assert result.exit_code == 0


def test_cli_long_running_monitor(monkeypatch):
    import asyncio
    async def fake_monitor(*args, **kwargs):
        await asyncio.sleep(0.2)
    from unittest.mock import patch
    with patch("networkstats.cli.monitor", fake_monitor):
        result = runner.invoke(app, ["--log-level", "DEBUG"])
        print("OUTPUT:\n", result.output)
        assert result.exit_code in (0, None)
