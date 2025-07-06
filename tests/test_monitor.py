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
