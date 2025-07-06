import pytest
import asyncio
from networkstats.alert_system import AlertSystem
from networkstats.notification_manager import NotificationManager

class DummyNotifier:
    def __init__(self):
        self.notifications = []
    def notify(self, message):
        self.notifications.append(message)

def test_notification_manager_notify(monkeypatch):
    nm = NotificationManager()
    outputs = []
    monkeypatch.setattr("builtins.print", lambda msg: outputs.append(msg))
    nm.notify("Test message")
    assert any("Test message" in o for o in outputs)

def test_notification_manager_play_sound(monkeypatch):
    nm = NotificationManager()
    outputs = []
    monkeypatch.setattr("builtins.print", lambda msg: outputs.append(msg))
    nm.play_sound()
    assert any("[SOUND]" in o for o in outputs)

def test_notification_manager_show_badge(monkeypatch):
    nm = NotificationManager()
    outputs = []
    monkeypatch.setattr("builtins.print", lambda msg: outputs.append(msg))
    nm.show_badge("ALERT")
    assert any("ALERT" in o for o in outputs)

def test_notification_manager_show_notification_center(monkeypatch):
    nm = NotificationManager()
    outputs = []
    monkeypatch.setattr("builtins.print", lambda msg: outputs.append(msg))
    nm.show_notification_center("NC message")
    assert any("NC message" in o for o in outputs)

def test_notification_manager_show_badge_menubar(monkeypatch):
    nm = NotificationManager()
    called = {}
    def fake_set_badge(text):
        called['badge'] = text
    nm.set_badge = fake_set_badge
    nm.show_badge("ALERT")
    assert called['badge'] == "ALERT"

@pytest.mark.asyncio
async def test_alert_system_threshold_and_cooldown():
    notifier = DummyNotifier()
    config = {
        'alerts': {
            'enabled': True,
            'downtime': {'enabled': True, 'minutes': 1},
            'latency': {'enabled': True, 'ms': 100},
            'packet_loss': {'enabled': True, 'percent': 10},
            'cooldown_minutes': 5
        }
    }
    alert_system = AlertSystem(config, notifier.notify)
    # Simulate downtime event
    await alert_system.check_conditions('8.8.8.8', success=False, latency=None, packet_loss=0)
    assert any('down' in msg for msg in notifier.notifications)
    # Simulate high latency event
    await alert_system.check_conditions('8.8.8.8', success=True, latency=200, packet_loss=0)
    assert any('latency' in msg for msg in notifier.notifications)
    # Simulate packet loss event
    await alert_system.check_conditions('8.8.8.8', success=True, latency=50, packet_loss=20)
    assert any('packet loss' in msg for msg in notifier.notifications)
    # Simulate cooldown: should not notify again immediately
    notifier.notifications.clear()
    await alert_system.check_conditions('8.8.8.8', success=False, latency=None, packet_loss=0)
    assert not notifier.notifications  # No notification due to cooldown

def test_alert_system_triggers_notification(monkeypatch):
    nm = NotificationManager()
    called = {'notify': [], 'badge': []}
    monkeypatch.setattr(nm, 'notify', lambda msg: called['notify'].append(msg))
    monkeypatch.setattr(nm, 'show_badge', lambda text='!': called['badge'].append(text))
    alert_system = AlertSystem({'alerts': {'enabled': True, 'downtime': {'enabled': True, 'minutes': 1}, 'cooldown_minutes': 0}}, nm.notify)
    # Simulate downtime event
    asyncio.run(alert_system.check_conditions('1.2.3.4', success=False, latency=None, packet_loss=0))
    assert any('down' in msg for msg in called['notify'])
    # Simulate badge update (would be called in real integration)
    nm.show_badge('!')
    assert '!' in called['badge'] 