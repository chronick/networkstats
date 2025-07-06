# Settings GUI Specification

## Overview

The Settings GUI provides a user-friendly interface for configuring all aspects of the Network Stats application. It follows native platform design guidelines while maintaining consistency across features.

## Design Principles

1. **Intuitive Layout**: Logical grouping of related settings
2. **Immediate Feedback**: Live preview of changes where applicable
3. **Validation**: Real-time input validation with helpful error messages
4. **Accessibility**: Full keyboard navigation and screen reader support
5. **Platform Native**: Follows macOS Human Interface Guidelines

## Architecture

### Window Structure

```python
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class SettingsWindow(toga.App):
    def __init__(self, config_manager, on_save=None):
        super().__init__(
            'NetworkStats Settings',
            'com.networkstats.settings'
        )
        self.config_manager = config_manager
        self.on_save = on_save
        self.unsaved_changes = False
        
    def startup(self):
        """Build the settings interface."""
        self.main_window = toga.MainWindow(title='NetworkStats Settings')
        
        # Create tabbed interface
        self.tabs = toga.OptionContainer(
            style=Pack(flex=1)
        )
        
        # Add tabs
        self.tabs.add('General', self.create_general_tab())
        self.tabs.add('Targets', self.create_targets_tab())
        self.tabs.add('Alerts', self.create_alerts_tab())
        self.tabs.add('Display', self.create_display_tab())
        self.tabs.add('Advanced', self.create_advanced_tab())
        
        # Create main container with buttons
        main_box = toga.Box(
            children=[
                self.tabs,
                self.create_button_bar()
            ],
            style=Pack(direction=COLUMN, padding=10)
        )
        
        self.main_window.content = main_box
        self.main_window.show()
```

## Tab Specifications

### 1. General Tab

```python
def create_general_tab(self):
    """General application settings."""
    box = toga.Box(style=Pack(direction=COLUMN, padding=10))
    
    # Monitoring interval
    interval_box = toga.Box(style=Pack(direction=ROW, padding=5))
    interval_box.add(toga.Label('Check interval:', style=Pack(width=150)))
    
    self.interval_input = toga.NumberInput(
        min=5,
        max=3600,
        step=5,
        value=self.config_manager.get('interval_sec', 30),
        style=Pack(width=100)
    )
    interval_box.add(self.interval_input)
    interval_box.add(toga.Label('seconds', style=Pack(padding_left=5)))
    
    # Launch at login
    self.launch_at_login = toga.Switch(
        'Launch at login',
        value=self.config_manager.get('launch_at_login', False),
        on_change=self.on_setting_changed
    )
    
    # Auto-update
    self.auto_update = toga.Switch(
        'Check for updates automatically',
        value=self.config_manager.get('auto_update', True),
        on_change=self.on_setting_changed
    )
    
    # Logging level
    log_box = toga.Box(style=Pack(direction=ROW, padding=5))
    log_box.add(toga.Label('Log level:', style=Pack(width=150)))
    
    self.log_level = toga.Selection(
        items=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        value=self.config_manager.get('log_level', 'WARNING'),
        on_change=self.on_setting_changed
    )
    log_box.add(self.log_level)
    
    # Add all to box
    box.add(interval_box)
    box.add(toga.Divider())
    box.add(self.launch_at_login)
    box.add(self.auto_update)
    box.add(toga.Divider())
    box.add(log_box)
    
    return box
```

### 2. Targets Tab

