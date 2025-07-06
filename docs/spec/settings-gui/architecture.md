# Settings GUI Specification: Architecture

## Window Structure
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
