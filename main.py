import logging
import logging.handlers
import os
import sys
import argparse

# --- macOS unified‑logging support ----------------------------------------
try:
    from Foundation import NSLog  # PyObjC gives access to NSLog()
except ModuleNotFoundError:       # (will be bundled automatically by pyinstaller/briefcase)
    NSLog = None

def setup_logging() -> None:
    """
    Configure logging so that messages appear in the macOS
    unified logging system (visible in Console.app) *and*
    in a rotating file under ~/Library/Logs/NetworkStats/.
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # 1️⃣  macOS unified logging via syslog
    syslog_handler = logging.handlers.SysLogHandler(address="/var/run/syslog")
    fmt = logging.Formatter("%(name)s[%(process)d] %(levelname)s: %(message)s")
    syslog_handler.setFormatter(fmt)
    root.addHandler(syslog_handler)

    # macOS Console.app / unified logging
    if NSLog is not None:
        class MacConsoleHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                if NSLog is None:
                    return
                try:
                    msg = self.format(record)
                    NSLog("%@", msg)
                except Exception:
                    self.handleError(record)
        ns_handler = MacConsoleHandler()
        ns_handler.setFormatter(fmt)
        root.addHandler(ns_handler)

    # 2️⃣  local log file for long‑term inspection
    log_dir = os.path.expanduser("~/Library/Logs/NetworkStats")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

def main():
    setup_logging()
    logger = logging.getLogger('NetworkStats')
    logger.info("Network‑Stats app started")

    parser = argparse.ArgumentParser(description="NetworkStats App Launcher")
    parser.add_argument('--settings', action='store_true', help='Launch Settings GUI')
    parser.add_argument('--stats', action='store_true', help='Launch Statistics Window')
    parser.add_argument('--menubar', action='store_true', help='Launch Menu Bar App (default)')
    args = parser.parse_args()

    if args.settings:
        # Launch Settings GUI
        from networkstats.gui.settings_window import SettingsWindow
        SettingsWindow().main_loop()
    elif args.stats:
        # Launch Statistics Window
        from networkstats.gui.stats_window import StatsWindow
        StatsWindow().main_loop()
    else:
        # Launch Menu Bar App (default)
        from networkstats.menubar import run_status_bar
        run_status_bar()

if __name__ == "__main__":
    main()