```python
def create_targets_tab(self):
    """Network targets configuration."""
    box = toga.Box(style=Pack(direction=COLUMN, padding=10))
    
    # Target list
    self.target_table = toga.Table(
        headings=['Target', 'Name', 'Enabled'],
        data=self.load_targets_data(),
        style=Pack(flex=1, padding=5),
        on_select=self.on_target_selected
    )
    
    # Add/Edit/Remove buttons
    button_box = toga.Box(style=Pack(direction=ROW, padding=5))
    
    self.add_target_btn = toga.Button(
        '+',
        on_press=self.add_target,
        style=Pack(width=40)
    )
    self.edit_target_btn = toga.Button(
        'Edit',
        on_press=self.edit_target,
        style=Pack(width=60),
        enabled=False
    )
    self.remove_target_btn = toga.Button(
        '-',
        on_press=self.remove_target,
        style=Pack(width=40),
        enabled=False
    )
    
    button_box.add(self.add_target_btn)
    button_box.add(self.edit_target_btn)
    button_box.add(self.remove_target_btn)
    
    # Quick add section
    quick_add_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
    quick_add_box.add(toga.Label('Quick Add:', style=Pack(padding_bottom=5)))
    
    self.target_input = toga.TextInput(
        placeholder='Enter IP or hostname',
        style=Pack(flex=1)
    )
    self.target_name_input = toga.TextInput(
        placeholder='Display name (optional)',
        style=Pack(flex=1)
    )
    
    add_btn = toga.Button(
        'Add Target',
        on_press=self.quick_add_target,
        style=Pack(width=100)
    )
    
    input_row = toga.Box(style=Pack(direction=ROW, padding=2))
    input_row.add(self.target_input)
    input_row.add(self.target_name_input)
    input_row.add(add_btn)
    
    quick_add_box.add(input_row)
    
    # Validation feedback
    self.validation_label = toga.Label(
        '',
        style=Pack(padding=5, color='#FF0000')
    )
    
    # Add all to box
    box.add(self.target_table)
    box.add(button_box)
    box.add(toga.Divider())
    box.add(quick_add_box)
    box.add(self.validation_label)
    
    return box
```

#### Target Editor Dialog

```python
class TargetEditor(toga.Window):
    """Dialog for editing target details."""
    
    def __init__(self, target=None, on_save=None):
        super().__init__(
            title='Edit Target' if target else 'Add Target',
            size=(400, 300)
        )
        self.target = target or {}
        self.on_save = on_save
        
        # Form fields
        form_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Target address
        self.address_input = toga.TextInput(
            value=self.target.get('address', ''),
            placeholder='e.g., 8.8.8.8 or google.com',
            style=Pack(width=300, padding=5)
        )
        
        # Display name
        self.name_input = toga.TextInput(
            value=self.target.get('name', ''),
            placeholder='e.g., Google DNS',
            style=Pack(width=300, padding=5)
        )
        
        # Advanced options
        advanced_box = toga.Box(style=Pack(direction=COLUMN))
        
        self.port_input = toga.NumberInput(
            value=self.target.get('port', 0),
            min=0,
            max=65535,
            step=1,
            style=Pack(width=100)
        )
        
        self.protocol_selection = toga.Selection(
            items=['ICMP', 'TCP', 'UDP', 'HTTP', 'HTTPS'],
            value=self.target.get('protocol', 'ICMP')
        )
        
        self.timeout_input = toga.NumberInput(
            value=self.target.get('timeout', 5.0),
            min=0.1,
            max=60.0,
            step=0.1,
            style=Pack(width=100)
        )
        
        # Tags
        self.tags_input = toga.TextInput(
            value=', '.join(self.target.get('tags', [])),
            placeholder='e.g., primary, dns, critical',
            style=Pack(width=300)
        )
        
        # Build form
        form_box.add(self.create_field('Address:', self.address_input))
        form_box.add(self.create_field('Display Name:', self.name_input))
        form_box.add(toga.Divider())
        form_box.add(toga.Label('Advanced Options:', style=Pack(padding_top=10)))
        form_box.add(self.create_field('Protocol:', self.protocol_selection))
        form_box.add(self.create_field('Port:', self.port_input))
        form_box.add(self.create_field('Timeout (s):', self.timeout_input))
        form_box.add(self.create_field('Tags:', self.tags_input))
        
        # Buttons
        button_box = self.create_dialog_buttons()
        
        main_box = toga.Box(
            children=[form_box, button_box],
            style=Pack(direction=COLUMN)
        )
        
        self.content = main_box
```

### 3. Alerts Tab

