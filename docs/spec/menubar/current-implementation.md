# Menu Bar Application Specification: Current Implementation



## Architecture

import rumps
import asyncio
import threading

class NetworkStatsApp(rumps.App):
    def __init__(self):
        super().__init__("Net📶", icon="🌐", quit_button=None)
        self.menu = ["Open Stats", None, "Quit"]
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring thread."""
        self.loop = asyncio.new_event_loop()
        self.monitor_thread = threading.Thread(
            target=self._run_monitor,
            daemon=True
        )
        self.monitor_thread.start()

```python
import rumps
import asyncio
import threading

class NetworkStatsApp(rumps.App):
    def __init__(self):
        super().__init__("Net📶", icon="🌐", quit_button=None)
        self.menu = ["Open Stats", None, "Quit"]
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring thread."""
        self.loop = asyncio.new_event_loop()
        self.monitor_thread = threading.Thread(
            target=self._run_monitor,
            daemon=True
        )
        self.monitor_thread.start()

```
