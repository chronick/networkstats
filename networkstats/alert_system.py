import time
from collections import defaultdict

class AlertSystem:
    def __init__(self, config, notify_callback):
        self.config = config
        self.notify = notify_callback
        # Track last alert time per target and alert type
        self.last_alert_time = defaultdict(lambda: {'downtime': 0, 'latency': 0, 'packet_loss': 0})

    async def check_conditions(self, target, success, latency, packet_loss):
        alerts = self.config.get('alerts', {})
        if not alerts.get('enabled', True):
            return
        now = time.time()
        cooldown = alerts.get('cooldown_minutes', 5) * 60
        # Downtime
        downtime_cfg = alerts.get('downtime', {})
        if downtime_cfg.get('enabled', True) and not success:
            if now - self.last_alert_time[target]['downtime'] >= cooldown:
                self.notify(f"Target {target} is down")
                self.last_alert_time[target]['downtime'] = now
        # High latency
        latency_cfg = alerts.get('latency', {})
        if latency_cfg.get('enabled', True) and latency is not None:
            if latency > latency_cfg.get('ms', 100):
                if now - self.last_alert_time[target]['latency'] >= cooldown:
                    self.notify(f"Target {target} latency {latency}ms exceeds threshold")
                    self.last_alert_time[target]['latency'] = now
        # Packet loss
        loss_cfg = alerts.get('packet_loss', {})
        if loss_cfg.get('enabled', True):
            if packet_loss > loss_cfg.get('percent', 10):
                if now - self.last_alert_time[target]['packet_loss'] >= cooldown:
                    self.notify(f"Target {target} packet loss {packet_loss}% exceeds threshold")
                    self.last_alert_time[target]['packet_loss'] = now 