```python
def create_alerts_tab(self):
    """Alert configuration."""
    box = toga.Box(style=Pack(direction=COLUMN, padding=10))
    
    # Enable alerts
    self.enable_alerts = toga.Switch(
        'Enable alerts',
        value=self.config_manager.get('alerts.enabled', True),
        on_change=self.toggle_alerts
    )
    
    # Alert conditions
    conditions_box = toga.Box(style=Pack(direction=COLUMN, padding_left=20))
    
    # Downtime alert
    downtime_box = toga.Box(style=Pack(direction=ROW, padding=5))
    self.alert_on_downtime = toga.Switch(
        'Alert when target is down for more than',
        value=self.config_manager.get('alerts.downtime.enabled', True)
    )
    self.downtime_threshold = toga.NumberInput(
        value=self.config_manager.get('alerts.downtime.minutes', 5),
        min=1,
        max=60,
        step=1,
        style=Pack(width=60)
    )
    downtime_box.add(self.alert_on_downtime)
    downtime_box.add(self.downtime_threshold)
    downtime_box.add(toga.Label('minutes'))
    
    # Latency alert
    latency_box = toga.Box(style=Pack(direction=ROW, padding=5))
    self.alert_on_latency = toga.Switch(
        'Alert when latency exceeds',
        value=self.config_manager.get('alerts.latency.enabled', True)
    )
    self.latency_threshold = toga.NumberInput(
        value=self.config_manager.get('alerts.latency.ms', 100),
        min=10,
        max=1000,
        step=10,
        style=Pack(width=80)
    )
    latency_box.add(self.alert_on_latency)
    latency_box.add(self.latency_threshold)
    latency_box.add(toga.Label('ms'))
    
    # Packet loss alert
    loss_box = toga.Box(style=Pack(direction=ROW, padding=5))
    self.alert_on_loss = toga.Switch(
        'Alert when packet loss exceeds',
        value=self.config_manager.get('alerts.packet_loss.enabled', False)
    )
    self.loss_threshold = toga.NumberInput(
        value=self.config_manager.get('alerts.packet_loss.percent', 10),
        min=1,
        max=100,
        step=1,
        style=Pack(width=60)
    )
    loss_box.add(self.alert_on_loss)
    loss_box.add(self.loss_threshold)
    loss_box.add(toga.Label('%'))
    
    conditions_box.add(downtime_box)
    conditions_box.add(latency_box)
    conditions_box.add(loss_box)
    
    # Notification settings
    notif_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
    notif_box.add(toga.Label('Notification Settings:', style=Pack(padding_bottom=5)))
    
    self.notif_sound = toga.Switch(
        'Play sound',
        value=self.config_manager.get('alerts.sound', True)
    )
    self.notif_badge = toga.Switch(
        'Show badge on menu bar icon',
        value=self.config_manager.get('alerts.badge', True)
    )
    self.notif_center = toga.Switch(
        'Show in Notification Center',
        value=self.config_manager.get('alerts.notification_center', True)
    )
    
    # Alert cooldown
    cooldown_box = toga.Box(style=Pack(direction=ROW, padding=5))
    cooldown_box.add(toga.Label('Cooldown period:', style=Pack(width=150)))
    self.alert_cooldown = toga.NumberInput(
        value=self.config_manager.get('alerts.cooldown_minutes', 15),
        min=1,
        max=60,
        step=1,
        style=Pack(width=60)
    )
    cooldown_box.add(self.alert_cooldown)
    cooldown_box.add(toga.Label('minutes'))
    
    # Add all to box
    box.add(self.enable_alerts)
    box.add(toga.Divider())
    box.add(conditions_box)
    box.add(toga.Divider())
    box.add(notif_box)
    box.add(self.notif_sound)
    box.add(self.notif_badge)
    box.add(self.notif_center)
    box.add(toga.Divider())
    box.add(cooldown_box)
    
    return box
```

### 4. Display Tab

