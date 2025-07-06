import toga
from toga.style import Pack
from toga.style.pack import COLUMN

class SummaryCard:
    """Reusable summary statistic card for network metrics."""
    def __init__(self, title: str, metric_type: str):
        self.title = title
        self.metric_type = metric_type
        self.current_value = None
        self.previous_value = None

    def format_value(self, value):
        if value is None:
            return "--"
        if self.metric_type == 'percentage':
            return f"{value:.2f}%"
        elif self.metric_type == 'ms':
            return f"{value:.1f} ms"
        else:
            return str(value)

    def format_trend(self):
        if self.current_value is None or self.previous_value is None:
            return ""
        diff = self.current_value - self.previous_value
        if diff > 0:
            return f"↑ {abs(diff):.2f} from prev"
        elif diff < 0:
            return f"↓ {abs(diff):.2f} from prev"
        else:
            return "No change"

    def create_widget(self) -> toga.Box:
        card = toga.Box(style=Pack(direction=COLUMN, margin=10, background_color='#f8f9fa', width=200, height=100))
        title_label = toga.Label(self.title, style=Pack(font_size=12, color='#6c757d'))
        self.value_label = toga.Label(self.format_value(self.current_value), style=Pack(font_size=24, font_weight='bold'))
        self.trend_label = toga.Label(self.format_trend(), style=Pack(font_size=10))
        card.add(title_label)
        card.add(self.value_label)
        card.add(self.trend_label)
        if self.metric_type == 'percentage':
            self.progress = toga.ProgressBar(max=100, value=self.current_value or 0, style=Pack(width=180, height=10))
            card.add(self.progress)
        return card

    def update(self, current: float, previous: float = None):
        self.current_value = current
        self.previous_value = previous
        self.value_label.text = self.format_value(current)
        self.trend_label.text = self.format_trend()
        if hasattr(self, 'progress'):
            self.progress.value = current 