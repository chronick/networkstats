# Database Specification: Query Optimization



## Common Query Patterns

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

## Materialized Views (DuckDB)

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
