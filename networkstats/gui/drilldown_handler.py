class DrillDownHandler:
    """Handle drill-down interactions for chart exploration and detail windows."""
    def __init__(self, stats_window):
        self.stats_window = stats_window

    def on_chart_click(self, event_data: dict):
        """Handle click events on charts."""
        point_data = event_data.get('points', [{}])[0]
        if 'customdata' in point_data:
            target = point_data['customdata']['target']
            timestamp = point_data['customdata']['timestamp']
            self.stats_window.show_detail_window(target, timestamp) 