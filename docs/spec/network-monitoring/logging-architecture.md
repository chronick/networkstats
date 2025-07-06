# Network Monitoring and Logging Specification: Logging Architecture



## Structured Logging

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

## Log Levels and Categories

**DEBUG**: Detailed ping results, packet contents

**INFO**: Target status changes, configuration updates

**WARNING**: Timeouts, high latency warnings

**ERROR**: Connection failures, permission issues

**CRITICAL**: Engine failures, unrecoverable errors

## Log Rotation

from logging.handlers import RotatingFileHandler

# Configure log rotation
handler = RotatingFileHandler(
    'networkstats.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)

```python
from logging.handlers import RotatingFileHandler

# Configure log rotation
handler = RotatingFileHandler(
    'networkstats.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)

```
