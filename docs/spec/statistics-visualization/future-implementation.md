# Statistics and Visualization Specification: Future Implementation



## Enhanced Dashboard Layout

┌─────────────────────────────────────────────────────────────┐
│ Network Statistics Dashboard                    [─][□][X]   │
├─────────────────────────────────────────────────────────────┤
│ Time Range: [Last 24 hours ▼] Auto-refresh: [✓] [Export]    │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌─────────────────────┐            │
│ │ Overall Uptime      │ │ Current Status       │            │
│ │   99.87%           │ │ ✅ All Systems OK    │            │
│ │ ████████████████░  │ │ 2/2 targets online   │            │
│ └─────────────────────┘ └─────────────────────┘            │
│                                                              │
│ ┌─────────────────────┐ ┌─────────────────────┐            │
│ │ Avg Latency         │ │ Packet Loss          │            │
│ │   15.3 ms          │ │   0.02%             │            │
│ │ ↓ 2.1ms from hour  │ │ ━━━━━━━━━━━━━━━━━   │            │
│ └─────────────────────┘ └─────────────────────┘            │
├─────────────────────────────────────────────────────────────┤
│ [Uptime] [Latency] [Timeline] [Heatmap] [Compare]          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Interactive Chart Area]                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

```
┌─────────────────────────────────────────────────────────────┐
│ Network Statistics Dashboard                    [─][□][X]   │
├─────────────────────────────────────────────────────────────┤
│ Time Range: [Last 24 hours ▼] Auto-refresh: [✓] [Export]    │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌─────────────────────┐            │
│ │ Overall Uptime      │ │ Current Status       │            │
│ │   99.87%           │ │ ✅ All Systems OK    │            │
│ │ ████████████████░  │ │ 2/2 targets online   │            │
│ └─────────────────────┘ └─────────────────────┘            │
│                                                              │
│ ┌─────────────────────┐ ┌─────────────────────┐            │
│ │ Avg Latency         │ │ Packet Loss          │            │
│ │   15.3 ms          │ │   0.02%             │            │
│ │ ↓ 2.1ms from hour  │ │ ━━━━━━━━━━━━━━━━━   │            │
│ └─────────────────────┘ └─────────────────────┘            │
├─────────────────────────────────────────────────────────────┤
│ [Uptime] [Latency] [Timeline] [Heatmap] [Compare]          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Interactive Chart Area]                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

```

## Core Components

### 1. Summary Cards

```python
class SummaryCard:
    """Reusable summary statistic card."""
    
    def __init__(self, title: str, metric_type: str):
        self.title = title
        self.metric_type = metric_type
        self.current_value = None
        self.previous_value = None
        
    def create_widget(self) -> toga.Box:
        """Create the card widget."""
        card = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10,
            background_color='#f8f9fa',
            width=200,
            height=100
        ))
        
        # Title
        title_label = toga.Label(
            self.title,
            style=Pack(font_size=12, color='#6c757d')
        )
        
        # Main value
        self.value_label = toga.Label(
            self.format_value(self.current_value),
            style=Pack(font_size=24, font_weight='bold')
        )
        
        # Trend indicator
        self.trend_label = toga.Label(
            self.format_trend(),
            style=Pack(font_size=10)
        )
        
        # Progress bar for percentage metrics
        if self.metric_type == 'percentage':
            self.progress = toga.ProgressBar(
                max=100,
                value=self.current_value or 0,
                style=Pack(width=180, height=10)
            )
            card.add(self.progress)
        
        card.add(title_label)
        card.add(self.value_label)
        card.add(self.trend_label)
        
        return card
    
    def update(self, current: float, previous: float = None):
        """Update card values."""
        self.current_value = current
        self.previous_value = previous
        
        self.value_label.text = self.format_value(current)
        self.trend_label.text = self.format_trend()
        
        if hasattr(self, 'progress'):
            self.progress.value = current

```

### 2. Chart Types

#### Uptime Chart

```python
class UptimeChart:
    """Uptime visualization with multiple views."""
    
    def __init__(self, data_source):
        self.data_source = data_source
        self.chart_type = 'bar'  # bar, line, area
        
    def create_chart(self, timeframe: int, targets: list[str] = None) -> str:
        """Generate uptime chart HTML."""
        df = self.data_source.get_uptime_data(timeframe, targets)
        
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
            
            # Add threshold line
            fig.add_hline(
                y=99.9,
                line_dash="dash",
                annotation_text="99.9% SLA",
                annotation_position="bottom right"
            )
            
        elif self.chart_type == 'line':
            # Time series uptime
            fig = px.line(
                df,
                x='hour',
                y='uptime_pct',
                color='target',
                title='Uptime Over Time',
                labels={'uptime_pct': 'Uptime %', 'hour': 'Time'},
                line_shape='spline'
            )
            
        return fig.to_html(include_plotlyjs='cdn')

```

