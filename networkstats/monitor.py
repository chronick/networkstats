import asyncio
import subprocess
import sys
import statistics
import logging
import time
from .storage import record
from .config import load

log = logging.getLogger(__name__)
cfg = load()


async def _ping_once(target: str, timeout: float = 1.0) -> float | None:
    """Ping using system ping -c1. Returns latency_ms or None."""
    cmd = (
        ["ping", "-c1", "-t1", target]
        if sys.platform == "darwin"
        else ["ping", "-c1", target]
    )
    start = time.perf_counter()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        await asyncio.wait_for(proc.communicate(), timeout=timeout)
        if proc.returncode == 0:
            return (time.perf_counter() - start) * 1000.0
    except asyncio.TimeoutError:
        pass
    return None


async def monitor():
    """Main async ping loop for all targets."""
    targets = cfg["targets"]
    interval = cfg["interval_sec"]
    while True:
        tasks = {asyncio.create_task(_ping_once(t)): t for t in targets}
        for coro in asyncio.as_completed(tasks):
            target = tasks[coro]
            latency = await coro
            record(target, latency or 0.0, latency is not None)
        await asyncio.sleep(interval)
