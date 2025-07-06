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

class StatsWindow(toga.App):
    def __init__(self):
        super().__init__('Network Stats', 'com.networkstats.stats')

    def startup(self):
        self.main_window = toga.MainWindow(title="Network Stats")
        self.timeframe = toga.Selection(
            items=[
                ("Last hour", 3600),
                ("24 hours", 86400),
                ("7 days", 604800),
            ],
            style=Pack(width=150, margin_right=10)
        )
        self.timeframe.on_change = self.refresh
        self.chart_type = toga.Selection(
            items=["Uptime", "Latency", "Timeline", "Heatmap", "Anomaly"],
            style=Pack(width=120, margin_right=10)
        )
        self.chart_type.on_change = self.refresh
        self.export_btn = toga.Button("Export", on_press=self.export_data, style=Pack(width=80, margin_left=10))
        self.web = toga.WebView(style=Pack(flex=1, height=400))
        # Summary cards
        self.uptime_card = SummaryCard("Uptime", "percentage")
        self.latency_card = SummaryCard("Latency", "ms")
        self.cards_box = toga.Box(children=[self.uptime_card.create_widget(), self.latency_card.create_widget()], style=Pack(direction=ROW, padding=10))
        # Controls
        controls = toga.Box(children=[self.timeframe, self.chart_type, self.export_btn], style=Pack(direction=ROW, padding=10))
        # Main layout
        box = toga.Box(children=[controls, self.cards_box, self.web], style=Pack(direction=COLUMN))
        self.main_window.content = box
        self.refresh(None)
        self.main_window.show()
        # Real-time updater
        self.realtime_updater = RealtimeUpdater(self.web)
        # Drilldown handler
        self.drilldown_handler = DrillDownHandler(self)

    def refresh(self, widget):
        span = self.timeframe.value or 3600
        chart_type = self.chart_type.value or "Uptime"
        df: pl.DataFrame = fetch_dataframe(span)
        if df.is_empty():
            html = "<h3>No data yet…</h3>"
            self.uptime_card.update(None)
            self.latency_card.update(None)
        else:
            # Update summary cards
            uptime = (
                df.groupby("target")
                .agg(pl.col("success").mean() * 100)
                .rename({"success": "uptime_pct"})
            )
            avg_uptime = float(uptime["uptime_pct"].mean()) if uptime.height > 0 else None
            avg_latency = float(df["latency_ms"].mean()) if "latency_ms" in df.columns else None
            self.uptime_card.update(avg_uptime)
            self.latency_card.update(avg_latency)
            # Chart selection
            if chart_type == "Uptime":
                chart = UptimeChart(lambda tf, t: uptime)
                chart.chart_type = 'bar'
                html = chart.create_chart(span)
            elif chart_type == "Latency":
                chart = LatencyChart(lambda tf, t: df)
                chart.chart_type = 'box'
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
            else:
                html = "<h3>Unknown chart type</h3>"
        self.web.set_content(html, "text/html")

    def export_data(self, widget):
        # Example: Export as CSV (expand as needed)
        pass

    def show_detail_window(self, target, timestamp):
        # Example: Show a detail window for drilldown
        win = toga.Window(title=f"Details: {target}")
        win.content = toga.Label(f"Details for {target} at {timestamp}")
        win.show() 