#### Latency Chart
```python
class LatencyChart:
    """Latency visualization with percentiles."""
    
    def create_chart(self, timeframe: int, targets: list[str] = None) -> str:
        """Generate latency chart with percentiles."""
        df = self.data_source.get_latency_data(timeframe, targets)
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add average latency line
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['avg_latency'],
                name='Average',
                line=dict(color='#007bff', width=2)
            ),
            secondary_y=False
        )
        
        # Add percentile bands
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['p95_latency'],
                name='95th percentile',
                line=dict(color='#ffc107', dash='dash')
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['p99_latency'],
                name='99th percentile',
                line=dict(color='#dc3545', dash='dot')
            ),
            secondary_y=False
        )
        
        # Add min/max range
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'].to_list() + df['timestamp'].to_list()[::-1],
                y=df['min_latency'].to_list() + df['max_latency'].to_list()[::-1],
                fill='toself',
                fillcolor='rgba(0,123,255,0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name='Range'
            ),
            secondary_y=False
        )
        
        # Update layout
        fig.update_layout(
            title='Latency Analysis',
            xaxis_title='Time',
            yaxis_title='Latency (ms)',
            hovermode='x unified',
            height=400
        )
        
        return fig.to_html(include_plotlyjs='cdn')

```

#### Timeline View

```python
class TimelineView:
    """Timeline visualization showing events."""
    
    def create_chart(self, timeframe: int, targets: list[str] = None) -> str:
        """Generate timeline chart showing up/down events."""
        events = self.data_source.get_events(timeframe, targets)
        
        fig = go.Figure()
        
        # Create timeline for each target
        for i, target in enumerate(events['target'].unique()):
            target_events = events.filter(pl.col('target') == target)
            
            # Add colored segments for up/down periods
            for _, row in target_events.iter_rows(named=True):
                color = '#28a745' if row['status'] == 'up' else '#dc3545'
                
                fig.add_trace(go.Scatter(
                    x=[row['start_time'], row['end_time']],
                    y=[i, i],
                    mode='lines',
                    line=dict(color=color, width=20),
                    showlegend=False,
                    hovertemplate=f"{target}<br>Status: {row['status']}<br>"
                                  f"Duration: {row['duration_min']} min<br>"
                                  f"<extra></extra>"
                ))
        
        # Update layout
        fig.update_layout(
            title='Network Status Timeline',
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(events['target'].unique()))),
                ticktext=events['target'].unique()
            ),
            xaxis_title='Time',
            height=300
        )
        
        return fig.to_html(include_plotlyjs='cdn')

```

#### Heatmap View
```python
class HeatmapView:
    """Heatmap visualization for patterns."""
    
    def create_chart(self, timeframe: int, metric: str = 'uptime') -> str:
        """Generate heatmap showing patterns by hour and day."""
        df = self.data_source.get_hourly_data(timeframe)
        
        # Pivot data for heatmap
        pivot = df.pivot(
            index='hour_of_day',
            columns='day_of_week',
            values=f'{metric}_pct'
        )
        
        fig = px.imshow(
            pivot,
            labels=dict(x="Day of Week", y="Hour of Day", color=f"{metric} %"),
            x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            y=[f"{h:02d}:00" for h in range(24)],
            color_continuous_scale='RdYlGn',
            aspect='auto',
            title=f'{metric.title()} Patterns by Hour and Day'
        )
        
        return fig.to_html(include_plotlyjs='cdn')

```

## 3. Interactive Features

### Drill-Down Analysis

```python
class DrillDownHandler:
    """Handle drill-down interactions."""
    
    def __init__(self, stats_window):
        self.stats_window = stats_window
        
    def on_chart_click(self, event_data: dict):
        """Handle click events on charts."""
        point_data = event_data.get('points', [{}])[0]
        
        if 'customdata' in point_data:
            target = point_data['customdata']['target']
            timestamp = point_data['customdata']['timestamp']
            
            # Show detail window
            self.show_detail_window(target, timestamp)
    
    def show_detail_window(self, target: str, timestamp: float):
        """Show detailed view for specific point."""
        detail_window = toga.Window(title=f"Details: {target}")
        
        # Get surrounding data
        detail_data = self.data_source.get_detail_data(
            target, 
            timestamp - 3600,  # 1 hour before
            timestamp + 3600   # 1 hour after
        )
        
        # Create detail chart
        chart = self.create_detail_chart(detail_data)
        
        # Add to window
        web_view = toga.WebView()
        web_view.set_content(chart, 'text/html')
        
        detail_window.content = web_view
        detail_window.show()

```

### Real-time Updates


