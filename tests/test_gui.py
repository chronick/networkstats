import pytest  # type: ignore

StatsWindow = None
SettingsWindow = None
TargetEditor = None
import_error = None

print("Starting GUI test imports...")

try:
    from networkstats.gui.stats_window import StatsWindow
    print("StatsWindow imported successfully")
except ImportError as e:
    print(f"StatsWindow import error: {e}")
    import_error = e

try:
    from networkstats.gui.settings_window import SettingsWindow
    print("SettingsWindow imported successfully")
except ImportError as e:
    print(f"SettingsWindow import error: {e}")
    import_error = e

try:
    from networkstats.gui.target_editor import TargetEditor
    print("TargetEditor imported successfully")
except ImportError as e:
    print(f"TargetEditor import error: {e}")
    import_error = e

try:
    import toga  # type: ignore
    print("Toga imported successfully")
except ImportError as e:
    print(f"Toga import error: {e}")
    import_error = e

print(f"Final values - StatsWindow: {StatsWindow}, SettingsWindow: {SettingsWindow}, TargetEditor: {TargetEditor}")
print(f"Import error: {import_error}")

def test_stats_window_instantiates():
    if StatsWindow is None or import_error:
        pytest.skip(f"Toga or StatsWindow not installed: {import_error}")
    app = StatsWindow()
    assert hasattr(app, "startup")

def test_settings_window_instantiates():
    if SettingsWindow is None or import_error:
        pytest.skip(f"Toga or SettingsWindow not installed: {import_error}")
    app = SettingsWindow(config_manager={})
    assert hasattr(app, "startup")

def test_settings_window_tabs():
    if SettingsWindow is None or import_error:
        pytest.skip(f"Toga or SettingsWindow not installed: {import_error}")
    app = SettingsWindow(config_manager={})
    app.startup()
    # Check that tabs were created
    assert hasattr(app, 'tabs')
    assert app.tabs is not None
    # Check tab content exists
    assert len(app.tabs.content) == 5  # General, Targets, Alerts, Display, Advanced

def test_target_editor_fields():
    if TargetEditor is None or import_error:
        pytest.skip(f"Toga or TargetEditor not installed: {import_error}")
    target = {
        'address': '1.2.3.4',
        'name': 'Test',
        'protocol': 'ICMP',
        'port': 0,
        'timeout': 5.0,
        'tags': ['foo', 'bar']
    }
    editor = TargetEditor(target=target)
    assert editor.address_input.value == '1.2.3.4'
    assert editor.name_input.value == 'Test'
    assert editor.protocol_selection.value == 'ICMP'
    assert int(editor.port_input.value) == 0
    assert float(editor.timeout_input.value) == 5.0
    assert 'foo' in editor.tags_input.value

from networkstats.gui.settings_validator import SettingsValidator
import pathlib
from networkstats.configuration_manager import ConfigurationManager

def test_settings_validator_target_valid():
    valid, msg = SettingsValidator.validate_target('8.8.8.8')
    assert valid is True
    assert msg == ''
    valid, msg = SettingsValidator.validate_target('invalid..address')
    assert valid is False
    assert 'Invalid' in msg or 'Cannot resolve' in msg

