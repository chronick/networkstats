# Network Monitoring and Logging Specification

## Overview

The network monitoring engine is the core component responsible for continuously checking network connectivity to configured targets. It provides both subprocess-based ping (current) and native Python implementation (future) with comprehensive logging and error handling.

## Current Implementation

### Subprocess-based Ping

The current implementation uses the system's `ping` command via subprocess:

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
- Uses system's native ping implementation
- Supports all ping options and flags
- Battle-tested reliability

**Disadvantages:**
- Platform-specific command variations
- Subprocess overhead
- Parsing output can be fragile
- Requires external binary

## Future Implementation: Native Python Ping

### Architecture

Implement ICMP Echo Request/Reply using raw sockets in Python:

```python
import socket
import struct
import time
import select
import os

class NativePing:
    """Native Python ICMP ping implementation."""
    
    ICMP_ECHO_REQUEST = 8
    ICMP_ECHO_REPLY = 0
    
    def __init__(self):
        # Create raw socket (requires root/admin privileges)
        self.socket = socket.socket(
            socket.AF_INET, 
            socket.SOCK_RAW, 
            socket.getprotobyname("icmp")
        )
        self.socket.setblocking(False)
        self.identifier = os.getpid() & 0xFFFF
        self.sequence = 0
    
    def checksum(self, data: bytes) -> int:
        """Calculate ICMP checksum."""
        if len(data) % 2:
            data += b'\x00'
        
        words = struct.unpack('!%dH' % (len(data) // 2), data)
        total = sum(words)
        
        # Add high 16 bits to low 16 bits
        total = (total >> 16) + (total & 0xffff)
        total += (total >> 16)  # Add carry
        
        return ~total & 0xffff
    
    def create_packet(self) -> bytes:
        """Create ICMP Echo Request packet."""
        # Header: type (8), code (8), checksum (16), id (16), sequence (16)
        header = struct.pack('!BBHHH', 
            self.ICMP_ECHO_REQUEST, 0, 0, 
            self.identifier, self.sequence
        )
        
        # Add timestamp as payload
        timestamp = struct.pack('!d', time.time())
        
        # Calculate checksum
        packet = header + timestamp
        checksum = self.checksum(packet)
        
        # Rebuild packet with checksum
        header = struct.pack('!BBHHH',
            self.ICMP_ECHO_REQUEST, 0, checksum,
            self.identifier, self.sequence
        )
        
        return header + timestamp
    
    async def ping(self, host: str, timeout: float = 1.0) -> float | None:
        """Send ping and return latency in milliseconds, or None if failed."""
        try:
            # Resolve hostname
            dest_addr = socket.gethostbyname(host)
            
            # Create and send packet
            packet = self.create_packet()
            self.socket.sendto(packet, (dest_addr, 0))
            send_time = time.time()
            
            # Wait for reply
            while True:
                ready = select.select([self.socket], [], [], timeout)
                if not ready[0]:
                    return None  # Timeout
                
                recv_time = time.time()
                recv_packet, addr = self.socket.recvfrom(1024)
                
                # Parse ICMP header (after IP header)
                ip_header_len = (recv_packet[0] & 0x0f) * 4
                icmp_header = recv_packet[ip_header_len:ip_header_len + 8]
                
                type_, code, checksum, packet_id, sequence = struct.unpack(
                    '!BBHHH', icmp_header
                )
                
                # Check if this is our reply
                if (type_ == self.ICMP_ECHO_REPLY and 
                    packet_id == self.identifier and
                    addr[0] == dest_addr):
                    
                    # Calculate latency
                    latency_ms = (recv_time - send_time) * 1000
                    return latency_ms
                
                # Check for timeout
                if recv_time - send_time > timeout:
                    return None
                    
        except Exception as e:
            logging.error(f"Native ping error for {host}: {e}")
            return None
        finally:
            self.sequence += 1
```

### Implementation Strategy

1. **Privilege Handling**
   ```python
   def can_use_raw_sockets() -> bool:
       """Check if we have permissions for raw sockets."""
       try:
           s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
           s.close()
           return True
       except PermissionError:
           return False
   ```

2. **Fallback Mechanism**
   ```python
   class PingStrategy:
       def __init__(self):
           self.use_native = can_use_raw_sockets()
           self.native_ping = NativePing() if self.use_native else None
       
       async def ping(self, host: str, timeout: float = 1.0) -> float | None:
           if self.use_native:
               return await self.native_ping.ping(host, timeout)
           else:
               return await _ping_once(host, timeout)
   ```

3. **Platform-Specific Considerations**
   - **macOS**: Requires root or special entitlements
   - **Linux**: Can use unprivileged ICMP sockets (ping capability)
   - **Windows**: Administrator required for raw sockets

### Benefits of Native Implementation

