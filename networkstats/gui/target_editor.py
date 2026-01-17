import rumps

class TargetEditor:
    """A modal dialog for adding or editing a network target using rumps."""
    def __init__(self, target=None, on_save=None):
        self.target = target or {}
        self.on_save = on_save

    def show(self):
        # Gather fields using rumps.Window (multi-field input)
        default_address = self.target.get('address', '')
        default_name = self.target.get('name', '')
        default_protocol = self.target.get('protocol', 'ICMP')
        default_port = str(self.target.get('port', 0))
        default_timeout = str(self.target.get('timeout', 5.0))
        default_tags = ', '.join(self.target.get('tags', []))

        # Compose a multi-line prompt for all fields
        prompt = (
            f"Address (e.g., 8.8.8.8 or google.com):\n{default_address}\n"
            f"Display Name (e.g., Google DNS):\n{default_name}\n"
            f"Protocol [ICMP/TCP/UDP/HTTP/HTTPS]:\n{default_protocol}\n"
            f"Port (0-65535):\n{default_port}\n"
            f"Timeout (seconds):\n{default_timeout}\n"
            f"Tags (comma separated):\n{default_tags}"
        )
        window = rumps.Window(
            message="Edit Target" if self.target else "Add Target",
            default_text=f"{default_address}\n{default_name}\n{default_protocol}\n{default_port}\n{default_timeout}\n{default_tags}",
            ok="Save",
            cancel="Cancel",
            dimensions=(400, 180)
        )
        window.title = "Edit Target" if self.target else "Add Target"
        window.message = prompt
        response = window.run()
        if response.clicked:
            values = response.text.split('\n')
            if len(values) < 6:
                rumps.alert("Please fill in all fields.")
                return
            address = values[0].strip()
            name = values[1].strip()
            protocol = values[2].strip().upper()
            port = int(values[3].strip() or 0)
            timeout = float(values[4].strip() or 5.0)
            tags = [t.strip() for t in values[5].split(',') if t.strip()]
            if not address:
                rumps.alert("Address is required.")
                return
            if protocol not in ['ICMP', 'TCP', 'UDP', 'HTTP', 'HTTPS']:
                rumps.alert("Invalid protocol.")
                return
            if not (0 <= port <= 65535):
                rumps.alert("Port must be between 0 and 65535.")
                return
            if not (0.1 <= timeout <= 60.0):
                rumps.alert("Timeout must be between 0.1 and 60 seconds.")
                return
            target = {
                'address': address,
                'name': name,
                'protocol': protocol,
                'port': port,
                'timeout': timeout,
                'tags': tags
            }
            if self.on_save:
                self.on_save(target) 