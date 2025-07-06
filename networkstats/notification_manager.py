import sys

class NotificationManager:
    """System notifications: sound, badge, notification center."""
    def __init__(self):
        self.platform = sys.platform
        if self.platform == 'darwin':
            try:
                import rumps
                self.rumps = rumps
                try:
                    from networkstats import menubar
                    self.set_badge = menubar.set_badge
                except ImportError:
                    self.set_badge = None
            except ImportError:
                self.rumps = None
                self.set_badge = None
        else:
            self.rumps = None
            self.set_badge = None

    def notify(self, message: str):
        """Show a system notification."""
        if self.platform == 'darwin' and self.rumps:
            self.rumps.notification("NetworkStats Alert", "", message, sound=True)
        else:
            print(f"NOTIFY: {message}")

    def play_sound(self):
        """Play a notification sound."""
        if self.platform == 'darwin' and self.rumps:
            self.rumps.alert("Alert", "Sound only", sound=True)
        else:
            print("[SOUND]")

    def show_badge(self, text: str = "!"):
        """Show a badge on the app icon (macOS only)."""
        if self.set_badge:
            self.set_badge(text)
        elif self.platform == 'darwin' and self.rumps:
            app = self.rumps.application
            if hasattr(app, 'badge'): app.badge = text
        else:
            print(f"[BADGE] {text}")

    def show_notification_center(self, message: str):
        """Show a notification in the system notification center."""
        self.notify(message) 