# Database Specification: Testing Strategy



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
