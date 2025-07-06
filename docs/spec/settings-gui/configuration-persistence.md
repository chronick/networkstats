# Settings GUI Specification: Configuration Persistence
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
