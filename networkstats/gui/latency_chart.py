import plotly.express as px
import polars as pl

class LatencyChart:
    """Latency visualization with percentiles, min/max, and trend analysis."""
    def __init__(self, data_source):
        self.data_source = data_source
        self.chart_type = 'box'  # box, line, area, etc.

    def create_chart(self, timeframe: int, targets: list[str] = None) -> str:
        """Generate latency chart HTML with percentiles and min/max."""
        df = self.data_source.get_latency_data(timeframe, targets)
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()
        if self.chart_type == 'box':
            fig = px.box(
                df,
                x='target',
                y='latency_ms',
                points='outliers',
                title='Latency Distribution by Target',
                labels={'latency_ms': 'Latency (ms)'},
                notched=True
            )
        elif self.chart_type == 'line':
            fig = px.line(
                df,
                x='datetime',
                y='latency_ms',
                color='target',
                title='Latency Over Time',
                labels={'latency_ms': 'Latency (ms)', 'datetime': 'Time'},
                line_shape='spline'
            )
        elif self.chart_type == 'area':
            fig = px.area(
                df,
                x='datetime',
                y='latency_ms',
                color='target',
                title='Latency Area Chart',
                labels={'latency_ms': 'Latency (ms)', 'datetime': 'Time'}
            )
        else:
            raise ValueError(f"Unknown chart type: {self.chart_type}")
        return fig.to_html(include_plotlyjs='cdn')

    @staticmethod
    def compute_percentiles(df, percentiles=[50, 90, 99]):
        """Compute latency percentiles for each target."""
        return df.groupby('target')['latency_ms'].quantile([p/100 for p in percentiles]).unstack()

    @staticmethod
    def compute_min_max(df):
        """Compute min and max latency for each target."""
        return df.groupby('target')['latency_ms'].agg(['min', 'max'])

    @staticmethod
    def compute_trend(current_df, previous_df):
        """Compare current and previous period median latency for trend analysis."""
        current = current_df.groupby('target')['latency_ms'].median()
        previous = previous_df.groupby('target')['latency_ms'].median()
        return (current - previous).to_dict() 