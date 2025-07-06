# Database Specification: Data Retention and Archival



## Retention Policies

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

## Data Archival

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
