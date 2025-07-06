# Statistics and Visualization Specification: Performance Optimization
## Data Aggregation
```python
class DataAggregator:
    """Efficient data aggregation for large datasets."""
    
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}
        
    async def get_aggregated_data(
        self, 
        timeframe: int, 
        resolution: str = 'auto'
    ) -> pl.DataFrame:
        """Get aggregated data with appropriate resolution."""
        cache_key = f"{timeframe}_{resolution}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Determine resolution
        if resolution == 'auto':
            resolution = self._determine_resolution(timeframe)
        
        # Query with aggregation
        if resolution == 'minute':
            df = await self.storage.query_raw(timeframe)
        elif resolution == 'hour':
            df = await self.storage.query_hourly_aggregates(timeframe)
        elif resolution == 'day':
            df = await self.storage.query_daily_aggregates(timeframe)
        
        # Cache result
        self.cache[cache_key] = df
        
        return df
    
    def _determine_resolution(self, timeframe: int) -> str:
        """Determine appropriate data resolution."""
        if timeframe <= 3600:  # 1 hour
            return 'minute'
        elif timeframe <= 86400 * 7:  # 1 week
            return 'hour'
        else:
            return 'day'

```

## Lazy Loading
```python
class LazyChartLoader:
    """Load charts on-demand for better performance."""
    
    def __init__(self, container: toga.Box):
        self.container = container
        self.charts = {}
        self.loaded_charts = set()
        
    def register_chart(self, chart_id: str, chart_factory):
        """Register a chart for lazy loading."""
        self.charts[chart_id] = chart_factory
        
        # Add placeholder
        placeholder = toga.Box(
            style=Pack(height=400, background_color='#f8f9fa')
        )
        placeholder.id = f"placeholder_{chart_id}"
        
        self.container.add(placeholder)
    
    async def load_chart(self, chart_id: str):
        """Load a specific chart."""
        if chart_id in self.loaded_charts:
            return
            
        # Get chart factory
        chart_factory = self.charts.get(chart_id)
        if not chart_factory:
            return
        
        # Generate chart
        chart_html = await chart_factory()
        
        # Replace placeholder
        web_view = toga.WebView()
        web_view.set_content(chart_html, 'text/html')
        
        # Find and replace placeholder
        placeholder_id = f"placeholder_{chart_id}"
        for i, child in enumerate(self.container.children):
            if hasattr(child, 'id') and child.id == placeholder_id:
                self.container.remove(child)
                self.container.insert(i, web_view)
                break
        
        self.loaded_charts.add(chart_id)

```
