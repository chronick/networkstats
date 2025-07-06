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
        'targets': ['8.8.8.8'],
        'alerts': {'downtime': {'minutes': 5}},
    }
    errors = SettingsValidator.validate_settings(valid_settings)
    assert errors == []
    invalid_settings = {
        'interval_sec': 2,
        'targets': [],
        'alerts': {'downtime': {'minutes': 0}},
    }
    errors = SettingsValidator.validate_settings(invalid_settings)
    assert 'Check interval must be at least 5 seconds' in errors
    assert 'At least one target must be configured' in errors
    assert 'Downtime threshold must be at least 1 minute' in errors

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
