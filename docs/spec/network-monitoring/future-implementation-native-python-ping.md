# Network Monitoring and Logging Specification: Future Implementation: Native Python Ping



## Architecture

Implement ICMP Echo Request/Reply using raw sockets in Python:

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

## Implementation Strategy

**Privilege Handling**

def can_use_raw_sockets() -> bool:
    """Check if we have permissions for raw sockets."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        s.close()
        return True
    except PermissionError:
        return False

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

**Fallback Mechanism**

class PingStrategy:
    def __init__(self):
        self.use_native = can_use_raw_sockets()
        self.native_ping = NativePing() if self.use_native else None
    
    async def ping(self, host: str, timeout: float = 1.0) -> float | None:
        if self.use_native:
            return await self.native_ping.ping(host, timeout)
        else:
            return await _ping_once(host, timeout)

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

**Platform-Specific Considerations**

**macOS**: Requires root or special entitlements

**Linux**: Can use unprivileged ICMP sockets (ping capability)

**Windows**: Administrator required for raw sockets

## Benefits of Native Implementation

**Cross-platform consistency**: Same behavior across all platforms

**Better performance**: No subprocess overhead

**Fine-grained control**: Direct access to ICMP fields

**Better error handling**: Can distinguish timeout vs unreachable

**Additional metrics**: Can extract TTL, packet loss patterns
