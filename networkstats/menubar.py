import rumps
import asyncio
import threading
from .monitor import monitor
from .gui import StatsWindow
import logging
import sys
import os
from Foundation import NSBundle

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app_instance = None  # Global reference to MenuApp

def set_badge(text):
    """Set the badge on the menubar app icon (for alert integration)."""
    global app_instance
    if app_instance and hasattr(app_instance, 'badge'):
        app_instance.badge = text

def start_asyncio_loop(loop):
    logger.debug("Starting asyncio loop thread")
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(monitor())
    except Exception as e:
        import traceback
        logger.error("Exception in monitor thread:\n%s", traceback.format_exc())


def run_status_bar():
    logger.debug("Entered run_status_bar()")
    loop = asyncio.new_event_loop()
    threading.Thread(target=start_asyncio_loop, args=(loop,), daemon=True).start()
    logger.debug("Asyncio monitor thread started")

    def resource_path(relative_path: str) -> str:
        """
        Resolve an absolute path to a bundled resource.

        • PyInstaller one‑file/one‑dir: use the temporary extract dir (`sys._MEIPASS`).
        • Frozen macOS .app bundle: use Cocoa’s NSBundle to get the correct
          Contents/Resources path (robust even if the Python executable
          lives under Frameworks).
        • Development: fall back to the project root.
        """
        # if hasattr(sys, "_MEIPASS"):
        #     base_path = sys._MEIPASS
        # elif getattr(sys, "frozen", False):
        base_path = str(NSBundle.mainBundle().resourcePath())
        # else:
        #     base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_path, relative_path)

    icon_path = resource_path("icon.icns")

    class MenuApp(rumps.App):
        def __init__(self):
            logger.debug("Initializing MenuApp")
            super().__init__("Net📶", icon=icon_path, quit_button=None)
            self.menu = ["Open Stats", None, "Quit"]
            global app_instance
            app_instance = self

        @rumps.clicked("Open Stats")
        def open_stats(self, _):
            logger.debug("Open Stats clicked")
            StatsWindow().main_loop()

        @rumps.clicked("Quit")
        def quit_(self, _):
            logger.debug("Quit clicked")
            rumps.quit_application()

    logger.debug("Running MenuApp")
    MenuApp().run()


if __name__ == "__main__":
    logger.debug("menubar.py __main__ entry")
    run_status_bar()