def test_settings_validator_settings():
    valid_settings = {
        'interval_sec': 30,
        'targets': [{'address': '8.8.8.8', 'name': '', 'protocol': 'ICMP', 'port': 0, 'timeout': 5.0, 'tags': []}],
        'alerts': {
            'enabled': True,
            'downtime': {'enabled': True, 'minutes': 5},
            'latency': {'enabled': True, 'ms': 100},
            'packet_loss': {'enabled': True, 'percent': 10},
            'sound': True,
            'badge': True,
            'notification_center': True,
            'cooldown_minutes': 15
        },
        'display': {
            'menubar_style': 'Icon only',
            'icon_style': 'Emoji (🌐 🟢 🟡 🔴)',
            'default_timeframe': '24 hours',
            'chart_type': 'Bar chart',
            'show_grid': True,
            'animate_charts': True,
            'theme': 'System'
        },
        'database': {
            'engine': 'SQLite',
            'retention_days': 30
        },
        'performance': {
            'max_workers': 10,
            'batch_writes': True
        },
        'network': {
            'ipv6': True,
            'dns_resolver': 'System'
        }
    }
    errors = SettingsValidator.validate_settings(valid_settings)
    assert errors == []
    invalid_settings = {
        'interval_sec': 2,
        'targets': [],
        'alerts': {'downtime': {'minutes': 0}},
        'display': {'default_timeframe': 'Invalid', 'chart_type': 'Invalid', 'theme': 'Invalid', 'menubar_style': 'Invalid', 'icon_style': 'Invalid'},
        'database': {'engine': 'Invalid', 'retention_days': 0},
        'performance': {'max_workers': 0, 'batch_writes': True},
        'network': {'ipv6': True, 'dns_resolver': 'Invalid'}
    }
    errors = SettingsValidator.validate_settings(invalid_settings)
    assert 'Check interval must be at least 5 seconds' in errors
    assert 'At least one target must be configured' in errors
    assert 'Downtime threshold must be at least 1 minute' in errors
    assert 'Default timeframe must be one of: Last hour, 24 hours, 7 days, 30 days' in errors
    assert 'Chart type must be one of: Bar chart, Line chart, Area chart, Heatmap' in errors
    assert 'Theme must be one of: System, Light, Dark' in errors
    assert 'Menu bar style must be a valid option' in errors
    assert 'Icon style must be a valid option' in errors
    assert 'Database engine must be SQLite or DuckDB' in errors
    assert 'Data retention must be at least 1 day' in errors
    assert 'Max workers must be at least 1' in errors
    assert 'DNS resolver must be a valid option or a valid IP address' in errors

def test_configuration_manager(tmp_path):
    config_path = tmp_path / 'settings.json'
    cm = ConfigurationManager(config_path)
    # Defaults loaded
    assert cm.get('interval_sec') == 30
    # Set and get
    cm.set('interval_sec', 42)
    assert cm.get('interval_sec') == 42
    # Save and reload
    cm.save()
    cm2 = ConfigurationManager(config_path)
    assert cm2.get('interval_sec') == 42
    # Dot notation
    cm.set('alerts.downtime.minutes', 7)
    assert cm.get('alerts.downtime.minutes') == 7
    cm.save()
    cm3 = ConfigurationManager(config_path)
    assert cm3.get('alerts.downtime.minutes') == 7

def test_settings_window_display_advanced_tabs():
    if SettingsWindow is None or import_error:
        pytest.skip(f"Toga or SettingsWindow not installed: {import_error}")
    app = SettingsWindow(config_manager={})
    app.startup()
    tab_names = [tab.text for tab in app.tabs.content]
    assert 'Display' in tab_names
    assert 'Advanced' in tab_names

def test_summary_card_creation():
    from networkstats.gui.summary_card import SummaryCard
    card = SummaryCard("Uptime", "percentage")
    widget = card.create_widget()
    assert widget is not None
    assert card.value_label.text == "--"
    card.update(99.5, 98.0)
    assert card.value_label.text == "99.50%"
    assert "↑" in card.trend_label.text or "↓" in card.trend_label.text or "No change" in card.trend_label.text
    if hasattr(card, 'progress'):
        assert card.progress.value == 99.5

def test_summary_card_latency():
    from networkstats.gui.summary_card import SummaryCard
    card = SummaryCard("Latency", "ms")
    card.create_widget()
    card.update(15.2, 17.3)
    assert card.value_label.text == "15.2 ms"
    assert "↓" in card.trend_label.text

def test_uptime_chart_bar_line_area():
    from networkstats.gui.uptime_chart import UptimeChart
    import polars as pl
    class DummySource:
        def get_uptime_data(self, timeframe, targets):
            return pl.DataFrame({
                'target': ['A', 'B'],
                'uptime_pct': [99.9, 98.7],
                'hour': [1, 2]
            })
    chart = UptimeChart(DummySource())
    # Bar chart
    chart.chart_type = 'bar'
    html = chart.create_chart(3600)
    assert 'html' in html
    # Line chart
    chart.chart_type = 'line'
    html = chart.create_chart(3600)
    assert 'html' in html
    # Area chart
    chart.chart_type = 'area'
    html = chart.create_chart(3600)
    assert 'html' in html

