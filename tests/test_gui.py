import pytest

try:
    from networkstats.gui.window import StatsWindow
    import toga
except ImportError:
    StatsWindow = None


def test_stats_window_instantiates():
    if StatsWindow is None:
        pytest.skip("Toga not installed")
    app = StatsWindow()
    assert hasattr(app, "main_window") or hasattr(app, "startup")
