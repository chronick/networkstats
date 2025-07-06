# Menu Bar Application Specification: Future Implementation

## Enhanced Menu Structure

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

## Icon System
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

## Real-time Updates
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

## Notification System

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

## Advanced Features
### 1. Quick Actions

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

### 2. Status Bar Text

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

### 3. Export Functionality

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
