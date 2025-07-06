import plotly.graph_objects as go
import polars as pl

class TimelineView:
    """Timeline visualization showing up/down events and status history."""
    def __init__(self, data_source):
        self.data_source = data_source

    def create_chart(self, timeframe: int, targets: list[str] = None) -> str:
        """Generate timeline chart showing up/down events."""
        events = self.data_source.get_events(timeframe, targets)
        if isinstance(events, pl.DataFrame):
            events = events.to_pandas()
        fig = go.Figure()
        unique_targets = events['target'].unique()
        for i, target in enumerate(unique_targets):
            target_events = events[events['target'] == target]
            for _, row in target_events.iterrows():
                color = '#28a745' if row['status'] == 'up' else '#dc3545'
                fig.add_trace(go.Scatter(
                    x=[row['start_time'], row['end_time']],
                    y=[i, i],
                    mode='lines',
                    line=dict(color=color, width=20),
                    showlegend=False,
                    hovertemplate=f"{target}<br>Status: {row['status']}<br>Duration: {row['duration_min']} min<br><extra></extra>"
                ))
        fig.update_layout(
            title='Network Status Timeline',
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(unique_targets))),
                ticktext=unique_targets
            ),
            xaxis_title='Time',
            height=300
        )
        return fig.to_html(include_plotlyjs='cdn') 