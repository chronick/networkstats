import logging
import logging.handlers
import os

# --- macOS unified‑logging support ----------------------------------------
try:
    from Foundation import NSLog  # PyObjC gives access to NSLog()
except ModuleNotFoundError:       # (will be bundled automatically by pyinstaller/briefcase)
    NSLog = None

class MacConsoleHandler(logging.Handler):
    """
    A logging.Handler that forwards records to macOS’s unified logging
    (visible in Console.app) via Foundation.NSLog().
    """
    def emit(self, record: logging.LogRecord) -> None:
        # Skip if PyObjC isn’t available (e.g., on CI runners)
        if NSLog is None:
            return
        try:
            msg = self.format(record)
            # NSLog uses printf‑style format strings; %@ is an NSString placeholder.
            NSLog("%@", msg)
        except Exception:
            self.handleError(record)

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
        ns_handler = MacConsoleHandler()
        ns_handler.setFormatter(fmt)
        root.addHandler(ns_handler)

    # 3️⃣  local log file for long‑term inspection

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


if __name__ == "__main__":
    main()

