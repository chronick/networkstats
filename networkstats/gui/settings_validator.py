import re
import socket
from typing import List, Dict

class SettingsValidator:
    """Validate settings input."""

    @staticmethod
    def validate_target(address: str) -> tuple[bool, str]:
        """Validate target address."""
        # IP address pattern
        ip_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        # Hostname pattern
        hostname_pattern = re.compile(
            r'^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)'\
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
    def validate_settings(settings: Dict) -> List[str]:
        """Validate all settings, return list of errors."""
        errors = []
        # Validate interval
        if settings.get('interval_sec', 30) < 5:
            errors.append("Check interval must be at least 5 seconds")
        # Validate targets
        if not settings.get('targets'):
            errors.append("At least one target must be configured")
        # Validate alert thresholds
        alerts = settings.get('alerts', {})
        downtime = alerts.get('downtime', {})
        if downtime.get('minutes', 5) < 1:
            errors.append("Downtime threshold must be at least 1 minute")
        # Display tab validations
        display = settings.get('display', {})
        if display.get('default_timeframe') not in ['Last hour', '24 hours', '7 days', '30 days']:
            errors.append("Default timeframe must be one of: Last hour, 24 hours, 7 days, 30 days")
        if display.get('chart_type') not in ['Bar chart', 'Line chart', 'Area chart', 'Heatmap']:
            errors.append("Chart type must be one of: Bar chart, Line chart, Area chart, Heatmap")
        if display.get('theme') not in ['System', 'Light', 'Dark']:
            errors.append("Theme must be one of: System, Light, Dark")
        if display.get('menubar_style') not in [
            'Icon only', 'Icon + Status', 'Icon + Uptime %', 'Icon + Latency', 'Text only']:
            errors.append("Menu bar style must be a valid option")
        if display.get('icon_style') not in [
            'Emoji (🌐 🟢 🟡 🔴)', 'Classic (monochrome)', 'Modern (colored)', 'Minimal (dots)']:
            errors.append("Icon style must be a valid option")
        # Advanced tab validations
        database = settings.get('database', {})
        if database.get('engine') not in ['SQLite', 'DuckDB']:
            errors.append("Database engine must be SQLite or DuckDB")
        if database.get('retention_days', 30) < 1:
            errors.append("Data retention must be at least 1 day")
        performance = settings.get('performance', {})
        if performance.get('max_workers', 10) < 1:
            errors.append("Max workers must be at least 1")
        network = settings.get('network', {})
        dns_resolver = network.get('dns_resolver', 'System')
        valid_dns = ['System', 'Google (8.8.8.8)', 'Cloudflare (1.1.1.1)', 'Custom']
        if dns_resolver not in valid_dns:
            # If custom, check if it's a valid IP
            if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', dns_resolver):
                errors.append("DNS resolver must be a valid option or a valid IP address")
        # No negative values for batch_writes, ipv6_enabled, etc. (should be bool)
        # No further validation needed for switches (assume bool)
        return errors 