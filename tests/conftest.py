import pytest

@pytest.fixture(autouse=True)
def patch_toga_gui(monkeypatch):
    try:
        import toga
        monkeypatch.setattr(toga.App, "main_loop", lambda self: None)
        monkeypatch.setattr(toga.MainWindow, "show", lambda self: None)
    except ImportError:
        pass 