import plotly.express as px
import polars as pl
import numpy as np

class HeatmapView:
    """Heatmap visualization for patterns by hour and day."""
    def __init__(self, data_source):
        self.data_source = data_source

    def create_chart(self, timeframe: int, metric: str = 'uptime') -> str:
        """Generate heatmap showing patterns by hour and day."""
        df = self.data_source.get_hourly_data(timeframe)
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()
        # Pivot data for heatmap
        pivot = df.pivot(index='hour_of_day', columns='day_of_week', values=f'{metric}_pct')
        fig = px.imshow(
            pivot,
            labels=dict(x="Day of Week", y="Hour of Day", color=f"{metric.title()} %"),
            x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            y=[f"{h:02d}:00" for h in range(24)],
            color_continuous_scale='RdYlGn',
            aspect='auto',
            title=f'{metric.title()} Patterns by Hour and Day'
        )
        return fig.to_html(include_plotlyjs='cdn') 