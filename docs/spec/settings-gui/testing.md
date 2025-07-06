# Settings GUI Specification: Testing



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