```python
def create_display_tab(self):
    """Display preferences."""
    box = toga.Box(style=Pack(direction=COLUMN, padding=10))
    
    # Menu bar display
    menubar_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
    menubar_box.add(toga.Label('Menu Bar Display:', style=Pack(padding_bottom=5)))
    
    self.menubar_style = toga.Selection(
        items=[
            'Icon only',
            'Icon + Status',
            'Icon + Uptime %',
            'Icon + Latency',
            'Text only'
        ],
        value=self.config_manager.get('display.menubar_style', 'Icon only')
    )
    
    # Icon style
    self.icon_style = toga.Selection(
        items=[
            'Emoji (🌐 🟢 🟡 🔴)',
            'Classic (monochrome)',
            'Modern (colored)',
            'Minimal (dots)'
        ],
        value=self.config_manager.get('display.icon_style', 'Emoji')
    )
    
    # Statistics window
    stats_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
    stats_box.add(toga.Label('Statistics Window:', style=Pack(padding_bottom=5)))
    
    self.default_timeframe = toga.Selection(
        items=['Last hour', '24 hours', '7 days', '30 days'],
        value=self.config_manager.get('display.default_timeframe', '24 hours')
    )
    
    self.chart_type = toga.Selection(
        items=['Bar chart', 'Line chart', 'Area chart', 'Heatmap'],
        value=self.config_manager.get('display.chart_type', 'Bar chart')
    )
    
    self.show_grid = toga.Switch(
        'Show grid lines',
        value=self.config_manager.get('display.show_grid', True)
    )
    
    self.animate_charts = toga.Switch(
        'Animate chart transitions',
        value=self.config_manager.get('display.animate_charts', True)
    )
    
    # Theme
    theme_box = toga.Box(style=Pack(direction=ROW, padding=5))
    theme_box.add(toga.Label('Theme:', style=Pack(width=150)))
    self.theme = toga.Selection(
        items=['System', 'Light', 'Dark'],
        value=self.config_manager.get('display.theme', 'System')
    )
    theme_box.add(self.theme)
    
    # Add all to box
    box.add(menubar_box)
    box.add(self.menubar_style)
    box.add(toga.Divider())
    box.add(self.icon_style)
    box.add(toga.Divider())
    box.add(stats_box)
    box.add(self.default_timeframe)
    box.add(self.chart_type)
    box.add(self.show_grid)
    box.add(self.animate_charts)
    box.add(toga.Divider())
    box.add(theme_box)
    
    return box
```

### 5. Advanced Tab

```python
def create_advanced_tab(self):
    """Advanced settings."""
    box = toga.Box(style=Pack(direction=COLUMN, padding=10))
    
    # Database settings
    db_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
    db_box.add(toga.Label('Database:', style=Pack(padding_bottom=5)))
    
    self.db_engine = toga.Selection(
        items=['SQLite', 'DuckDB'],
        value=self.config_manager.get('database.engine', 'SQLite')
    )
    
    retention_box = toga.Box(style=Pack(direction=ROW, padding=5))
    retention_box.add(toga.Label('Keep data for:', style=Pack(width=150)))
    self.data_retention = toga.NumberInput(
        value=self.config_manager.get('database.retention_days', 30),
        min=1,
        max=365,
        step=1,
        style=Pack(width=60)
    )
    retention_box.add(self.data_retention)
    retention_box.add(toga.Label('days'))
    
    # Performance
    perf_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
    perf_box.add(toga.Label('Performance:', style=Pack(padding_bottom=5)))
    
    workers_box = toga.Box(style=Pack(direction=ROW, padding=5))
    workers_box.add(toga.Label('Max workers:', style=Pack(width=150)))
    self.max_workers = toga.NumberInput(
        value=self.config_manager.get('performance.max_workers', 10),
        min=1,
        max=50,
        step=1,
        style=Pack(width=60)
    )
    workers_box.add(self.max_workers)
    
    self.batch_writes = toga.Switch(
        'Enable batch database writes',
        value=self.config_manager.get('performance.batch_writes', True)
    )
    
    # Network
    net_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
    net_box.add(toga.Label('Network:', style=Pack(padding_bottom=5)))
    
    self.ipv6_enabled = toga.Switch(
        'Enable IPv6',
        value=self.config_manager.get('network.ipv6', True)
    )
    
    dns_box = toga.Box(style=Pack(direction=ROW, padding=5))
    dns_box.add(toga.Label('DNS resolver:', style=Pack(width=150)))
    self.dns_resolver = toga.Selection(
        items=['System', 'Google (8.8.8.8)', 'Cloudflare (1.1.1.1)', 'Custom'],
        value=self.config_manager.get('network.dns_resolver', 'System')
    )
    dns_box.add(self.dns_resolver)
    
    # Export/Import
    data_box = toga.Box(style=Pack(direction=ROW, padding=10))
    
    self.export_config_btn = toga.Button(
        'Export Config',
        on_press=self.export_config,
        style=Pack(width=120)
    )
    self.import_config_btn = toga.Button(
        'Import Config',
        on_press=self.import_config,
        style=Pack(width=120)
    )
    self.reset_btn = toga.Button(
        'Reset to Defaults',
        on_press=self.reset_to_defaults,
        style=Pack(width=120)
    )
    
    data_box.add(self.export_config_btn)
    data_box.add(self.import_config_btn)
    data_box.add(self.reset_btn)
    
    # Add all to box
    box.add(db_box)
    box.add(self.db_engine)
    box.add(retention_box)
    box.add(toga.Divider())
    box.add(perf_box)
    box.add(workers_box)
    box.add(self.batch_writes)
    box.add(toga.Divider())
    box.add(net_box)
    box.add(self.ipv6_enabled)
    box.add(dns_box)
    box.add(toga.Divider())
    box.add(data_box)
    
    return box
```

