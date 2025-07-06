import pytest
import sys
import asyncio
from networkstats import monitor
import socket
import struct
import time
import types
from unittest.mock import patch, MagicMock


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


class DummySocket:
    def __init__(self):
        self.sent_packet = None
        self.recv_called = False
    def sendto(self, packet, addr):
        self.sent_packet = packet
        return len(packet)
    def recvfrom(self, bufsize):
        self.recv_called = True
        # Simulate a valid ICMP Echo Reply packet
        # IP header: 20 bytes, ICMP header: 8 bytes, payload: 8 bytes (timestamp)
        ip_header = bytes([0x45, 0]*19)  # minimal IP header
        icmp_header = struct.pack('!BBHHH', 0, 0, 0, 1234, 1)  # type=0 (reply), id=1234
        payload = struct.pack('!d', time.time())
        return ip_header + icmp_header + payload, ('8.8.8.8', 0)
    def setblocking(self, flag):
        pass
    def close(self):
        pass
    def fileno(self):
        return 42


@pytest.mark.asyncio
async def test_native_ping_success(monkeypatch):
    from networkstats.monitor import NativePing
    # Patch socket.socket to return DummySocket
    monkeypatch.setattr(socket, "socket", lambda *a, **k: DummySocket())
    monkeypatch.setattr(socket, "gethostbyname", lambda host: "8.8.8.8")
    # Patch select.select to always indicate ready
    monkeypatch.setattr("select.select", lambda r, w, x, t: ([r[0]], [], []))
    # Patch os.getpid to return a fixed id
    import os
    monkeypatch.setattr(os, "getpid", lambda: 1234)
    pinger = NativePing()
    latency = await pinger.ping("8.8.8.8")
    assert isinstance(latency, float)
    assert latency > 0


@pytest.mark.asyncio
async def test_native_ping_timeout(monkeypatch):
    from networkstats.monitor import NativePing
    # Patch socket.socket to return DummySocket
    monkeypatch.setattr(socket, "socket", lambda *a, **k: DummySocket())
    monkeypatch.setattr(socket, "gethostbyname", lambda host: "8.8.8.8")
    # Patch select.select to always timeout
    monkeypatch.setattr("select.select", lambda r, w, x, t: ([], [], []))
    import os
    monkeypatch.setattr(os, "getpid", lambda: 1234)
    pinger = NativePing()
    latency = await pinger.ping("8.8.8.8", timeout=0.01)
    assert latency is None


@pytest.mark.asyncio
def test_can_use_raw_sockets_true(monkeypatch):
    from networkstats import monitor
    class DummySocket:
        def close(self):
            pass
        def fileno(self):
            return 44
    monkeypatch.setattr(monitor.socket, "socket", lambda *a, **k: DummySocket())
    assert monitor.can_use_raw_sockets() is True


@pytest.mark.asyncio
def test_can_use_raw_sockets_false(monkeypatch):
    from networkstats import monitor
    def raise_permission(*a, **k):
        raise PermissionError
    monkeypatch.setattr(monitor.socket, "socket", raise_permission)
    assert monitor.can_use_raw_sockets() is False


@pytest.mark.asyncio
async def test_ping_strategy_native(monkeypatch):
    from networkstats import monitor
    # Simulate raw sockets available
    monkeypatch.setattr(monitor, "can_use_raw_sockets", lambda: True)
    class DummyNativePing:
        async def ping(self, host, timeout=1.0):
            return 42.0
    monkeypatch.setattr(monitor, "NativePing", lambda: DummyNativePing())
    ps = monitor.PingStrategy()
    latency = await ps.ping("8.8.8.8")
    assert latency == 42.0


@pytest.mark.asyncio
async def test_ping_strategy_fallback(monkeypatch):
    from networkstats import monitor
    # Simulate raw sockets unavailable
    monkeypatch.setattr(monitor, "can_use_raw_sockets", lambda: False)
    monkeypatch.setattr(monitor, "NativePing", lambda: None)
    async def fake_ping_once(host, timeout=1.0):
        return 99.0
    monkeypatch.setattr(monitor, "_ping_once", fake_ping_once)
    ps = monitor.PingStrategy()
    latency = await ps.ping("8.8.8.8")
    assert latency == 99.0


def test_native_ping_checksum(monkeypatch):
    from networkstats.monitor import NativePing
    monkeypatch.setattr(socket, "socket", lambda *a, **k: DummySocket())
    pinger = NativePing()
    # Example data: b'\x08\x00' + 6 zero bytes
    data = b'\x08\x00' + b'\x00' * 6
    # The checksum should be a 16-bit int
    result = pinger.checksum(data)
    assert isinstance(result, int)
    assert 0 <= result <= 0xFFFF


def test_native_ping_create_packet(monkeypatch):
    from networkstats.monitor import NativePing
    import os
    monkeypatch.setattr(socket, "socket", lambda *a, **k: DummySocket())
    monkeypatch.setattr(os, "getpid", lambda: 1234)
    pinger = NativePing()
    packet = pinger.create_packet()
    assert isinstance(packet, bytes)
    assert len(packet) > 8  # Should be at least header + timestamp


@pytest.mark.asyncio
async def test_native_ping_sequence_increment(monkeypatch):
    from networkstats.monitor import NativePing
    monkeypatch.setattr(socket, "socket", lambda *a, **k: DummySocket())
    monkeypatch.setattr(socket, "gethostbyname", lambda host: "8.8.8.8")
    monkeypatch.setattr("select.select", lambda r, w, x, t: ([r[0]], [], []))
    import os
    monkeypatch.setattr(os, "getpid", lambda: 1234)
    pinger = NativePing()
    seq_before = pinger.sequence
    await pinger.ping("8.8.8.8")
    assert pinger.sequence == seq_before + 1


@pytest.mark.asyncio
async def test_native_ping_invalid_host(monkeypatch):
    from networkstats.monitor import NativePing
    monkeypatch.setattr(socket, "socket", lambda *a, **k: DummySocket())
    def raise_gaierror(host):
        raise socket.gaierror
    monkeypatch.setattr(socket, "gethostbyname", raise_gaierror)
    import os
    monkeypatch.setattr(os, "getpid", lambda: 1234)
    pinger = NativePing()
    result = await pinger.ping("bad.host")
    assert result is None


@pytest.mark.asyncio
async def test_native_ping_socket_error(monkeypatch):
    from networkstats.monitor import NativePing
    class ErrorSocket(DummySocket):
        def sendto(self, packet, addr):
            raise OSError("sendto failed")
        def fileno(self):
            return 43
    monkeypatch.setattr(socket, "socket", lambda *a, **k: ErrorSocket())
    monkeypatch.setattr(socket, "gethostbyname", lambda host: "8.8.8.8")
    import os
    monkeypatch.setattr(os, "getpid", lambda: 1234)
    pinger = NativePing()
    result = await pinger.ping("8.8.8.8")
    assert result is None
