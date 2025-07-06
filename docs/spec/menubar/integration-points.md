# Menu Bar Application Specification: Integration Points



## 1. Statistics Window

@rumps.clicked("Open Statistics...")
def open_statistics(self, sender):
    """Open the statistics window."""
    # Launch Toga-based statistics window
    if not hasattr(self, 'stats_window'):
        self.stats_window = StatsWindow()
    self.stats_window.show()

```python
@rumps.clicked("Open Statistics...")
def open_statistics(self, sender):
    """Open the statistics window."""
    # Launch Toga-based statistics window
    if not hasattr(self, 'stats_window'):
        self.stats_window = StatsWindow()
    self.stats_window.show()

```

## 2. Settings Integration

@rumps.clicked("Settings...")
def open_settings(self, sender):
    """Open settings window."""
    if not hasattr(self, 'settings_window'):
        self.settings_window = SettingsWindow(
            on_save=self.reload_configuration
        )
    self.settings_window.show()

```python
@rumps.clicked("Settings...")
def open_settings(self, sender):
    """Open settings window."""
    if not hasattr(self, 'settings_window'):
        self.settings_window = SettingsWindow(
            on_save=self.reload_configuration
        )
    self.settings_window.show()

```

## 3. System Integration

class SystemIntegration:
    """macOS system integration."""
    
    def setup_launch_at_login(self):
        """Configure launch at login."""
        from LaunchServices import LSSharedFileListCreate
        # ... implementation ...
    
    def handle_sleep_wake(self):
        """Handle system sleep/wake events."""
        NSWorkspace.sharedWorkspace().notificationCenter().addObserver_selector_name_object_(
            self,
            'systemDidWake:',
            NSWorkspaceDidWakeNotification,
            None
        )

```python
class SystemIntegration:
    """macOS system integration."""
    
    def setup_launch_at_login(self):
        """Configure launch at login."""
        from LaunchServices import LSSharedFileListCreate
        # ... implementation ...
    
    def handle_sleep_wake(self):
        """Handle system sleep/wake events."""
        NSWorkspace.sharedWorkspace().notificationCenter().addObserver_selector_name_object_(
            self,
            'systemDidWake:',
            NSWorkspaceDidWakeNotification,
            None
        )

```
