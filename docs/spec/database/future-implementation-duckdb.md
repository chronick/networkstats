# Database Specification: Future Implementation: DuckDB



## Why DuckDB?

**Columnar Storage**: Optimized for analytical queries

**Better Compression**: Reduced storage footprint

**Parallel Query Execution**: Faster aggregations

**SQL Analytics**: Window functions, CTEs, advanced aggregations

**Zero-Copy Integration**: Direct Pandas/Polars integration

## Schema Design

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

## DuckDB Implementation

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

## Migration Strategy

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
