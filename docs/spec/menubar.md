# Menu Bar Application Specification

## Overview

The menu bar application provides a persistent, lightweight interface for Network Stats on macOS. It runs continuously in the background, displaying real-time network status and providing quick access to statistics and settings.

## Design Principles

1. **Minimal Resource Usage**: < 1% CPU, < 30MB RAM
2. **Instant Access**: All features within 2 clicks
3. **Non-intrusive**: Clean, professional appearance
4. **Real-time Updates**: Live status indicators
5. **Native Feel**: Follows macOS design guidelines

## Current Implementation

### Architecture

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

## Future Implementation

### Enhanced Menu Structure

```
NetworkStats [Icon]
├── Status: ✅ All Systems Operational    <- Dynamic status
├── ─────────────────────────────────    <- Separator
├── Google DNS (8.8.8.8)                 <- Target submenu
│   ├── Status: ✅ Online
│   ├── Latency: 12.5ms
│   ├── Uptime: 99.9%
│   └── Last Check: 2s ago
├── Cloudflare (1.1.1.1)
│   ├── Status: ✅ Online
│   ├── Latency: 8.2ms
│   ├── Uptime: 100%
│   └── Last Check: 2s ago
├── ─────────────────────────────────
├── Quick Stats                          <- Submenu
│   ├── Last Hour: 99.8% uptime
│   ├── Last 24h: 99.5% uptime
│   └── Last Week: 98.9% uptime
├── ─────────────────────────────────
├── 📊 Open Statistics...
├── ⚙️  Settings...
├── 🔔 Alerts                           <- Submenu
│   ├── ✓ Enable Alerts
│   ├── Alert on Downtime > 5 min
│   └── Alert on High Latency > 100ms
├── ─────────────────────────────────
├── 📋 Export Report...
├── ℹ️  About NetworkStats
└── 🚪 Quit
```

### Icon System

```python
class StatusIcon:
    """Dynamic menu bar icon based on network status."""
    
    # Icon states
    ICONS = {
        'all_good': '🟢',      # All targets online
        'partial': '🟡',       # Some targets offline
        'all_down': '🔴',      # All targets offline
        'checking': '🔄',      # Currently checking
        'error': '⚠️',         # Error state
    }
    
    # Alternative: Custom NSImage icons
    CUSTOM_ICONS = {
        'all_good': 'assets/icon_green.png',
        'partial': 'assets/icon_yellow.png',
        'all_down': 'assets/icon_red.png',
        'checking': 'assets/icon_checking.png',
        'error': 'assets/icon_error.png',
    }
    
    def __init__(self, app: rumps.App):
        self.app = app
        self.current_state = 'checking'
        
    def update_icon(self, state: str):
        """Update menu bar icon."""
        if state != self.current_state:
            self.current_state = state
            self.app.icon = self.ICONS[state]
            
            # Optional: Add badge for alert count
            if self.alert_count > 0:
                self.app.title = f"{self.ICONS[state]} {self.alert_count}"
```

### Real-time Updates

```python
class MenuUpdater:
    """Handle real-time menu updates."""
    
    def __init__(self, app: NetworkStatsApp):
        self.app = app
        self.target_items = {}
        self.last_update = {}
        
    async def update_target_status(self, target: str, result: dict):
        """Update menu item for specific target."""
        # Create or update target menu item
        if target not in self.target_items:
            self.target_items[target] = self._create_target_menu(target)
            
        item = self.target_items[target]
        
        # Update submenu items
        status = "✅ Online" if result['success'] else "❌ Offline"
        latency = f"{result['latency']:.1f}ms" if result['success'] else "N/A"
        
        item['Status'].title = f"Status: {status}"
        item['Latency'].title = f"Latency: {latency}"
        item['Last Check'].title = f"Last Check: {self._format_time_ago(result['timestamp'])}"
        
        # Update icon based on overall status
        self._update_overall_status()
        
    def _format_time_ago(self, timestamp: float) -> str:
        """Format timestamp as human-readable time ago."""
        delta = time.time() - timestamp
        if delta < 60:
            return f"{int(delta)}s ago"
        elif delta < 3600:
            return f"{int(delta/60)}m ago"
        else:
            return f"{int(delta/3600)}h ago"
```

### Notification System

```python
import UserNotifications

class NotificationManager:
    """Handle system notifications for alerts."""
    
    def __init__(self):
        self.setup_notifications()
        
    def setup_notifications(self):
        """Request notification permissions."""
        # For PyObjC implementation
        self.notification_center = UserNotifications.UNUserNotificationCenter.currentNotificationCenter()
        self.notification_center.requestAuthorizationWithOptions_completionHandler_(
            UserNotifications.UNAuthorizationOptionAlert |
            UserNotifications.UNAuthorizationOptionSound,
            self._authorization_callback
        )
    
    def send_alert(self, title: str, message: str, target: str = None):
        """Send system notification."""
        notification = rumps.notification(
            title=title,
            subtitle=f"Target: {target}" if target else "",
            message=message,
            sound=True,
            action_button="View Stats",
            other_button="Dismiss"
        )
        
        # Handle notification response
        if notification.clicked:
            self.app.open_stats_for_target(target)
```

### Advanced Features

#### 1. Quick Actions

