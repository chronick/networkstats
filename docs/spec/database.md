# Database Specification

## Overview

The database layer provides efficient time-series storage for network monitoring data, supporting high-frequency writes and complex analytical queries. The architecture supports a migration path from SQLite (current) to DuckDB (future) for enhanced performance and analytical capabilities.

## Current Implementation: SQLite

### Schema Design

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

### Storage Architecture

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

### Write Optimization

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

## Future Implementation: DuckDB

### Why DuckDB?

1. **Columnar Storage**: Optimized for analytical queries
2. **Better Compression**: Reduced storage footprint
3. **Parallel Query Execution**: Faster aggregations
4. **SQL Analytics**: Window functions, CTEs, advanced aggregations
5. **Zero-Copy Integration**: Direct Pandas/Polars integration

### Schema Design

```sql
-- DuckDB schema with partitioning
CREATE TABLE IF NOT EXISTS pings (
  ts TIMESTAMP NOT NULL,
  target VARCHAR NOT NULL,
  latency_ms DOUBLE,
  success BOOLEAN,
  -- Additional columns for enhanced analytics
  ttl INTEGER,
  packet_size INTEGER,
  response_code INTEGER
) PARTITION BY (DATE_TRUNC('day', ts));

-- Create aggregated views for performance
CREATE VIEW hourly_stats AS
SELECT 
  DATE_TRUNC('hour', ts) as hour,
  target,
  COUNT(*) as ping_count,
  AVG(latency_ms) as avg_latency,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY latency_ms) as p50_latency,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_latency,
  SUM(CASE WHEN success THEN 1 ELSE 0 END)::DOUBLE / COUNT(*) * 100 as uptime_pct
FROM pings
GROUP BY DATE_TRUNC('hour', ts), target;
```

### DuckDB Implementation

```python
import duckdb
import pandas as pd
import polars as pl
from typing import Optional
import pyarrow as pa

class DuckDBStorage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._init_db()
        
    def _init_db(self):
        """Initialize DuckDB with optimized settings."""
        # Performance settings
        self.conn.execute("SET memory_limit='1GB'")
        self.conn.execute("SET threads=4")
        
        # Create schema
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS pings (
                ts TIMESTAMP NOT NULL,
                target VARCHAR NOT NULL,
                latency_ms DOUBLE,
                success BOOLEAN
            )
        """)
        
    def write_batch(self, df: pl.DataFrame):
        """Write batch using Arrow for zero-copy transfer."""
        arrow_table = df.to_arrow()
        self.conn.register("batch_data", arrow_table)
        self.conn.execute("""
            INSERT INTO pings 
            SELECT * FROM batch_data
        """)
        self.conn.unregister("batch_data")
    
    def query_analytics(self, query: str) -> pl.DataFrame:
        """Execute analytical query returning Polars DataFrame."""
        result = self.conn.execute(query).arrow()
        return pl.from_arrow(result)
```

### Migration Strategy

```python
class DatabaseMigrator:
    """Migrate from SQLite to DuckDB."""
    
    def __init__(self, sqlite_path: str, duckdb_path: str):
        self.sqlite_storage = SQLiteStorage(sqlite_path)
        self.duckdb_storage = DuckDBStorage(duckdb_path)
        
    def migrate(self, batch_size: int = 10000):
        """Migrate data in batches."""
        with self.sqlite_storage.connection() as conn:
            # Get total count
            count = conn.execute("SELECT COUNT(*) FROM pings").fetchone()[0]
            
            # Migrate in batches
            for offset in range(0, count, batch_size):
                logger.info(f"Migrating batch {offset}-{offset+batch_size}")
                
                # Read batch from SQLite
                df = pl.read_database(
                    f"""
                    SELECT ts, target, latency_ms, success 
                    FROM pings 
                    ORDER BY ts 
                    LIMIT {batch_size} OFFSET {offset}
                    """,
                    connection=conn
                )
                
                # Transform timestamp
                df = df.with_columns(
                    pl.col("ts").cast(pl.Datetime).alias("ts")
                )
                
                # Write to DuckDB
                self.duckdb_storage.write_batch(df)
        
        logger.info("Migration complete")
```

## Data Retention and Archival

### Retention Policies

```python
class RetentionManager:
    """Manage data retention and archival."""
    
    DEFAULT_POLICIES = {
        'raw_data': 30,        # 30 days of raw data
        'hourly_agg': 90,      # 90 days of hourly aggregates
        'daily_agg': 365,      # 1 year of daily aggregates
    }
    
    def __init__(self, storage: Union[SQLiteStorage, DuckDBStorage]):
        self.storage = storage
        
    async def apply_retention(self):
        """Apply retention policies."""
        cutoff_raw = time.time() - (self.DEFAULT_POLICIES['raw_data'] * 86400)
        
        # Archive old data before deletion
        await self.archive_old_data(cutoff_raw)
        
        # Delete old raw data
        if isinstance(self.storage, SQLiteStorage):
            with self.storage.connection() as conn:
                conn.execute("DELETE FROM pings WHERE ts < ?", (cutoff_raw,))
        else:
            self.storage.conn.execute(
                f"DELETE FROM pings WHERE ts < TIMESTAMP '{cutoff_raw}'"
            )
```

