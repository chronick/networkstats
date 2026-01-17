import platform
try:
    import rumps
except ImportError:
    rumps = None

class NotificationManager:
    """System notifications: sound, badge, notification center."""
    def __init__(self):
        self.platform = platform.system().lower()
        self.rumps = rumps
        self.set_badge = None  # To be set by menubar integration if needed

    def notify(self, message):
        """Show a notification using rumps if available."""
        if self.platform == 'darwin' and self.rumps:
            self.rumps.notification("NetworkStats", "Alert", message)
        # else: fallback or log

    def play_sound(self):
        """Play a notification sound (use rumps.alert as a workaround)."""
        if self.platform == 'darwin' and self.rumps:
            self.rumps.alert("Alert", "Sound only")
        # else: fallback or log

    def show_badge(self, text):
        """Show a badge on the menubar icon if set_badge is available."""
        if self.set_badge:
            self.set_badge(text)
        # else: fallback or log

    def show_notification_center(self, message):
        if self.platform == 'darwin' and self.rumps:
            self.rumps.notification("NetworkStats", "Notification Center", message)
        # else: fallback or log 