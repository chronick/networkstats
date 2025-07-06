import plotly.express as px
import polars as pl

class PacketLossChart:
    """Packet loss visualization by target, supporting bar, line, and area charts."""
    def __init__(self, data_source):
        self.data_source = data_source
        self.chart_type = 'bar'  # bar, line, area

    def create_chart(self, timeframe: int, targets: list[str] = None) -> str:
        """Generate packet loss chart HTML."""
        df = self.data_source.get_packet_loss_data(timeframe, targets)
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()
        if self.chart_type == 'bar':
            fig = px.bar(
                df,
                x='target',
                y='packet_loss_pct',
                title='Packet Loss by Target',
                labels={'packet_loss_pct': 'Packet Loss %'},
                color='packet_loss_pct',
                color_continuous_scale=['#28a745', '#ffc107', '#dc3545'],
                range_color=[0, 100]
            )
        elif self.chart_type == 'line':
            fig = px.line(
                df,
                x='datetime',
                y='packet_loss_pct',
                color='target',
                title='Packet Loss Over Time',
                labels={'packet_loss_pct': 'Packet Loss %', 'datetime': 'Time'},
                line_shape='spline'
            )
        elif self.chart_type == 'area':
            fig = px.area(
                df,
                x='datetime',
                y='packet_loss_pct',
                color='target',
                title='Packet Loss Area Chart',
                labels={'packet_loss_pct': 'Packet Loss %', 'datetime': 'Time'}
            )
        else:
            raise ValueError(f"Unknown chart type: {self.chart_type}")
        return fig.to_html(include_plotlyjs='cdn')

    @staticmethod
    def compute_packet_loss(df: pl.DataFrame) -> pl.DataFrame:
        """Compute packet loss percentage for each target."""
        result = df.group_by('target').agg(((1 - pl.col('success').mean()) * 100).alias('packet_loss_pct'))
        if hasattr(result, 'collect'):
            return result.collect()
        return result

    @staticmethod
    def compute_packet_loss_over_time(df: pl.DataFrame) -> pl.DataFrame:
        """Compute packet loss percentage for each target over time (e.g., by hour)."""
        result = df.group_by(['target', 'datetime']).agg(((1 - pl.col('success').mean()) * 100).alias('packet_loss_pct'))
        if hasattr(result, 'collect'):
            return result.collect()
        return result 