import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import polars as pl
from ..storage import fetch_dataframe
from .uptime_chart import UptimeChart
from .latency_chart import LatencyChart
from .timeline_view import TimelineView
from .heatmap_view import HeatmapView
from .anomaly_detector import AnomalyDetector
from .export_manager import ExportManager
from .realtime_updater import RealtimeUpdater
from .drilldown_handler import DrillDownHandler
from .summary_card import SummaryCard
from .packet_loss_chart import PacketLossChart

class StatsWindow(toga.App):
    def __init__(self):
        super().__init__('Network Stats', 'com.networkstats.stats')

    def startup(self):
        self.main_window = toga.MainWindow(title="Network Stats")
        self.timeframe_items = [
            ("Last hour", 3600),
            ("24 hours", 86400),
            ("7 days", 604800),
        ]
        self.timeframe = toga.Selection(
            items=[label for label, _ in self.timeframe_items],
            style=Pack(width=150, margin_right=10)
        )
        self.timeframe.on_change = self.refresh
        self.chart_type = toga.Selection(
            items=["Uptime", "Latency", "Timeline", "Heatmap", "Anomaly", "Packet Loss", "Combined"],
            style=Pack(width=120, margin_right=10)
        )
        self.chart_type.on_change = self.on_chart_type_change
        # Chart subtype selector (contextual)
        self.chart_subtype = toga.Selection(
            items=["bar", "line", "area", "box"],
            style=Pack(width=100, margin_right=10)
        )
        self.chart_subtype.on_change = self.refresh
        # Metric selector for new chart types (e.g., for Combined)
        self.metric_selector = toga.Selection(
            items=["Uptime", "Latency", "Packet Loss"],
            style=Pack(width=120, margin_right=10)
        )
        self.metric_selector.on_change = self.refresh
        # Target filter
        self.target_filter = toga.TextInput(placeholder="Filter by target (optional)", style=Pack(width=180, margin_right=10))
        self.target_filter.on_change = self.refresh
        self.export_btn = toga.Button("Export", on_press=self.export_data, style=Pack(width=80, margin_left=10))
        self.web = toga.WebView(style=Pack(flex=1, height=400))
        # Summary cards
        self.uptime_card = SummaryCard("Uptime", "percentage")
        self.latency_card = SummaryCard("Latency", "ms")
        self.cards_box = toga.Box(children=[self.uptime_card.create_widget(), self.latency_card.create_widget()], style=Pack(direction=ROW, padding=10))
        # Controls
        controls = toga.Box(children=[self.timeframe, self.chart_type, self.chart_subtype, self.metric_selector, self.target_filter, self.export_btn], style=Pack(direction=ROW, padding=10))
        # Main layout
        box = toga.Box(children=[controls, self.cards_box, self.web], style=Pack(direction=COLUMN))
        self.main_window.content = box
        self.refresh(None)
        self.main_window.show()
        # Real-time updater
        self.realtime_updater = RealtimeUpdater(self.web)
        # Drilldown handler
        self.drilldown_handler = DrillDownHandler(self)
        self.web.on_navigate = self.on_web_navigate

    def on_chart_type_change(self, widget):
        chart_type = self.chart_type.value or "Uptime"
        # Update subtype options based on chart type
        if chart_type == "Uptime":
            self.chart_subtype.items = ["bar", "line", "area"]
            self.chart_subtype.value = "bar"
        elif chart_type == "Latency":
            self.chart_subtype.items = ["box", "line", "area"]
            self.chart_subtype.value = "box"
        elif chart_type == "Timeline":
            self.chart_subtype.items = []
            self.chart_subtype.value = None
        elif chart_type == "Heatmap":
            self.chart_subtype.items = []
            self.chart_subtype.value = None
        elif chart_type == "Anomaly":
            self.chart_subtype.items = []
            self.chart_subtype.value = None
        elif chart_type == "Packet Loss":
            self.chart_subtype.items = ["bar", "line", "area"]
            self.chart_subtype.value = "bar"
        elif chart_type == "Combined":
            self.chart_subtype.items = ["line", "area"]
            self.chart_subtype.value = "line"
        else:
            self.chart_subtype.items = []
            self.chart_subtype.value = None
        self.refresh(None)

    def refresh(self, widget):
        label = self.timeframe.value or "Last hour"
        span = dict(self.timeframe_items).get(label, 3600)
        chart_type = self.chart_type.value or "Uptime"
        subtype = self.chart_subtype.value if hasattr(self.chart_subtype, 'value') else None
        metric = self.metric_selector.value if hasattr(self.metric_selector, 'value') else None
        target_filter = self.target_filter.value.strip() if hasattr(self.target_filter, 'value') and self.target_filter.value else None
        df: pl.DataFrame = fetch_dataframe(span)
        if target_filter:
            df = df.filter(pl.col("target").str.contains(target_filter, case=False))
        if df.is_empty():
            html = "<h3>No data yet…</h3>"
            self.uptime_card.update(None)
            self.latency_card.update(None)
        else:
            # Update summary cards
            uptime = (
                df.group_by("target")
                .agg(pl.col("success").mean() * 100)
                .rename({"success": "uptime_pct"})
            )
            avg_uptime = float(uptime["uptime_pct"].mean()) if uptime.height > 0 else None
            avg_latency = float(df["latency_ms"].mean()) if "latency_ms" in df.columns else None
            self.uptime_card.update(avg_uptime)
            self.latency_card.update(avg_latency)
            # Chart selection
            if chart_type == "Uptime":
                class DummySource:
                    def get_uptime_data(self, tf, t):
                        return uptime
                chart = UptimeChart(DummySource())
                chart.chart_type = subtype or 'bar'
                html = chart.create_chart(span)
            elif chart_type == "Latency":
                chart = LatencyChart(lambda tf, t: df)
                chart.chart_type = subtype or 'box'
                html = chart.create_chart(span)
            elif chart_type == "Timeline":
                class DummySource:
                    def get_events(self, tf, t):
                        return df
                chart = TimelineView(DummySource())
                html = chart.create_chart(span)
            elif chart_type == "Heatmap":
                class DummySource:
                    def get_hourly_data(self, tf):
                        return df
                chart = HeatmapView(DummySource())
                html = chart.create_chart(span)
            elif chart_type == "Anomaly":
                detector = AnomalyDetector()
                result = detector.detect_anomalies(df)
                html = detector.create_anomaly_chart(result)
            elif chart_type == "Packet Loss":
                # Compute packet loss per target
                packet_loss_df = PacketLossChart.compute_packet_loss(df)
                class DummySource:
                    def get_packet_loss_data(self, tf, t):
                        return packet_loss_df
                chart = PacketLossChart(DummySource())
                chart.chart_type = subtype or 'bar'
                html = chart.create_chart(span)
            elif chart_type == "Combined":
                # Placeholder for combined metrics chart
                html = "<h3>Combined metrics chart coming soon…</h3>"
            else:
                html = "<h3>Unknown chart type</h3>"
        self.web.set_content(html, "text/html")
        # Inject Plotly click event handler for drilldown
        js = """
        if (window.Plotly && document.querySelector('.js-plotly-plot')) {
            document.querySelector('.js-plotly-plot').on('plotly_click', function(data) {
                var pt = data.points[0];
                var target = pt.customdata && pt.customdata.target ? pt.customdata.target : (pt.x || pt.label || '');
                var timestamp = pt.customdata && pt.customdata.timestamp ? pt.customdata.timestamp : (pt.x || '');
                var url = 'drilldown://' + encodeURIComponent(target) + '/' + encodeURIComponent(timestamp);
                window.location.href = url;
            });
        }
        """
        self.web.evaluate_javascript(js)

    def export_data(self, widget):
        # Example: Export as CSV (expand as needed)
        pass

    def show_detail_window(self, target, timestamp):
        # Example: Show a detail window for drilldown
        win = toga.Window(title=f"Details: {target}")
        win.content = toga.Label(f"Details for {target} at {timestamp}")
        win.show()

    def on_web_navigate(self, widget, url):
        if url.startswith('drilldown://'):
            try:
                _, rest = url.split('://', 1)
                target, timestamp = rest.split('/', 1)
                target = target and target != 'undefined' and target or None
                timestamp = timestamp and timestamp != 'undefined' and timestamp or None
                self.drilldown_handler.on_chart_click({'points': [{'customdata': {'target': target, 'timestamp': timestamp}}]})
            except Exception as e:
                print(f"Drilldown parse error: {e}")
            return True  # Prevent navigation
        return False 