### Data Archival

```python
import gzip
import json

class DataArchiver:
    """Archive old data to compressed files."""
    
    def __init__(self, archive_dir: pathlib.Path):
        self.archive_dir = archive_dir
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
    def archive_batch(self, data: pl.DataFrame, timestamp: int):
        """Archive a batch of data."""
        filename = self.archive_dir / f"pings_{timestamp}.json.gz"
        
        # Convert to JSON and compress
        json_data = data.to_dicts()
        
        with gzip.open(filename, 'wt', encoding='utf-8') as f:
            json.dump(json_data, f)
        
        logger.info(f"Archived {len(data)} records to {filename}")
```

## Query Optimization

### Common Query Patterns

```python
class QueryOptimizer:
    """Optimized queries for common patterns."""
    
    @staticmethod
    def uptime_query(target: str, hours: int) -> str:
        """Generate uptime query."""
        if isinstance(storage, DuckDBStorage):
            return f"""
                SELECT 
                    target,
                    COUNT(*) as total_pings,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_pings,
                    (SUM(CASE WHEN success THEN 1 ELSE 0 END)::DOUBLE / COUNT(*)) * 100 as uptime_pct,
                    AVG(CASE WHEN success THEN latency_ms ELSE NULL END) as avg_latency,
                    PERCENTILE_CONT(0.95) WITHIN GROUP 
                        (ORDER BY CASE WHEN success THEN latency_ms ELSE NULL END) as p95_latency
                FROM pings
                WHERE target = '{target}'
                  AND ts > NOW() - INTERVAL '{hours} hours'
                GROUP BY target
            """
        else:
            # SQLite version
            cutoff = int(time.time()) - (hours * 3600)
            return f"""
                SELECT 
                    target,
                    COUNT(*) as total_pings,
                    SUM(success) as successful_pings,
                    (CAST(SUM(success) AS REAL) / COUNT(*)) * 100 as uptime_pct,
                    AVG(CASE WHEN success = 1 THEN latency_ms ELSE NULL END) as avg_latency
                FROM pings
                WHERE target = '{target}'
                  AND ts > {cutoff}
                GROUP BY target
            """
```

### Materialized Views (DuckDB)

```sql
-- Create materialized views for common queries
CREATE MATERIALIZED VIEW target_summary AS
SELECT 
    target,
    DATE_TRUNC('day', ts) as day,
    COUNT(*) as ping_count,
    AVG(latency_ms) as avg_latency,
    MIN(latency_ms) as min_latency,
    MAX(latency_ms) as max_latency,
    STDDEV(latency_ms) as stddev_latency,
    SUM(CASE WHEN success THEN 1 ELSE 0 END)::DOUBLE / COUNT(*) * 100 as uptime_pct
FROM pings
GROUP BY target, DATE_TRUNC('day', ts);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW target_summary;
```

## Performance Benchmarks

### Expected Performance

| Operation | SQLite | DuckDB |
|-----------|--------|--------|
| Single write | 0.1ms | 0.2ms |
| Batch write (1000) | 10ms | 5ms |
| Hour aggregation | 50ms | 10ms |
| Day aggregation | 200ms | 20ms |
| Week aggregation | 1000ms | 50ms |

### Storage Efficiency

| Metric | SQLite | DuckDB |
|--------|--------|--------|
| Row size | 40 bytes | 20 bytes |
| Compression | None | ~70% |
| 1M records | 40MB | 6MB |
| Index size | 20MB | 5MB |

## Testing Strategy

```python
import pytest
import tempfile

@pytest.fixture
def test_storage():
    """Create test storage instance."""
    with tempfile.NamedTemporaryFile() as f:
        storage = SQLiteStorage(f.name)
        yield storage

def test_write_performance(test_storage, benchmark):
    """Benchmark write performance."""
    def write_batch():
        batch = [
            (int(time.time()), f"192.168.1.{i}", 10.5, 1)
            for i in range(1000)
        ]
        with test_storage.connection() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO pings VALUES (?, ?, ?, ?)",
                batch
            )
    
    benchmark(write_batch)

def test_query_performance(test_storage, benchmark):
    """Benchmark query performance."""
    # Insert test data
    insert_test_data(test_storage, 100000)
    
    def query():
        with test_storage.connection() as conn:
            conn.execute("""
                SELECT target, AVG(latency_ms), COUNT(*)
                FROM pings
                WHERE ts > ?
                GROUP BY target
            """, (time.time() - 3600,)).fetchall()
    
    benchmark(query)
```

## Future Enhancements

1. **Distributed Storage**: MotherDuck integration for cloud backup
2. **Real-time Streaming**: Apache Arrow Flight for live data
3. **Advanced Analytics**: Machine learning models for anomaly detection
4. **Data Federation**: Query across multiple data sources
5. **Time-series Specific**: Integration with TimescaleDB or InfluxDB
6. **GraphQL API**: For flexible data queries
7. **Data Lineage**: Track data transformations and quality 