## Validation and Error Handling

```python
class SettingsValidator:
    """Validate settings input."""
    
    @staticmethod
    def validate_target(address: str) -> tuple[bool, str]:
        """Validate target address."""
        import re
        import socket
        
        # IP address pattern
        ip_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        
        # Hostname pattern
        hostname_pattern = re.compile(
            r'^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)'
            r'(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$'
        )
        
        if ip_pattern.match(address):
            return True, ""
        
        if hostname_pattern.match(address):
            # Try to resolve
            try:
                socket.gethostbyname(address)
                return True, ""
            except socket.gaierror:
                return False, f"Cannot resolve hostname: {address}"
        
        return False, "Invalid IP address or hostname"
    
    @staticmethod
    def validate_settings(settings: dict) -> list[str]:
        """Validate all settings, return list of errors."""
        errors = []
        
        # Validate interval
        if settings.get('interval_sec', 30) < 5:
            errors.append("Check interval must be at least 5 seconds")
        
        # Validate targets
        if not settings.get('targets'):
            errors.append("At least one target must be configured")
        
        # Validate alert thresholds
        if settings.get('alerts.downtime.minutes', 5) < 1:
            errors.append("Downtime threshold must be at least 1 minute")
        
        return errors
```

## Configuration Persistence

```python
import json
import pathlib
from typing import Any

class ConfigurationManager:
    """Manage settings persistence."""
    
    def __init__(self, config_path: pathlib.Path):
        self.config_path = config_path
        self.config = self.load()
        self.observers = []
    
    def load(self) -> dict:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self.get_defaults()
    
    def save(self):
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Notify observers
        for observer in self.observers:
            observer(self.config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value with dot notation support."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @staticmethod
    def get_defaults() -> dict:
        """Get default configuration."""
        return {
            'interval_sec': 30,
            'targets': [
                {'address': '8.8.8.8', 'name': 'Google DNS'},
                {'address': '1.1.1.1', 'name': 'Cloudflare DNS'}
            ],
            'alerts': {
                'enabled': True,
                'downtime': {'enabled': True, 'minutes': 5},
                'latency': {'enabled': True, 'ms': 100},
                'packet_loss': {'enabled': False, 'percent': 10}
            },
            'display': {
                'menubar_style': 'Icon only',
                'icon_style': 'Emoji',
                'theme': 'System'
            },
            'database': {
                'engine': 'SQLite',
                'retention_days': 30
            },
            'performance': {
                'max_workers': 10,
                'batch_writes': True
            },
            'network': {
                'ipv6': True,
                'dns_resolver': 'System'
            }
        }
```

## Testing

```python
import pytest
from unittest.mock import Mock, patch

class TestSettingsWindow:
    def test_settings_load(self):
        """Test loading settings into UI."""
        config = ConfigurationManager(':memory:')
        window = SettingsWindow(config)
        
        # Verify defaults loaded
        assert window.interval_input.value == 30
        assert window.enable_alerts.value == True
    
    def test_validation(self):
        """Test input validation."""
        # Test target validation
        valid, msg = SettingsValidator.validate_target('8.8.8.8')
        assert valid == True
        
        valid, msg = SettingsValidator.validate_target('invalid..address')
        assert valid == False
        assert 'Invalid' in msg
    
    def test_save_settings(self):
        """Test saving settings."""
        config = ConfigurationManager(':memory:')
        window = SettingsWindow(config)
        
        # Change setting
        window.interval_input.value = 60
        window.save_settings()
        
        # Verify saved
        assert config.get('interval_sec') == 60
```

## Future Enhancements

1. **Profile Support**: Multiple configuration profiles
2. **Cloud Sync**: Sync settings via iCloud
3. **Backup/Restore**: Automatic configuration backups
4. **Presets**: Pre-configured settings for common use cases
5. **Search**: Search functionality within settings
6. **Keyboard Shortcuts**: Full keyboard navigation
7. **Undo/Redo**: Undo recent changes
8. **Live Preview**: Preview changes before applying 