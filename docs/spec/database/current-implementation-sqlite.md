# Database Specification: Current Implementation: SQLite



## Schema Design

-- Core pings table
CREATE TABLE IF NOT EXISTS pings (
  ts INTEGER NOT NULL,           -- Unix timestamp
  target TEXT NOT NULL,          -- IP or hostname
  latency_ms REAL,              -- Latency in milliseconds
  success INTEGER,              -- 1 for success, 0 for failure
  PRIMARY KEY (ts, target)
);

-- Optimized indexes
CREATE INDEX IF NOT EXISTS idx_target_ts ON pings(target, ts DESC);
CREATE INDEX IF NOT EXISTS idx_ts ON pings(ts DESC);

-- Future: Additional metadata
CREATE TABLE IF NOT EXISTS ping_metadata (
  ts INTEGER NOT NULL,
  target TEXT NOT NULL,
  ttl INTEGER,                  -- Time to live
  packet_loss REAL,             -- Packet loss percentage
  jitter_ms REAL,               -- Jitter in milliseconds
  FOREIGN KEY (ts, target) REFERENCES pings(ts, target)
);

```sql
-- Core pings table
CREATE TABLE IF NOT EXISTS pings (
  ts INTEGER NOT NULL,           -- Unix timestamp
  target TEXT NOT NULL,          -- IP or hostname
  latency_ms REAL,              -- Latency in milliseconds
  success INTEGER,              -- 1 for success, 0 for failure
  PRIMARY KEY (ts, target)
);

-- Optimized indexes
CREATE INDEX IF NOT EXISTS idx_target_ts ON pings(target, ts DESC);
CREATE INDEX IF NOT EXISTS idx_ts ON pings(ts DESC);

-- Future: Additional metadata
CREATE TABLE IF NOT EXISTS ping_metadata (
  ts INTEGER NOT NULL,
  target TEXT NOT NULL,
  ttl INTEGER,                  -- Time to live
  packet_loss REAL,             -- Packet loss percentage
  jitter_ms REAL,               -- Jitter in milliseconds
  FOREIGN KEY (ts, target) REFERENCES pings(ts, target)
);

```

## Storage Architecture

import sqlite3
import pathlib
from contextlib import contextmanager
from typing import Iterator

class SQLiteStorage:
    def __init__(self, db_path: str):
        self.db_path = pathlib.Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database with schema."""
        with self.connection() as conn:
            conn.executescript(DDL)
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=30000000000")
    
    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

```python
import sqlite3
import pathlib
from contextlib import contextmanager
from typing import Iterator

class SQLiteStorage:
    def __init__(self, db_path: str):
        self.db_path = pathlib.Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database with schema."""
        with self.connection() as conn:
            conn.executescript(DDL)
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=30000000000")
    
    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

```

## Write Optimization

from queue import Queue
import threading
import time

class BatchWriter:
    """Batch writes for improved performance."""
    
    def __init__(self, storage: SQLiteStorage, batch_size: int = 100):
        self.storage = storage
        self.batch_size = batch_size
        self.queue = Queue()
        self.thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.thread.start()
    
    def write(self, target: str, latency_ms: float, success: bool):
        """Queue a write operation."""
        self.queue.put((int(time.time()), target, latency_ms, int(success)))
    
    def _writer_loop(self):
        """Background writer thread."""
        batch = []
        
        while True:
            try:
                # Collect items up to batch size or timeout
                deadline = time.time() + 1.0  # 1 second timeout
                
                while len(batch) < self.batch_size and time.time() < deadline:
                    timeout = deadline - time.time()
                    if timeout > 0:
                        try:
                            item = self.queue.get(timeout=timeout)
                            batch.append(item)
                        except:
                            break
                
                # Write batch if we have data
                if batch:
                    self._write_batch(batch)
                    batch = []
                    
            except Exception as e:
                logger.error(f"Batch writer error: {e}")
    
    def _write_batch(self, batch: list):
        """Write a batch of records."""
        with self.storage.connection() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO pings VALUES (?, ?, ?, ?)",
                batch
            )

```python
from queue import Queue
import threading
import time

class BatchWriter:
    """Batch writes for improved performance."""
    
    def __init__(self, storage: SQLiteStorage, batch_size: int = 100):
        self.storage = storage
        self.batch_size = batch_size
        self.queue = Queue()
        self.thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.thread.start()
    
    def write(self, target: str, latency_ms: float, success: bool):
        """Queue a write operation."""
        self.queue.put((int(time.time()), target, latency_ms, int(success)))
    
    def _writer_loop(self):
        """Background writer thread."""
        batch = []
        
        while True:
            try:
                # Collect items up to batch size or timeout
                deadline = time.time() + 1.0  # 1 second timeout
                
                while len(batch) < self.batch_size and time.time() < deadline:
                    timeout = deadline - time.time()
                    if timeout > 0:
                        try:
                            item = self.queue.get(timeout=timeout)
                            batch.append(item)
                        except:
                            break
                
                # Write batch if we have data
                if batch:
                    self._write_batch(batch)
                    batch = []
                    
            except Exception as e:
                logger.error(f"Batch writer error: {e}")
    
    def _write_batch(self, batch: list):
        """Write a batch of records."""
        with self.storage.connection() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO pings VALUES (?, ?, ?, ?)",
                batch
            )

```