1. **Cross-platform consistency**: Same behavior across all platforms
2. **Better performance**: No subprocess overhead
3. **Fine-grained control**: Direct access to ICMP fields
4. **Better error handling**: Can distinguish timeout vs unreachable
5. **Additional metrics**: Can extract TTL, packet loss patterns

## Monitoring Engine Architecture

### Async Task Management

```python
class MonitoringEngine:
    def __init__(self, config: dict):
        self.config = config
        self.ping_strategy = PingStrategy()
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 10))
        self.tasks: dict[str, asyncio.Task] = {}
    
    async def monitor_target(self, target: str):
        """Monitor a single target continuously."""
        interval = self.config['interval_sec']
        
        while True:
            try:
                latency = await self.ping_strategy.ping(target)
                success = latency is not None
                
                # Record result
                await self.record_result(target, latency or 0.0, success)
                
                # Emit event for UI updates
                await self.emit_event('ping_result', {
                    'target': target,
                    'latency': latency,
                    'success': success,
                    'timestamp': time.time()
                })
                
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Error monitoring {target}: {e}")
            
            await asyncio.sleep(interval)
```

### Dynamic Target Management

```python
async def add_target(self, target: str):
    """Add a new monitoring target."""
    if target not in self.tasks:
        task = asyncio.create_task(self.monitor_target(target))
        self.tasks[target] = task
        logger.info(f"Added monitoring target: {target}")

async def remove_target(self, target: str):
    """Remove a monitoring target."""
    if target in self.tasks:
        self.tasks[target].cancel()
        await self.tasks[target]
        del self.tasks[target]
        logger.info(f"Removed monitoring target: {target}")
```

## Logging Architecture

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### Log Levels and Categories

1. **DEBUG**: Detailed ping results, packet contents
2. **INFO**: Target status changes, configuration updates
3. **WARNING**: Timeouts, high latency warnings
4. **ERROR**: Connection failures, permission issues
5. **CRITICAL**: Engine failures, unrecoverable errors

### Log Rotation

```python
from logging.handlers import RotatingFileHandler

# Configure log rotation
handler = RotatingFileHandler(
    'networkstats.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
```

## Performance Optimization

### Concurrent Monitoring

- Use asyncio for concurrent target monitoring
- Configurable worker pool size
- Batch database writes for efficiency

### Resource Management

```python
class ResourceMonitor:
    """Monitor and limit resource usage."""
    
    MAX_CPU_PERCENT = 5.0
    MAX_MEMORY_MB = 100
    
    async def check_resources(self):
        """Check if we're within resource limits."""
        import psutil
        
        process = psutil.Process()
        cpu_percent = process.cpu_percent(interval=1)
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if cpu_percent > self.MAX_CPU_PERCENT:
            logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
            # Implement throttling
            
        if memory_mb > self.MAX_MEMORY_MB:
            logger.warning(f"High memory usage: {memory_mb:.1f}MB")
            # Implement cleanup
```

## Error Handling

### Graceful Degradation

1. **Network errors**: Log and continue monitoring
2. **Permission errors**: Fall back to subprocess ping
3. **Resource limits**: Throttle monitoring frequency
4. **Database errors**: Queue writes for retry

### Recovery Strategies

```python
class ErrorRecovery:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.backoff_times = defaultdict(float)
    
    async def handle_error(self, target: str, error: Exception):
        """Implement exponential backoff for repeated errors."""
        self.error_counts[target] += 1
        
        if self.error_counts[target] > 3:
            # Exponential backoff
            self.backoff_times[target] = min(
                300,  # Max 5 minutes
                2 ** self.error_counts[target]
            )
            logger.warning(
                f"Target {target} backing off for {self.backoff_times[target]}s"
            )
```

## Testing Strategy

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_native_ping():
    """Test native ping implementation."""
    ping = NativePing()
    
    # Mock socket operations
    with patch('socket.socket') as mock_socket:
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.recvfrom.return_value = (create_mock_reply(), ('8.8.8.8', 0))
        
        latency = await ping.ping('8.8.8.8')
        assert latency is not None
        assert 0 < latency < 1000
```

### Integration Tests

```python
@pytest.mark.integration
async def test_monitoring_engine():
    """Test full monitoring engine."""
    config = {
        'targets': ['127.0.0.1'],
        'interval_sec': 1
    }
    
    engine = MonitoringEngine(config)
    await engine.start()
    
    # Wait for results
    await asyncio.sleep(2)
    
    # Verify results recorded
    results = await fetch_recent_results('127.0.0.1', 5)
    assert len(results) >= 1
```

## Future Enhancements

1. **IPv6 Support**: Extend native ping for IPv6
2. **TCP/UDP Monitoring**: Beyond ICMP
3. **HTTP/HTTPS Checks**: Application-layer monitoring
4. **DNS Resolution Time**: Track DNS performance
5. **Traceroute Integration**: Path analysis
6. **Jitter Calculation**: Network stability metrics
7. **Packet Loss Patterns**: Advanced diagnostics
8. **MTU Discovery**: Network path analysis 