```python
class QuickActions:
    """Keyboard shortcuts and quick actions."""
    
    SHORTCUTS = {
        'cmd+r': 'refresh_all',
        'cmd+s': 'open_stats',
        'cmd+,': 'open_settings',
        'cmd+e': 'export_report',
    }
    
    @rumps.clicked("Refresh Now")
    def refresh_now(self, _):
        """Force immediate refresh of all targets."""
        asyncio.run_coroutine_threadsafe(
            self.monitor.check_all_targets(),
            self.loop
        )
```

#### 2. Status Bar Text

```python
class StatusBarDisplay:
    """Optional text display in menu bar."""
    
    def __init__(self, app: rumps.App):
        self.app = app
        self.display_mode = 'icon_only'  # or 'uptime', 'latency', 'custom'
        
    def update_display(self, stats: dict):
        """Update menu bar text based on display mode."""
        if self.display_mode == 'icon_only':
            self.app.title = ""
        elif self.display_mode == 'uptime':
            uptime = stats.get('overall_uptime', 0)
            self.app.title = f"{uptime:.1f}%"
        elif self.display_mode == 'latency':
            avg_latency = stats.get('avg_latency', 0)
            self.app.title = f"{avg_latency:.0f}ms"
        elif self.display_mode == 'custom':
            self.app.title = self.format_custom(stats)
```

#### 3. Export Functionality

```python
class ReportExporter:
    """Export network statistics reports."""
    
    @rumps.clicked("Export Report...")
    def export_report(self, sender):
        """Export statistics report."""
        # Show save dialog
        panel = NSSavePanel.alloc().init()
        panel.setNameFieldStringValue_("network_stats_report.pdf")
        panel.setAllowedFileTypes_(["pdf", "csv", "json"])
        
        if panel.runModal() == NSModalResponseOK:
            path = panel.URL().path()
            file_type = path.split('.')[-1]
            
            if file_type == 'pdf':
                self._export_pdf(path)
            elif file_type == 'csv':
                self._export_csv(path)
            elif file_type == 'json':
                self._export_json(path)
    
    def _export_pdf(self, path: str):
        """Generate PDF report with charts."""
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        # Create PDF with statistics and charts
        # ... implementation ...
```

## Performance Optimization

### Memory Management

```python
class MemoryEfficientMenu:
    """Optimize memory usage for menu items."""
    
    def __init__(self):
        self.menu_cache = {}
        self.update_queue = asyncio.Queue(maxsize=100)
        
    def update_menu_item(self, path: str, value: str):
        """Update menu item with caching."""
        if path in self.menu_cache and self.menu_cache[path] == value:
            return  # No change needed
            
        self.menu_cache[path] = value
        # Batch updates
        self.update_queue.put_nowait((path, value))
        
    async def process_updates(self):
        """Process batched menu updates."""
        updates = []
        
        # Collect updates
        while not self.update_queue.empty():
            updates.append(await self.update_queue.get())
            
        # Apply updates in single pass
        if updates:
            self._apply_menu_updates(updates)
```

### CPU Optimization

```python
class CPUOptimizedApp:
    """Minimize CPU usage."""
    
    def __init__(self):
        self.update_interval = 1.0  # Minimum update interval
        self.last_update = 0
        self.pending_updates = {}
        
    def schedule_update(self, key: str, data: dict):
        """Schedule update with rate limiting."""
        self.pending_updates[key] = data
        
        now = time.time()
        if now - self.last_update >= self.update_interval:
            self._flush_updates()
            self.last_update = now
```

## Integration Points

### 1. Statistics Window

```python
@rumps.clicked("Open Statistics...")
def open_statistics(self, sender):
    """Open the statistics window."""
    # Launch Toga-based statistics window
    if not hasattr(self, 'stats_window'):
        self.stats_window = StatsWindow()
    self.stats_window.show()
```

### 2. Settings Integration

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

### 3. System Integration

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

## Testing Strategy

```python
import pytest
from unittest.mock import Mock, patch

def test_menu_structure():
    """Test menu hierarchy."""
    app = NetworkStatsApp()
    
    # Verify menu structure
    assert "Open Statistics..." in app.menu
    assert "Settings..." in app.menu
    assert "Quit" in app.menu

def test_icon_updates():
    """Test icon state changes."""
    app = NetworkStatsApp()
    icon_manager = StatusIcon(app)
    
    # Test state transitions
    icon_manager.update_icon('all_good')
    assert app.icon == '🟢'
    
    icon_manager.update_icon('all_down')
    assert app.icon == '🔴'

@patch('rumps.notification')
def test_notifications(mock_notification):
    """Test notification system."""
    notifier = NotificationManager()
    notifier.send_alert("Network Down", "8.8.8.8 is unreachable")
    
    mock_notification.assert_called_once()
```

## Accessibility

### VoiceOver Support

```python
class AccessibleMenu:
    """Ensure menu items are accessible."""
    
    def create_menu_item(self, title: str, action=None):
        """Create accessible menu item."""
        item = rumps.MenuItem(title)
        
        # Add accessibility description
        if hasattr(item, '_menuitem'):
            item._menuitem.setAccessibilityDescription_(
                f"Network stats menu item: {title}"
            )
        
        return item
```

## Future Enhancements

1. **Touch Bar Support**: Quick stats on MacBook Pro Touch Bar
2. **Widgets**: macOS widget for Today view
3. **Siri Shortcuts**: "Hey Siri, what's my network uptime?"
4. **Apple Watch**: Companion app for quick glances
5. **iCloud Sync**: Sync settings across devices
6. **Dark Mode**: Automatic theme switching
7. **Localization**: Multi-language support
8. **Custom Plugins**: Extension system for custom monitors 