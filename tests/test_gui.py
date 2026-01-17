import pytest

try:
    from networkstats.gui.target_editor import TargetEditor
    from networkstats.gui.settings_window import SettingsApp
    from networkstats.gui.settings_validator import SettingsValidator
except ImportError:
    pytest.skip("TargetEditor, SettingsApp, or SettingsValidator not available", allow_module_level=True)

def test_target_editor_show(monkeypatch):
    # Patch rumps.Window to simulate user input
    class DummyResponse:
        clicked = True
        text = "1.2.3.4\nTest\nICMP\n0\n5.0\nfoo, bar"
    monkeypatch.setattr("rumps.Window", lambda *a, **k: type("W", (), {"run": lambda self: DummyResponse()})())
    called = {}
    def on_save(target):
        called.update(target)
    editor = TargetEditor(target=None, on_save=on_save)
    editor.show()
    assert called['address'] == '1.2.3.4'
    assert called['name'] == 'Test'
    assert called['protocol'] == 'ICMP'
    assert called['port'] == 0
    assert called['timeout'] == 5.0
    assert 'foo' in called['tags']
    assert 'bar' in called['tags']

def test_settings_app_menu():
    app = SettingsApp(config_manager={})
    menu_titles = []
    for item in app.menu:
        t = None
        if hasattr(item, 'title'):
            t = item.title() if callable(item.title) else item.title
        elif isinstance(item, str):
            t = item
        if t:
            menu_titles.append(t)
    assert 'General' in menu_titles
    assert 'Targets' in menu_titles
    assert 'Alerts' in menu_titles
    assert 'Display' in menu_titles
    assert 'Advanced' in menu_titles
    assert 'Save Settings' in menu_titles

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
