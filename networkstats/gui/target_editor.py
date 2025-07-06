import toga
from toga.style import Pack
from toga.style.pack import COLUMN

class TargetEditor(toga.Window):
    def __init__(self, target=None, on_save=None):
        super().__init__(title='Edit Target' if target else 'Add Target', size=(400, 300))
        self.target = target or {}
        self.on_save = on_save
        form_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        self.address_input = toga.TextInput(
            value=self.target.get('address', ''),
            placeholder='e.g., 8.8.8.8 or google.com',
            style=Pack(width=300, margin=5)
        )
        self.name_input = toga.TextInput(
            value=self.target.get('name', ''),
            placeholder='e.g., Google DNS',
            style=Pack(width=300, margin=5)
        )
        self.protocol_selection = toga.Selection(
            items=['ICMP', 'TCP', 'UDP', 'HTTP', 'HTTPS'],
            value=self.target.get('protocol', 'ICMP'),
            style=Pack(width=100)
        )
        self.port_input = toga.NumberInput(
            value=self.target.get('port', 0),
            min=0,
            max=65535,
            step=1,
            style=Pack(width=100)
        )
        self.timeout_input = toga.NumberInput(
            value=self.target.get('timeout', 5.0),
            min=0.1,
            max=60.0,
            step=0.1,
            style=Pack(width=100)
        )
        self.tags_input = toga.TextInput(
            value=', '.join(self.target.get('tags', [])),
            placeholder='e.g., primary, dns, critical',
            style=Pack(width=300)
        )
        form_box.add(self._create_field('Address:', self.address_input))
        form_box.add(self._create_field('Display Name:', self.name_input))
        form_box.add(toga.Divider())
        form_box.add(toga.Label('Advanced Options:', style=Pack(margin_top=10)))
        form_box.add(self._create_field('Protocol:', self.protocol_selection))
        form_box.add(self._create_field('Port:', self.port_input))
        form_box.add(self._create_field('Timeout (s):', self.timeout_input))
        form_box.add(self._create_field('Tags:', self.tags_input))
        button_box = toga.Box(style=Pack(direction="row", margin=10))
        save_btn = toga.Button('Save', on_press=self._on_save, style=Pack(width=100))
        cancel_btn = toga.Button('Cancel', on_press=self._on_cancel, style=Pack(width=100))
        button_box.add(save_btn)
        button_box.add(cancel_btn)
        main_box = toga.Box(children=[form_box, button_box], style=Pack(direction=COLUMN))
        self.content = main_box

    def _create_field(self, label, widget):
        row = toga.Box(style=Pack(direction="row", margin=2))
        row.add(toga.Label(label, style=Pack(width=120)))
        row.add(widget)
        return row

    def _on_save(self, widget):
        target = {
            'address': self.address_input.value.strip(),
            'name': self.name_input.value.strip(),
            'protocol': self.protocol_selection.value,
            'port': int(self.port_input.value),
            'timeout': float(self.timeout_input.value),
            'tags': [t.strip() for t in self.tags_input.value.split(',') if t.strip()]
        }
        if self.on_save:
            self.on_save(target)
        self.close()

    def _on_cancel(self, widget):
        self.close() 