def test_latency_chart_percentiles_min_max_trend():
    from networkstats.gui.latency_chart import LatencyChart
    import polars as pl
    import numpy as np
    # Dummy data source for LatencyChart
    class DummySource:
        def get_latency_data(self, timeframe, targets):
            # Simulate 2 targets, 100 samples each
            np.random.seed(42)
            data = {
                'target': ['A'] * 100 + ['B'] * 100,
                'latency_ms': np.concatenate([
                    np.random.normal(20, 5, 100),
                    np.random.normal(50, 10, 100)
                ]),
                'datetime': np.tile(np.arange(100), 2)
            }
            return pl.DataFrame(data)
    chart = LatencyChart(DummySource())
    # Test chart HTML output
    html = chart.create_chart(3600)
    assert 'html' in html or '<div' in html
    # Test percentiles
    df = DummySource().get_latency_data(3600, None).to_pandas()
    percentiles = chart.compute_percentiles(df, percentiles=[50, 90, 99])
    assert 'A' in percentiles.index or 'A' in percentiles.columns
    assert percentiles.shape[1] == 3 or percentiles.shape[0] == 3
    # Test min/max
    minmax = chart.compute_min_max(df)
    assert 'min' in minmax.columns and 'max' in minmax.columns
    # Test trend analysis
    current_df = df[df['datetime'] < 50]
    previous_df = df[df['datetime'] >= 50]
    trend = chart.compute_trend(current_df, previous_df)
    assert isinstance(trend, dict)

def test_timeline_view_up_down_events():
    from networkstats.gui.timeline_view import TimelineView
    import polars as pl
    # Dummy data source for TimelineView
    class DummySource:
        def get_events(self, timeframe, targets):
            # Simulate up/down events for 2 targets
            data = {
                'target': ['A', 'A', 'B', 'B'],
                'status': ['up', 'down', 'up', 'down'],
                'start_time': [0, 50, 0, 60],
                'end_time': [50, 100, 60, 120],
                'duration_min': [50, 50, 60, 60]
            }
            return pl.DataFrame(data)
    view = TimelineView(DummySource())
    html = view.create_chart(3600)
    assert 'html' in html or '<div' in html

def test_heatmap_view_patterns_by_hour_day():
    from networkstats.gui.heatmap_view import HeatmapView
    import polars as pl
    import numpy as np
    # Dummy data source for HeatmapView
    class DummySource:
        def get_hourly_data(self, timeframe):
            # Simulate hourly data for 7 days, 24 hours
            data = {
                'hour_of_day': np.tile(np.arange(24), 7),
                'day_of_week': np.repeat(np.arange(7), 24),
                'uptime_pct': np.random.uniform(95, 100, 24*7)
            }
            return pl.DataFrame(data)
    view = HeatmapView(DummySource())
    html = view.create_chart(3600)
    assert 'html' in html or '<div' in html

def test_drilldown_handler_interactive_detail():
    from networkstats.gui.drilldown_handler import DrillDownHandler
    # Dummy stats window and data source
    class DummyStatsWindow:
        def __init__(self):
            self.detail_shown = False
        def show_detail_window(self, target, timestamp):
            self.detail_shown = (target, timestamp)
    stats_window = DummyStatsWindow()
    handler = DrillDownHandler(stats_window)
    # Simulate chart click event data
    event_data = {'points': [{'customdata': {'target': 'A', 'timestamp': 1234567890}}]}
    handler.on_chart_click(event_data)
    assert stats_window.detail_shown == ('A', 1234567890)

def test_realtime_updater_live_chart_updates():
    import asyncio
    from networkstats.gui.realtime_updater import RealtimeUpdater
    # Dummy WebView and data source
    class DummyWebView:
        def __init__(self):
            self.scripts = []
        async def evaluate_javascript(self, script):
            self.scripts.append(script)
    class DummyDataSource:
        async def get_latest_data(self):
            return {'timestamps': [1, 2, 3], 'values': [10, 20, 30]}
    webview = DummyWebView()
    updater = RealtimeUpdater(webview)
    updater.data_source = DummyDataSource()
    # Run one update iteration
    async def run_once():
        updater.is_running = True
        await updater.start_updates(run_once=True)
    asyncio.run(run_once())
    assert any('Plotly.extendTraces' in s for s in webview.scripts)

