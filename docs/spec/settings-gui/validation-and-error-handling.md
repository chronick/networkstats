# Settings GUI Specification: Validation and Error Handling



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
