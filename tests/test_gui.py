import pytest  # type: ignore

try:
    from networkstats.gui.window import StatsWindow  # noqa: F401
    import toga  # type: ignore 
except ImportError:
    StatsWindow = None


def test_stats_window_instantiates():
    if StatsWindow is None:
        pytest.skip("Toga not installed")
    app = StatsWindow()
    assert hasattr(app, "main_window") or hasattr(app, "startup")
