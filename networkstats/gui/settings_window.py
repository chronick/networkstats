import rumps
from .target_editor import TargetEditor

class SettingsApp(rumps.App):
    """A rumps-based menu bar app for NetworkStats settings."""
    def __init__(self, config_manager=None, on_save=None):
        super(SettingsApp, self).__init__("NetworkStats Settings")
        self.config_manager = config_manager or {}
        self.on_save = on_save
        self.menu = [
            rumps.MenuItem("General", callback=self.open_general),
            rumps.MenuItem("Targets", callback=self.open_targets),
            rumps.MenuItem("Alerts", callback=self.open_alerts),
            rumps.MenuItem("Display", callback=self.open_display),
            rumps.MenuItem("Advanced", callback=self.open_advanced),
            None,
            rumps.MenuItem("Save Settings", callback=self.save_settings),
        ]
        self.unsaved_changes = False

    def open_general(self, _):
        interval = self.config_manager.get('interval_sec', 30)
        launch = self.config_manager.get('launch_at_login', False)
        auto_update = self.config_manager.get('auto_update', True)
        log_level = self.config_manager.get('log_level', 'WARNING')
        # Interval
        resp = rumps.Window(
            "Check interval (seconds):",
            default_text=str(interval),
            ok="Save",
            cancel="Cancel"
        ).run()
        if resp.clicked:
            try:
                val = int(resp.text.strip())
                if 5 <= val <= 3600:
                    self.config_manager['interval_sec'] = val
                    self.unsaved_changes = True
                else:
                    rumps.alert("Interval must be 5-3600 seconds.")
            except Exception:
                rumps.alert("Invalid interval.")
        # Launch at login
        launch_val = rumps.alert("Launch at login?", ok="Yes", cancel="No")
        self.config_manager['launch_at_login'] = (launch_val == 1)
        # Auto update
        auto_val = rumps.alert("Check for updates automatically?", ok="Yes", cancel="No")
        self.config_manager['auto_update'] = (auto_val == 1)
        # Log level
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        log_idx = rumps.Window(
            "Log level (0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR, 4=CRITICAL):",
            default_text=str(log_levels.index(log_level)),
            ok="Save",
            cancel="Cancel"
        ).run()
        if log_idx.clicked:
            try:
                idx = int(log_idx.text.strip())
                if 0 <= idx < len(log_levels):
                    self.config_manager['log_level'] = log_levels[idx]
                    self.unsaved_changes = True
                else:
                    rumps.alert("Invalid log level.")
            except Exception:
                rumps.alert("Invalid log level.")

    def open_targets(self, _):
        # List targets and allow add/edit/remove
        targets = self.config_manager.get('targets', [])
        menu_items = [f"{i+1}. {t['address']} ({t.get('name','')})" for i, t in enumerate(targets)]
        menu_items.append("Add Target")
        menu_items.append("Remove Target")
        resp = rumps.Window(
            "Targets:\n" + '\n'.join(menu_items) + "\n\nEnter number to edit, 'a' to add, 'r' to remove:",
            default_text="",
            ok="OK",
            cancel="Cancel"
        ).run()
        if not resp.clicked:
            return
        val = resp.text.strip().lower()
        if val == 'a':
            def on_save(new_target):
                targets.append(new_target)
                self.config_manager['targets'] = targets
                self.unsaved_changes = True
            TargetEditor(target=None, on_save=on_save).show()
        elif val == 'r':
            idx_resp = rumps.Window("Enter number of target to remove:", default_text="", ok="Remove", cancel="Cancel").run()
            if idx_resp.clicked:
                try:
                    idx = int(idx_resp.text.strip()) - 1
                    if 0 <= idx < len(targets):
                        del targets[idx]
                        self.config_manager['targets'] = targets
                        self.unsaved_changes = True
                    else:
                        rumps.alert("Invalid target number.")
                except Exception:
                    rumps.alert("Invalid input.")
        else:
            try:
                idx = int(val) - 1
                if 0 <= idx < len(targets):
                    def on_save(updated_target):
                        targets[idx] = updated_target
                        self.config_manager['targets'] = targets
                        self.unsaved_changes = True
                    TargetEditor(target=targets[idx], on_save=on_save).show()
                else:
                    rumps.alert("Invalid target number.")
            except Exception:
                rumps.alert("Invalid input.")

    def open_alerts(self, _):
        alerts = self.config_manager.get('alerts', {})
        enabled = alerts.get('enabled', True)
        downtime = alerts.get('downtime', {'enabled': True, 'minutes': 5})
        latency = alerts.get('latency', {'enabled': True, 'ms': 100})
        packet_loss = alerts.get('packet_loss', {'enabled': False, 'percent': 10})
        sound = alerts.get('sound', True)
        badge = alerts.get('badge', True)
        notif_center = alerts.get('notification_center', True)
        cooldown = alerts.get('cooldown_minutes', 15)
        # Enable alerts
        enabled_val = rumps.alert("Enable alerts?", ok="Yes", cancel="No")
        alerts['enabled'] = (enabled_val == 1)
        # Downtime
        downtime_val = rumps.Window("Downtime threshold (minutes):", default_text=str(downtime.get('minutes', 5)), ok="Save", cancel="Cancel").run()
        if downtime_val.clicked:
            try:
                downtime['minutes'] = int(downtime_val.text.strip())
                downtime['enabled'] = True
            except Exception:
                rumps.alert("Invalid downtime value.")
        # Latency
        latency_val = rumps.Window("Latency threshold (ms):", default_text=str(latency.get('ms', 100)), ok="Save", cancel="Cancel").run()
        if latency_val.clicked:
            try:
                latency['ms'] = int(latency_val.text.strip())
                latency['enabled'] = True
            except Exception:
                rumps.alert("Invalid latency value.")
        # Packet loss
        loss_val = rumps.Window("Packet loss threshold (%):", default_text=str(packet_loss.get('percent', 10)), ok="Save", cancel="Cancel").run()
        if loss_val.clicked:
            try:
                packet_loss['percent'] = int(loss_val.text.strip())
                packet_loss['enabled'] = True
            except Exception:
                rumps.alert("Invalid packet loss value.")
        # Sound
        sound_val = rumps.alert("Play sound for alerts?", ok="Yes", cancel="No")
        alerts['sound'] = (sound_val == 1)
        # Badge
        badge_val = rumps.alert("Show badge on menu bar icon?", ok="Yes", cancel="No")
        alerts['badge'] = (badge_val == 1)
        # Notification Center
        notif_val = rumps.alert("Show in Notification Center?", ok="Yes", cancel="No")
        alerts['notification_center'] = (notif_val == 1)
        # Cooldown
        cooldown_val = rumps.Window("Alert cooldown (minutes):", default_text=str(cooldown), ok="Save", cancel="Cancel").run()
        if cooldown_val.clicked:
            try:
                alerts['cooldown_minutes'] = int(cooldown_val.text.strip())
            except Exception:
                rumps.alert("Invalid cooldown value.")
        alerts['downtime'] = downtime
        alerts['latency'] = latency
        alerts['packet_loss'] = packet_loss
        self.config_manager['alerts'] = alerts
        self.unsaved_changes = True

    def open_display(self, _):
        display = self.config_manager.get('display', {})
        menubar_styles = ['Icon only', 'Icon + Status', 'Icon + Uptime %', 'Icon + Latency', 'Text only']
        icon_styles = ['Emoji (🌐 🟢 🟡 🔴)', 'Classic (monochrome)', 'Modern (colored)', 'Minimal (dots)']
        timeframes = ['Last hour', '24 hours', '7 days', '30 days']
        chart_types = ['Bar chart', 'Line chart', 'Area chart', 'Heatmap']
        # Menubar style
        menubar_idx = rumps.Window("Menubar style (0-4):\n" + '\n'.join(f"{i}: {s}" for i, s in enumerate(menubar_styles)), default_text=str(menubar_styles.index(display.get('menubar_style', 'Icon only'))), ok="Save", cancel="Cancel").run()
        if menubar_idx.clicked:
            try:
                idx = int(menubar_idx.text.strip())
                display['menubar_style'] = menubar_styles[idx]
            except Exception:
                rumps.alert("Invalid menubar style.")
        # Icon style
        icon_idx = rumps.Window("Icon style (0-3):\n" + '\n'.join(f"{i}: {s}" for i, s in enumerate(icon_styles)), default_text=str(icon_styles.index(display.get('icon_style', icon_styles[0]))), ok="Save", cancel="Cancel").run()
        if icon_idx.clicked:
            try:
                idx = int(icon_idx.text.strip())
                display['icon_style'] = icon_styles[idx]
            except Exception:
                rumps.alert("Invalid icon style.")
        # Timeframe
        tf_idx = rumps.Window("Default timeframe (0-3):\n" + '\n'.join(f"{i}: {s}" for i, s in enumerate(timeframes)), default_text=str(timeframes.index(display.get('default_timeframe', '24 hours'))), ok="Save", cancel="Cancel").run()
        if tf_idx.clicked:
            try:
                idx = int(tf_idx.text.strip())
                display['default_timeframe'] = timeframes[idx]
            except Exception:
                rumps.alert("Invalid timeframe.")
        # Chart type
        chart_idx = rumps.Window("Chart type (0-3):\n" + '\n'.join(f"{i}: {s}" for i, s in enumerate(chart_types)), default_text=str(chart_types.index(display.get('chart_type', 'Bar chart'))), ok="Save", cancel="Cancel").run()
        if chart_idx.clicked:
            try:
                idx = int(chart_idx.text.strip())
                display['chart_type'] = chart_types[idx]
            except Exception:
                rumps.alert("Invalid chart type.")
        # Show grid
        grid_val = rumps.alert("Show grid lines?", ok="Yes", cancel="No")
        display['show_grid'] = (grid_val == 1)
        # Animate charts
        anim_val = rumps.alert("Animate chart transitions?", ok="Yes", cancel="No")
        display['animate_charts'] = (anim_val == 1)
        # Theme
        themes = ['System', 'Light', 'Dark']
        theme_idx = rumps.Window("Theme (0-2):\n" + '\n'.join(f"{i}: {s}" for i, s in enumerate(themes)), default_text=str(themes.index(display.get('theme', 'System'))), ok="Save", cancel="Cancel").run()
        if theme_idx.clicked:
            try:
                idx = int(theme_idx.text.strip())
                display['theme'] = themes[idx]
            except Exception:
                rumps.alert("Invalid theme.")
        self.config_manager['display'] = display
        self.unsaved_changes = True

    def open_advanced(self, _):
        database = self.config_manager.get('database', {})
        performance = self.config_manager.get('performance', {})
        network = self.config_manager.get('network', {})
        # Database engine
        engines = ['SQLite', 'DuckDB']
        eng_idx = rumps.Window("Database engine (0=SQLite, 1=DuckDB):", default_text=str(engines.index(database.get('engine', 'SQLite'))), ok="Save", cancel="Cancel").run()
        if eng_idx.clicked:
            try:
                idx = int(eng_idx.text.strip())
                database['engine'] = engines[idx]
            except Exception:
                rumps.alert("Invalid engine.")
        # Retention days
        ret_val = rumps.Window("Data retention (days):", default_text=str(database.get('retention_days', 30)), ok="Save", cancel="Cancel").run()
        if ret_val.clicked:
            try:
                database['retention_days'] = int(ret_val.text.strip())
            except Exception:
                rumps.alert("Invalid retention value.")
        # Max workers
        maxw_val = rumps.Window("Max workers:", default_text=str(performance.get('max_workers', 10)), ok="Save", cancel="Cancel").run()
        if maxw_val.clicked:
            try:
                performance['max_workers'] = int(maxw_val.text.strip())
            except Exception:
                rumps.alert("Invalid max workers.")
        # Batch writes
        batch_val = rumps.alert("Enable batch database writes?", ok="Yes", cancel="No")
        performance['batch_writes'] = (batch_val == 1)
        # IPv6
        ipv6_val = rumps.alert("Enable IPv6?", ok="Yes", cancel="No")
        network['ipv6'] = (ipv6_val == 1)
        # DNS resolver
        resolvers = ['System', 'Google (8.8.8.8)', 'Cloudflare (1.1.1.1)', 'Custom']
        dns_idx = rumps.Window("DNS resolver (0-3):\n" + '\n'.join(f"{i}: {s}" for i, s in enumerate(resolvers)), default_text=str(resolvers.index(network.get('dns_resolver', 'System'))), ok="Save", cancel="Cancel").run()
        if dns_idx.clicked:
            try:
                idx = int(dns_idx.text.strip())
                network['dns_resolver'] = resolvers[idx]
            except Exception:
                rumps.alert("Invalid resolver.")
        self.config_manager['database'] = database
        self.config_manager['performance'] = performance
        self.config_manager['network'] = network
        self.unsaved_changes = True

    def save_settings(self, _):
        # Optionally validate here
        if self.on_save:
            self.on_save(self.config_manager)
        self.unsaved_changes = False
        rumps.notification("Settings Saved", "NetworkStats", "Settings have been saved.") 