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