```python
class RealtimeUpdater:
    """Handle real-time chart updates."""
    
    def __init__(self, chart_container: toga.WebView):
        self.chart_container = chart_container
        self.update_interval = 5  # seconds
        self.is_running = False
        
    async def start_updates(self):
        """Start real-time updates."""
        self.is_running = True
        
        while self.is_running:
            # Get latest data
            latest_data = await self.data_source.get_latest_data()
            
            # Update chart via JavaScript
            update_script = f"""
                Plotly.extendTraces('chart', {{
                    x: [[{latest_data['timestamps']}]],
                    y: [[{latest_data['values']}]]
                }}, [0]);
                
                // Keep only last N points
                Plotly.relayout('chart', {{
                    'xaxis.range': [
                        new Date(Date.now() - 3600000),
                        new Date()
                    ]
                }});
            """
            
            await self.chart_container.evaluate_javascript(update_script)
            await asyncio.sleep(self.update_interval)

```

## 4. Export Functionality


```python
class ExportManager:
    """Handle data and chart exports."""
    
    EXPORT_FORMATS = ['PDF', 'PNG', 'CSV', 'Excel', 'JSON']
    
    def __init__(self, data_source):
        self.data_source = data_source
        
    async def export_data(self, format: str, timeframe: int, options: dict):
        """Export data in specified format."""
        # Get data
        df = self.data_source.get_export_data(timeframe, options)
        
        if format == 'CSV':
            return self._export_csv(df)
        elif format == 'Excel':
            return self._export_excel(df)
        elif format == 'JSON':
            return self._export_json(df)
        elif format in ['PDF', 'PNG']:
            return await self._export_chart(df, format)
    
    def _export_excel(self, df: pl.DataFrame) -> bytes:
        """Export to Excel with formatting."""
        import xlsxwriter
        from io import BytesIO
        
        output = BytesIO()
        
        with xlsxwriter.Workbook(output) as workbook:
            # Summary sheet
            summary_sheet = workbook.add_worksheet('Summary')
            self._write_summary(summary_sheet, df, workbook)
            
            # Raw data sheet
            data_sheet = workbook.add_worksheet('Raw Data')
            self._write_raw_data(data_sheet, df, workbook)
            
            # Charts sheet
            charts_sheet = workbook.add_worksheet('Charts')
            self._create_excel_charts(charts_sheet, df, workbook)
        
        return output.getvalue()
    
    async def _export_chart(self, df: pl.DataFrame, format: str) -> bytes:
        """Export chart as image or PDF."""
        # Create comprehensive report
        report = ReportGenerator(df)
        
        if format == 'PDF':
            return await report.generate_pdf()
        else:  # PNG
            return await report.generate_image()

```

## 5. Advanced Analytics

### Anomaly Detection
```python
class AnomalyDetector:
    """Detect anomalies in network metrics."""
    
    def __init__(self, sensitivity: float = 2.5):
        self.sensitivity = sensitivity
        
    def detect_anomalies(self, df: pl.DataFrame) -> pl.DataFrame:
        """Detect anomalies using statistical methods."""
        # Calculate rolling statistics
        window_size = 60  # 1 hour for minute-level data
        
        df = df.with_columns([
            pl.col('latency_ms').rolling_mean(window_size).alias('rolling_mean'),
            pl.col('latency_ms').rolling_std(window_size).alias('rolling_std')
        ])
        
        # Mark anomalies (values outside N standard deviations)
        df = df.with_columns([
            (
                (pl.col('latency_ms') > 
                 pl.col('rolling_mean') + self.sensitivity * pl.col('rolling_std')) |
                (pl.col('latency_ms') < 
                 pl.col('rolling_mean') - self.sensitivity * pl.col('rolling_std'))
            ).alias('is_anomaly')
        ])
        
        return df
    
    def create_anomaly_chart(self, df: pl.DataFrame) -> str:
        """Create chart highlighting anomalies."""
        fig = go.Figure()
        
        # Normal points
        normal = df.filter(~pl.col('is_anomaly'))
        fig.add_trace(go.Scatter(
            x=normal['timestamp'],
            y=normal['latency_ms'],
            mode='markers',
            name='Normal',
            marker=dict(color='#007bff', size=4)
        ))
        
        # Anomaly points
        anomalies = df.filter(pl.col('is_anomaly'))
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
        
        return fig.to_html()

```

### Predictive Analytics
```python
class PredictiveAnalytics:
    """Predict future network behavior."""
    
    def predict_downtime_risk(self, historical_data: pl.DataFrame) -> dict:
        """Predict risk of downtime in next period."""
        # Simple time-series based prediction
        recent_uptime = historical_data.tail(24).select(
            pl.col('uptime_pct').mean()
        ).item()
        
        # Calculate trend
        hourly_uptime = historical_data.group_by_dynamic(
            'timestamp', every='1h'
        ).agg(
            pl.col('success').mean().alias('hourly_uptime')
        )
        
        trend = self._calculate_trend(hourly_uptime)
        
        # Risk scoring
        risk_score = 0
        if recent_uptime < 99.9:
            risk_score += 30
        if trend < -0.1:  # Declining trend
            risk_score += 40
        
        return {
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'predicted_uptime': max(0, min(100, recent_uptime + trend * 24)),
            'confidence': 0.75  # Simplified confidence score
        }

```
