import rumps
import asyncio
import threading
from .monitor import monitor
from .gui.window import StatsWindow


def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor())


def run_status_bar():
    loop = asyncio.new_event_loop()
    threading.Thread(target=start_asyncio_loop, args=(loop,), daemon=True).start()

    class MenuApp(rumps.App):
        def __init__(self):
            super().__init__("Net📶", icon="🌐", quit_button=None)
            self.menu = ["Open Stats", None, "Quit"]

        @rumps.clicked("Open Stats")
        def open_stats(self, _):
            StatsWindow().main_loop()

        @rumps.clicked("Quit")
        def quit_(self, _):
            rumps.quit_application()

    MenuApp().run()


if __name__ == "__main__":
    run_status_bar()
