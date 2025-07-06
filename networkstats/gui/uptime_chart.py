import plotly.express as px
import polars as pl

class UptimeChart:
    """Uptime visualization with multiple views (bar, line, area)."""
    def __init__(self, data_source):
        self.data_source = data_source
        self.chart_type = 'bar'  # bar, line, area

    def create_chart(self, timeframe: int, targets: list[str] = None) -> str:
        """Generate uptime chart HTML."""
        df = self.data_source.get_uptime_data(timeframe, targets)
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()
        if self.chart_type == 'bar':
            fig = px.bar(
                df,
                x='target',
                y='uptime_pct',
                title='Uptime by Target',
                labels={'uptime_pct': 'Uptime %'},
                color='uptime_pct',
                color_continuous_scale=['#dc3545', '#ffc107', '#28a745'],
                range_color=[95, 100]
            )
            fig.add_hline(
                y=99.9,
                line_dash="dash",
                annotation_text="99.9% SLA",
                annotation_position="bottom right"
            )
        elif self.chart_type == 'line':
            fig = px.line(
                df,
                x='hour',
                y='uptime_pct',
                color='target',
                title='Uptime Over Time',
                labels={'uptime_pct': 'Uptime %', 'hour': 'Time'},
                line_shape='spline'
            )
        elif self.chart_type == 'area':
            fig = px.area(
                df,
                x='hour',
                y='uptime_pct',
                color='target',
                title='Uptime Area Chart',
                labels={'uptime_pct': 'Uptime %', 'hour': 'Time'}
            )
        else:
            raise ValueError(f"Unknown chart type: {self.chart_type}")
        return fig.to_html(include_plotlyjs='cdn') 