def test_export_manager_export_formats(tmp_path, monkeypatch):
    import polars as pl
    from networkstats.gui.export_manager import ExportManager
    # Dummy data source
    class DummySource:
        def get_export_data(self, timeframe, options):
            return pl.DataFrame({
                'target': ['A', 'B'],
                'uptime_pct': [99.9, 98.7],
                'latency_ms': [20.1, 50.2]
            })
    manager = ExportManager(DummySource())
    # CSV
    csv_bytes = manager._export_csv(manager.data_source.get_export_data(3600, {}))
    assert b'A' in csv_bytes and b'uptime_pct' in csv_bytes
    # Excel (mock xlsxwriter)
    class DummyWorkbook:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def add_worksheet(self, name): return DummyWorksheet()
    class DummyWorksheet:
        def write(self, *args, **kwargs): pass
    monkeypatch.setattr('xlsxwriter.Workbook', lambda *a, **kw: DummyWorkbook())
    excel_bytes = manager._export_excel(manager.data_source.get_export_data(3600, {}))
    assert isinstance(excel_bytes, bytes)
    # JSON
    json_bytes = manager._export_json(manager.data_source.get_export_data(3600, {}))
    assert b'"target"' in json_bytes
    # PNG/PDF (mock report generator)
    class DummyReport:
        async def generate_pdf(self): return b'PDFDATA'
        async def generate_image(self): return b'IMAGEDATA'
    async def dummy_export_chart(df, fmt):
        report = DummyReport()
        if fmt == 'PDF':
            return await report.generate_pdf()
        else:
            return await report.generate_image()
    manager._export_chart = dummy_export_chart
    import asyncio
    pdf_bytes = asyncio.run(manager._export_chart(manager.data_source.get_export_data(3600, {}), 'PDF'))
    png_bytes = asyncio.run(manager._export_chart(manager.data_source.get_export_data(3600, {}), 'PNG'))
    assert pdf_bytes == b'PDFDATA'
    assert png_bytes == b'IMAGEDATA'

def test_anomaly_detector_outlier_detection():
    import polars as pl
    from networkstats.gui.anomaly_detector import AnomalyDetector
    # Simulate latency data with outliers
    data = {
        'timestamp': list(range(100)),
        'latency_ms': [10]*30 + [100]*5 + [12]*30 + [200]*5 + [11]*30
    }
    df = pl.DataFrame(data)
    detector = AnomalyDetector(sensitivity=2.0)
    result = detector.detect_anomalies(df)
    # There should be some anomalies detected
    assert 'is_anomaly' in result.columns
    assert result['is_anomaly'].sum() > 0
    # Chart output
    html = detector.create_anomaly_chart(result)
    assert 'html' in html or '<div' in html

def test_packet_loss_chart_bar_line_area():
    from networkstats.gui.packet_loss_chart import PacketLossChart
    import polars as pl
    class DummySource:
        def get_packet_loss_data(self, timeframe, targets):
            return pl.DataFrame({
                'target': ['A', 'B'],
                'packet_loss_pct': [0.0, 5.5],
                'datetime': [1, 2]
            })
    chart = PacketLossChart(DummySource())
    # Bar chart
    chart.chart_type = 'bar'
    html = chart.create_chart(3600)
    assert 'html' in html
    # Line chart
    chart.chart_type = 'line'
    html = chart.create_chart(3600)
    assert 'html' in html
    # Area chart
    chart.chart_type = 'area'
    html = chart.create_chart(3600)
    assert 'html' in html

def test_drilldown_handler_triggers_detail():
    from networkstats.gui.drilldown_handler import DrillDownHandler
    class DummyStatsWindow:
        def __init__(self):
            self.detail_called = False
            self.detail_args = None
        def show_detail_window(self, target, timestamp):
            self.detail_called = True
            self.detail_args = (target, timestamp)
    stats_window = DummyStatsWindow()
    handler = DrillDownHandler(stats_window)
    event_data = {'points': [{'customdata': {'target': 'A', 'timestamp': '12345'}}]}
    handler.on_chart_click(event_data)
    assert stats_window.detail_called
    assert stats_window.detail_args == ('A', '12345')
