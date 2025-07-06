import rumps
import asyncio
import threading
from .monitor import monitor
from .gui.window import StatsWindow
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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

    class MenuApp(rumps.App):
        def __init__(self):
            logger.debug("Initializing MenuApp")
            super().__init__("Net📶", icon="🌐", quit_button=None)
            self.menu = ["Open Stats", None, "Quit"]

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
