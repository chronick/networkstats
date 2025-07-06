# Database Specification: Performance Benchmarks



## Expected Performance

| Operation | SQLite | DuckDB |
|-----------|--------|--------|
| Single write | 0.1ms | 0.2ms |
| Batch write (1000) | 10ms | 5ms |
| Hour aggregation | 50ms | 10ms |
| Day aggregation | 200ms | 20ms |
| Week aggregation | 1000ms | 50ms |

## Storage Efficiency

| Metric | SQLite | DuckDB |
|--------|--------|--------|
| Row size | 40 bytes | 20 bytes |
| Compression | None | ~70% |
| 1M records | 40MB | 6MB |
| Index size | 20MB | 5MB |
