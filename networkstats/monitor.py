import asyncio
import subprocess
import sys
import statistics
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from .storage import record
from .config import load

log = logging.getLogger(__name__)
cfg = load()

# Thread pool for subprocess operations
executor = ThreadPoolExecutor(max_workers=10)


def _run_ping_sync(
    target: str,
    timeout: float = 1.0,
    verbose: bool = False,
    quiet: bool = False,
    extra_ping_args: str = ""
) -> tuple[bool, float]:
    """Run ping synchronously in a thread. Returns (success, latency_ms)."""
    # Determine loglevel and set ping verbosity unless overridden
    loglevel = log.getEffectiveLevel()
    extra_flags = []
    if verbose:
        extra_flags.append("-v")
    elif quiet:
        extra_flags.append("-q")
    else:
        if loglevel <= logging.DEBUG:
            extra_flags.append("-v")
        elif loglevel >= logging.WARNING:
            extra_flags.append("-q")
    # Parse extra_ping_args string into list if provided
    if extra_ping_args:
        import shlex
        extra_flags.extend(shlex.split(extra_ping_args))
    cmd = (
        ["ping", "-c1", "-t1"] + extra_flags + [target]
        if sys.platform == "darwin"
        else ["ping", "-c1"] + extra_flags + [target]
    )
    start = time.perf_counter()
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False
        )
        latency = (time.perf_counter() - start) * 1000.0
        # Log ping output
        if result.stdout:
            log.debug(f"ping stdout for {target}: {result.stdout.decode(errors='replace').strip()}")
        if result.stderr:
            log.warning(f"ping stderr for {target}: {result.stderr.decode(errors='replace').strip()}")
        return result.returncode == 0, latency
    except subprocess.TimeoutExpired:
        log.warning(f"ping to {target} timed out after {timeout}s")
        return False, 0.0
    except Exception as e:
        log.error(f"Unexpected error pinging {target}: {e}")
        return False, 0.0


async def _ping_once(
    target: str,
    timeout: float = 1.0,
    verbose: bool = False,
    quiet: bool = False,
    extra_ping_args: str = ""
) -> float | None:
    """Ping using system ping -c1. Returns latency_ms or None."""
    log.debug(f"Pinging {target}")
    try:
        loop = asyncio.get_event_loop()
        success, latency = await loop.run_in_executor(
            executor, _run_ping_sync, target, timeout, verbose, quiet, extra_ping_args
        )
        if success:
            log.debug(f"Ping to {target} succeeded: {latency:.2f} ms")
            return latency
        else:
            log.debug(f"Ping to {target} failed or timed out")
            return None
    except Exception as e:
        log.error(f"Unexpected error in async ping wrapper for {target}: {e}")
        return None


async def monitor(verbose: bool = False, quiet: bool = False, extra_ping_args: str = "", once: bool = False):
    """Main async ping loop for all targets.

    Args:
        verbose: Pass -v to ping for verbose output.
        quiet: Pass -q to ping for quiet output.
        extra_ping_args: Extra arguments to pass to ping.
        once: If True, run only one iteration and exit.
    """
    targets = cfg["targets"]
    interval = cfg["interval_sec"]
    log.info(f"Starting monitor loop for targets: {targets}, interval: {interval}s")
    log.info(f"Using executor with {executor._max_workers} workers")
    log.info(f"Connected to database at {cfg['sqlite_path']}")
    try:
        while True:
            log.debug("Starting new monitor iteration")
            # Create tasks with target mapping
            tasks = [asyncio.create_task(_ping_once(t, verbose=verbose, quiet=quiet, extra_ping_args=extra_ping_args)) for t in targets]
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Process results
            for target, result in zip(targets, results):
                if isinstance(result, Exception):
                    log.error(f"Error pinging {target}: {result}")
                    record(target, 0.0, False)
                else:
                    latency = result
                    log.debug(f"Result for {target}: latency={latency} ms, success={latency is not None}")
                    record(target, latency or 0.0, latency is not None)
            if once:
                break
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        log.info("Monitor cancelled, shutting down cleanly.")
        # Optionally: clean up or flush data here
        raise
