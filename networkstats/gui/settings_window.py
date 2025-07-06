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

    def startup(self):
        self.main_window = toga.MainWindow(title='NetworkStats Settings')
        self.tabs = toga.OptionContainer(
            content=[
                ('General', self.create_general_tab()),
                ('Targets', self.create_targets_tab()),
                ('Alerts', self.create_alerts_tab()),
                ('Display', toga.Label('Display options (coming soon)')),
                ('Advanced', toga.Label('Advanced settings (coming soon)')),
            ],
            style=Pack(flex=1)
        )
        main_box = toga.Box(children=[self.tabs], style=Pack(direction=COLUMN, margin=10))
        self.main_window.content = main_box
        self.main_window.show() 