import pytest
import sys
import asyncio
from networkstats import monitor


@pytest.mark.asyncio
async def test_ping_once_success(monkeypatch):
    # Patch subprocess to simulate ping success
    class DummyProc:
        returncode = 0

        async def communicate(self):
            return b"", b""

    async def dummy_create_subprocess_exec(*args, **kwargs):
        return DummyProc()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", dummy_create_subprocess_exec)
    latency = await monitor._ping_once("8.8.8.8")
    assert isinstance(latency, float)
    assert latency >= 0


@pytest.mark.asyncio
async def test_ping_once_timeout(monkeypatch):
    # Patch subprocess to simulate timeout
    class DummyProc:
        returncode = 1
        async def communicate(self):
            await asyncio.sleep(2)
            return b"", b""
    async def dummy_create_subprocess_exec(*args, **kwargs):
        return DummyProc()
    monkeypatch.setattr(asyncio, "create_subprocess_exec", dummy_create_subprocess_exec)
    latency = await monitor._ping_once("bad.target", timeout=0.01)
    assert latency is None


def test_monitor_once(monkeypatch):
    # Patch _ping_once and record to avoid real pings and DB writes
    async def fake_ping_once(*args, **kwargs):
        return 42.0
    monkeypatch.setattr(monitor, "_ping_once", fake_ping_once)
    monkeypatch.setattr(monitor, "record", lambda *a, **k: None)
    # Patch config to use a single target and short interval
    monkeypatch.setattr(monitor, "cfg", {"targets": ["1.2.3.4"], "interval_sec": 0.01, "sqlite_path": ":memory:"})
    # Should complete after one iteration
    asyncio.run(monitor.monitor(once=True))


def test_monitor_long_running(monkeypatch):
    # Patch _ping_once and record to avoid real pings and DB writes
    async def fake_ping_once(*args, **kwargs):
        await asyncio.sleep(0.01)
        return 42.0
    monkeypatch.setattr(monitor, "_ping_once", fake_ping_once)
    monkeypatch.setattr(monitor, "record", lambda *a, **k: None)
    # Patch config to use a single target and short interval
    monkeypatch.setattr(monitor, "cfg", {"targets": ["1.2.3.4"], "interval_sec": 0.01, "sqlite_path": ":memory:"})
    # Should run for a short time and then be cancelled
    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(asyncio.wait_for(monitor.monitor(), timeout=0.05))
