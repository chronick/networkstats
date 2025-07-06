import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from .target_editor import TargetEditor

class SettingsWindow(toga.App):
    def __init__(self, config_manager=None, on_save=None):
        super().__init__('NetworkStats Settings', 'com.networkstats.settings')
        self.config_manager = config_manager
        self.on_save = on_save
        self.unsaved_changes = False

    def create_general_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        interval_box = toga.Box(style=Pack(direction="row", margin=5))
        interval_box.add(toga.Label('Check interval:', style=Pack(width=150)))
        self.interval_input = toga.NumberInput(
            min=5,
            max=3600,
            step=5,
            value=(self.config_manager.get('interval_sec', 30) if self.config_manager else 30),
            style=Pack(width=100)
        )
        interval_box.add(self.interval_input)
        interval_box.add(toga.Label('seconds', style=Pack(margin_left=5)))
        self.launch_at_login = toga.Switch(
            'Launch at login',
            value=(self.config_manager.get('launch_at_login', False) if self.config_manager else False),
            on_change=self.on_setting_changed
        )
        self.auto_update = toga.Switch(
            'Check for updates automatically',
            value=(self.config_manager.get('auto_update', True) if self.config_manager else True),
            on_change=self.on_setting_changed
        )
        log_box = toga.Box(style=Pack(direction="row", margin=5))
        log_box.add(toga.Label('Log level:', style=Pack(width=150)))
        self.log_level = toga.Selection(
            items=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            value=(self.config_manager.get('log_level', 'WARNING') if self.config_manager else 'WARNING'),
            on_change=self.on_setting_changed
        )
        log_box.add(self.log_level)
        box.add(interval_box)
        box.add(toga.Divider())
        box.add(self.launch_at_login)
        box.add(self.auto_update)
        box.add(toga.Divider())
        box.add(log_box)
        return box

    def on_setting_changed(self, widget):
        self.unsaved_changes = True

    def create_targets_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        targets = self.config_manager.get('targets', []) if self.config_manager else []
        table_data = [(t if isinstance(t, dict) else {'address': t, 'name': ''}) for t in targets]
        self.target_table = toga.Table(
            headings=['Address', 'Name'],
            data=[[row['address'], row.get('name', '')] for row in table_data],
            style=Pack(flex=1, margin=5),
            on_select=self.on_target_selected
        )
        button_box = toga.Box(style=Pack(direction="row", margin=5))
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
        quick_add_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
        quick_add_box.add(toga.Label('Quick Add:', style=Pack(margin_bottom=5)))
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
        input_row = toga.Box(style=Pack(direction="row", margin=2))
        input_row.add(self.target_input)
        input_row.add(self.target_name_input)
        input_row.add(add_btn)
        quick_add_box.add(input_row)
        self.validation_label = toga.Label(
            '',
            style=Pack(margin=5, color='#FF0000')
        )
        box.add(self.target_table)
        box.add(button_box)
        box.add(toga.Divider())
        box.add(quick_add_box)
        box.add(self.validation_label)
        return box

    def on_target_selected(self, widget, row=None):
        self.edit_target_btn.enabled = row is not None
        self.remove_target_btn.enabled = row is not None

    def add_target(self, widget):
        def on_save(new_target):
            if not new_target['address']:
                self.validation_label.text = 'Address is required.'
                return
            targets = self.config_manager.get('targets', []) if self.config_manager else []
            addresses = [t['address'] if isinstance(t, dict) else t for t in targets]
            if new_target['address'] in addresses:
                self.validation_label.text = 'Target already exists.'
                return
            targets.append(new_target)
            if self.config_manager is not None:
                self.config_manager['targets'] = targets
            self.target_table.data.append([new_target['address'], new_target.get('name', '')])
            self.validation_label.text = ''
            self.unsaved_changes = True
        editor = TargetEditor(target=None, on_save=on_save)
        editor.show()

    def edit_target(self, widget):
        row = self.target_table.selection
        if row is None:
            return
        address, name = row
        targets = self.config_manager.get('targets', []) if self.config_manager else []
        idx = next((i for i, t in enumerate(targets) if (t.get('address') if isinstance(t, dict) else t) == address), None)
        if idx is None:
            return
        target = targets[idx]
        def on_save(updated_target):
            if not updated_target['address']:
                self.validation_label.text = 'Address is required.'
                return
            addresses = [t['address'] if isinstance(t, dict) else t for i, t in enumerate(targets) if i != idx]
            if updated_target['address'] in addresses:
                self.validation_label.text = 'Target already exists.'
                return
            targets[idx] = updated_target
            if self.config_manager is not None:
                self.config_manager['targets'] = targets
            self.target_table.data[idx] = [updated_target['address'], updated_target.get('name', '')]
            self.validation_label.text = ''
            self.unsaved_changes = True
        editor = TargetEditor(target=target, on_save=on_save)
        editor.show()

    def remove_target(self, widget):
        row = self.target_table.selection
        if row is None:
            return
        address, name = row
        targets = self.config_manager.get('targets', []) if self.config_manager else []
        idx = next((i for i, t in enumerate(targets) if (t.get('address') if isinstance(t, dict) else t) == address), None)
        if idx is not None:
            del targets[idx]
            if self.config_manager is not None:
                self.config_manager['targets'] = targets
            del self.target_table.data[idx]
            self.validation_label.text = ''
            self.unsaved_changes = True

    def quick_add_target(self, widget):
        address = self.target_input.value.strip()
        name = self.target_name_input.value.strip()
        if not address:
            self.validation_label.text = 'Address is required.'
            return
        targets = self.config_manager.get('targets', []) if self.config_manager else []
        addresses = [t['address'] if isinstance(t, dict) else t for t in targets]
        if address in addresses:
            self.validation_label.text = 'Target already exists.'
            return
        new_target = {'address': address, 'name': name, 'protocol': 'ICMP', 'port': 0, 'timeout': 5.0, 'tags': []}
        targets.append(new_target)
        if self.config_manager is not None:
            self.config_manager['targets'] = targets
        self.target_table.data.append([address, name])
        self.target_input.value = ''
        self.target_name_input.value = ''
        self.validation_label.text = ''
        self.unsaved_changes = True

    def create_alerts_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        # Enable alerts
        self.enable_alerts = toga.Switch(
            'Enable alerts',
            value=(self.config_manager.get('alerts', {}).get('enabled', True) if self.config_manager else True),
            on_change=self.on_setting_changed
        )
        # Alert conditions
        conditions_box = toga.Box(style=Pack(direction=COLUMN, margin_left=20))
        # Downtime alert
        downtime = self.config_manager.get('alerts', {}).get('downtime', {}) if self.config_manager else {}
        downtime_box = toga.Box(style=Pack(direction="row", margin=5))
        self.alert_on_downtime = toga.Switch(
            'Alert when target is down for more than',
            value=downtime.get('enabled', True),
            on_change=self.on_setting_changed
        )
        self.downtime_threshold = toga.NumberInput(
            value=downtime.get('minutes', 5),
            min=1,
            max=60,
            step=1,
            style=Pack(width=60),
            on_change=self.on_setting_changed
        )
        downtime_box.add(self.alert_on_downtime)
        downtime_box.add(self.downtime_threshold)
        downtime_box.add(toga.Label('minutes'))
        # Latency alert
        latency = self.config_manager.get('alerts', {}).get('latency', {}) if self.config_manager else {}
        latency_box = toga.Box(style=Pack(direction="row", margin=5))
        self.alert_on_latency = toga.Switch(
            'Alert when latency exceeds',
            value=latency.get('enabled', True),
            on_change=self.on_setting_changed
        )
        self.latency_threshold = toga.NumberInput(
            value=latency.get('ms', 100),
            min=10,
            max=1000,
            step=10,
            style=Pack(width=80),
            on_change=self.on_setting_changed
        )
        latency_box.add(self.alert_on_latency)
        latency_box.add(self.latency_threshold)
        latency_box.add(toga.Label('ms'))
        # Packet loss alert
        loss = self.config_manager.get('alerts', {}).get('packet_loss', {}) if self.config_manager else {}
        loss_box = toga.Box(style=Pack(direction="row", margin=5))
        self.alert_on_loss = toga.Switch(
            'Alert when packet loss exceeds',
            value=loss.get('enabled', False),
            on_change=self.on_setting_changed
        )
        self.loss_threshold = toga.NumberInput(
            value=loss.get('percent', 10),
            min=1,
            max=100,
            step=1,
            style=Pack(width=60),
            on_change=self.on_setting_changed
        )
        loss_box.add(self.alert_on_loss)
        loss_box.add(self.loss_threshold)
        loss_box.add(toga.Label('%'))
        conditions_box.add(downtime_box)
        conditions_box.add(latency_box)
        conditions_box.add(loss_box)
        # Notification settings
        notif_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        notif_box.add(toga.Label('Notification Settings:', style=Pack(margin_bottom=5)))
        self.notif_sound = toga.Switch(
            'Play sound',
            value=(self.config_manager.get('alerts', {}).get('sound', True) if self.config_manager else True),
            on_change=self.on_setting_changed
        )
        self.notif_badge = toga.Switch(
            'Show badge on menu bar icon',
            value=(self.config_manager.get('alerts', {}).get('badge', True) if self.config_manager else True),
            on_change=self.on_setting_changed
        )
        self.notif_center = toga.Switch(
            'Show in Notification Center',
            value=(self.config_manager.get('alerts', {}).get('notification_center', True) if self.config_manager else True),
            on_change=self.on_setting_changed
        )
        # Alert cooldown
        cooldown_box = toga.Box(style=Pack(direction="row", margin=5))
        cooldown_box.add(toga.Label('Cooldown period:', style=Pack(width=150)))
        self.alert_cooldown = toga.NumberInput(
            value=(self.config_manager.get('alerts', {}).get('cooldown_minutes', 15) if self.config_manager else 15),
            min=1,
            max=60,
            step=1,
            style=Pack(width=60),
            on_change=self.on_setting_changed
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

    def create_display_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        # Menu bar display
        menubar_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
        menubar_box.add(toga.Label('Menu Bar Display:', style=Pack(margin_bottom=5)))
        self.menubar_style = toga.Selection(
            items=[
                'Icon only',
                'Icon + Status',
                'Icon + Uptime %',
                'Icon + Latency',
                'Text only'
            ],
            value=(self.config_manager.get('display', {}).get('menubar_style', 'Icon only') if self.config_manager else 'Icon only'),
            style=Pack(width=200)
        )
        # Icon style
        self.icon_style = toga.Selection(
            items=[
                'Emoji (🌐 🟢 🟡 🔴)',
                'Classic (monochrome)',
                'Modern (colored)',
                'Minimal (dots)'
            ],
            value=(self.config_manager.get('display', {}).get('icon_style', 'Emoji (🌐 🟢 🟡 🔴)') if self.config_manager else 'Emoji (🌐 🟢 🟡 🔴)'),
            style=Pack(width=200)
        )
        # Statistics window
        stats_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
        stats_box.add(toga.Label('Statistics Window:', style=Pack(margin_bottom=5)))
        self.default_timeframe = toga.Selection(
            items=['Last hour', '24 hours', '7 days', '30 days'],
            value=(self.config_manager.get('display', {}).get('default_timeframe', '24 hours') if self.config_manager else '24 hours'),
            style=Pack(width=150)
        )
        self.chart_type = toga.Selection(
            items=['Bar chart', 'Line chart', 'Area chart', 'Heatmap'],
            value=(self.config_manager.get('display', {}).get('chart_type', 'Bar chart') if self.config_manager else 'Bar chart'),
            style=Pack(width=150)
        )
        self.show_grid = toga.Switch(
            'Show grid lines',
            value=(self.config_manager.get('display', {}).get('show_grid', True) if self.config_manager else True)
        )
        self.animate_charts = toga.Switch(
            'Animate chart transitions',
            value=(self.config_manager.get('display', {}).get('animate_charts', True) if self.config_manager else True)
        )
        # Theme
        theme_box = toga.Box(style=Pack(direction="row", margin=5))
        theme_box.add(toga.Label('Theme:', style=Pack(width=150)))
        self.theme = toga.Selection(
            items=['System', 'Light', 'Dark'],
            value=(self.config_manager.get('display', {}).get('theme', 'System') if self.config_manager else 'System'),
            style=Pack(width=100)
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

    def create_advanced_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        # Database settings
        db_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
        db_box.add(toga.Label('Database:', style=Pack(margin_bottom=5)))
        self.db_engine = toga.Selection(
            items=['SQLite', 'DuckDB'],
            value=(self.config_manager.get('database', {}).get('engine', 'SQLite') if self.config_manager else 'SQLite'),
            style=Pack(width=120)
        )
        retention_box = toga.Box(style=Pack(direction="row", margin=5))
        retention_box.add(toga.Label('Keep data for:', style=Pack(width=150)))
        self.data_retention = toga.NumberInput(
            value=(self.config_manager.get('database', {}).get('retention_days', 30) if self.config_manager else 30),
            min=1,
            max=365,
            step=1,
            style=Pack(width=60)
        )
        retention_box.add(self.data_retention)
        retention_box.add(toga.Label('days'))
        # Performance
        perf_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
        perf_box.add(toga.Label('Performance:', style=Pack(margin_bottom=5)))
        workers_box = toga.Box(style=Pack(direction="row", margin=5))
        workers_box.add(toga.Label('Max workers:', style=Pack(width=150)))
        self.max_workers = toga.NumberInput(
            value=(self.config_manager.get('performance', {}).get('max_workers', 10) if self.config_manager else 10),
            min=1,
            max=50,
            step=1,
            style=Pack(width=60)
        )
        workers_box.add(self.max_workers)
        self.batch_writes = toga.Switch(
            'Enable batch database writes',
            value=(self.config_manager.get('performance', {}).get('batch_writes', True) if self.config_manager else True)
        )
        # Network
        net_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
        net_box.add(toga.Label('Network:', style=Pack(margin_bottom=5)))
        self.ipv6_enabled = toga.Switch(
            'Enable IPv6',
            value=(self.config_manager.get('network', {}).get('ipv6', True) if self.config_manager else True)
        )
        dns_box = toga.Box(style=Pack(direction="row", margin=5))
        dns_box.add(toga.Label('DNS resolver:', style=Pack(width=150)))
        self.dns_resolver = toga.Selection(
            items=['System', 'Google (8.8.8.8)', 'Cloudflare (1.1.1.1)', 'Custom'],
            value=(self.config_manager.get('network', {}).get('dns_resolver', 'System') if self.config_manager else 'System'),
            style=Pack(width=180)
        )
        dns_box.add(self.dns_resolver)
        # Export/Import
        data_box = toga.Box(style=Pack(direction="row", margin=10))
        self.export_config_btn = toga.Button(
            'Export Config',
            on_press=self.export_config if hasattr(self, 'export_config') else None,
            style=Pack(width=120)
        )
        self.import_config_btn = toga.Button(
            'Import Config',
            on_press=self.import_config if hasattr(self, 'import_config') else None,
            style=Pack(width=120)
        )
        self.reset_btn = toga.Button(
            'Reset to Defaults',
            on_press=self.reset_to_defaults if hasattr(self, 'reset_to_defaults') else None,
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

    def startup(self):
        self.main_window = toga.MainWindow(title='NetworkStats Settings')
        self.tabs = toga.OptionContainer(
            content=[
                ('General', self.create_general_tab()),
                ('Targets', self.create_targets_tab()),
                ('Alerts', self.create_alerts_tab()),
                ('Display', self.create_display_tab()),
                ('Advanced', self.create_advanced_tab()),
            ],
            style=Pack(flex=1)
        )
        # Error label for validation feedback
        self.error_label = toga.Label('', style=Pack(color='#FF0000', margin=10))
        # Save button
        self.save_btn = toga.Button('Save', on_press=self.on_save_clicked, style=Pack(width=100, margin=10))
        # Main layout
        main_box = toga.Box(children=[self.tabs, self.error_label, self.save_btn], style=Pack(direction=COLUMN, margin=10))
        self.main_window.content = main_box
        self.main_window.show()

    def on_save_clicked(self, widget):
        from .settings_validator import SettingsValidator
        # Gather settings from all tabs
        settings = self.collect_settings()
        errors = SettingsValidator.validate_settings(settings)
        if errors:
            self.error_label.text = '\n'.join(errors)
        else:
            self.error_label.text = ''
            # Save settings to config_manager
            if self.config_manager is not None:
                self.config_manager.update(settings)
            if self.on_save:
                self.on_save(settings)
            self.unsaved_changes = False
            self.main_window.info_dialog('Settings Saved', 'Settings have been saved successfully.')

    def collect_settings(self):
        # Collect settings from all controls in all tabs
        # General
        settings = {}
        settings['interval_sec'] = int(self.interval_input.value)
        settings['launch_at_login'] = bool(self.launch_at_login.value)
        settings['auto_update'] = bool(self.auto_update.value)
        settings['log_level'] = self.log_level.value
        # Targets
        targets = []
        for row in self.target_table.data:
            address, name = row
            targets.append({'address': address, 'name': name, 'protocol': 'ICMP', 'port': 0, 'timeout': 5.0, 'tags': []})
        settings['targets'] = targets
        # Alerts
        settings['alerts'] = {
            'enabled': bool(self.enable_alerts.value),
            'downtime': {
                'enabled': bool(self.alert_on_downtime.value),
                'minutes': int(self.downtime_threshold.value)
            },
            'latency': {
                'enabled': bool(self.alert_on_latency.value),
                'ms': int(self.latency_threshold.value)
            },
            'packet_loss': {
                'enabled': bool(self.alert_on_loss.value),
                'percent': int(self.loss_threshold.value)
            },
            'sound': bool(self.notif_sound.value),
            'badge': bool(self.notif_badge.value),
            'notification_center': bool(self.notif_center.value),
            'cooldown_minutes': int(self.alert_cooldown.value)
        }
        # Display
        settings['display'] = {
            'menubar_style': self.menubar_style.value,
            'icon_style': self.icon_style.value,
            'default_timeframe': self.default_timeframe.value,
            'chart_type': self.chart_type.value,
            'show_grid': bool(self.show_grid.value),
            'animate_charts': bool(self.animate_charts.value),
            'theme': self.theme.value
        }
        # Advanced
        settings['database'] = {
            'engine': self.db_engine.value,
            'retention_days': int(self.data_retention.value)
        }
        settings['performance'] = {
            'max_workers': int(self.max_workers.value),
            'batch_writes': bool(self.batch_writes.value)
        }
        settings['network'] = {
            'ipv6': bool(self.ipv6_enabled.value),
            'dns_resolver': self.dns_resolver.value
        }
        return settings 