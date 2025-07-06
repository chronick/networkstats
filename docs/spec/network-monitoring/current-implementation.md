# Network Monitoring and Logging Specification: Current Implementation



## Subprocess-based Ping

The current implementation uses the system's `ping` command via subprocess:

def _run_ping_sync(
    target: str,
    timeout: float = 1.0,
    verbose: bool = False,
    quiet: bool = False,
    extra_ping_args: str = ""
) -> tuple[bool, float]:
    """Run ping synchronously in a thread. Returns (success, latency_ms)."""
    cmd = ["ping", "-c1", "-t1"] + extra_flags + [target]
    result = subprocess.run(cmd, ...)
    return result.returncode == 0, latency

```python
def _run_ping_sync(
    target: str,
    timeout: float = 1.0,
    verbose: bool = False,
    quiet: bool = False,
    extra_ping_args: str = ""
) -> tuple[bool, float]:
    """Run ping synchronously in a thread. Returns (success, latency_ms)."""
    cmd = ["ping", "-c1", "-t1"] + extra_flags + [target]
    result = subprocess.run(cmd, ...)
    return result.returncode == 0, latency

```

**Advantages:**

Uses system's native ping implementation

Supports all ping options and flags

Battle-tested reliability

**Disadvantages:**

Platform-specific command variations

Subprocess overhead

Parsing output can be fragile

Requires external binary
