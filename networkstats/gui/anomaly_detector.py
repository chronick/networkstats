import polars as pl
import plotly.graph_objects as go

class AnomalyDetector:
    """Detect anomalies in network metrics using statistical methods."""
    def __init__(self, sensitivity: float = 2.5):
        self.sensitivity = sensitivity

    def detect_anomalies(self, df: pl.DataFrame) -> pl.DataFrame:
        window_size = 10  # Use a small window for test/demo
        df = df.with_columns([
            pl.col('latency_ms').rolling_mean(window_size).alias('rolling_mean'),
            pl.col('latency_ms').rolling_std(window_size).alias('rolling_std')
        ])
        df = df.with_columns([
            (
                (pl.col('latency_ms') > pl.col('rolling_mean') + self.sensitivity * pl.col('rolling_std')) |
                (pl.col('latency_ms') < pl.col('rolling_mean') - self.sensitivity * pl.col('rolling_std'))
            ).alias('is_anomaly')
        ])
        return df

    def create_anomaly_chart(self, df: pl.DataFrame) -> str:
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()
        # Ensure is_anomaly is boolean and fill NaN/None with False
        if 'is_anomaly' in df.columns:
            df['is_anomaly'] = df['is_anomaly'].fillna(False).infer_objects(copy=False).astype(bool)
        fig = go.Figure()
        # Normal points
        normal = df[~df['is_anomaly']]
        fig.add_trace(go.Scatter(
            x=normal['timestamp'],
            y=normal['latency_ms'],
            mode='markers',
            name='Normal',
            marker=dict(color='#007bff', size=4)
        ))
        # Anomaly points
        anomalies = df[df['is_anomaly']]
        fig.add_trace(go.Scatter(
            x=anomalies['timestamp'],
            y=anomalies['latency_ms'],
            mode='markers',
            name='Anomaly',
            marker=dict(color='#dc3545', size=8, symbol='x')
        ))
        # Add confidence bands
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['rolling_mean'] + self.sensitivity * df['rolling_std'],
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['rolling_mean'] - self.sensitivity * df['rolling_std'],
            fill='tonexty',
            fillcolor='rgba(0,123,255,0.2)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Normal range'
        ))
        return fig.to_html(include_plotlyjs='cdn') 