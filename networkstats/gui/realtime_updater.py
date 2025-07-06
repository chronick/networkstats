import asyncio

class RealtimeUpdater:
    """Handle real-time chart updates using JavaScript injection."""
    def __init__(self, chart_container):
        self.chart_container = chart_container
        self.update_interval = 5  # seconds
        self.is_running = False
        self.data_source = None  # Should be set externally

    async def start_updates(self, run_once=False):
        """Start real-time updates. If run_once is True, only one update is performed (for testing)."""
        self.is_running = True
        while self.is_running:
            if self.data_source is None:
                break
            latest_data = await self.data_source.get_latest_data()
            update_script = f"""
                Plotly.extendTraces('chart', {{
                    x: [[{latest_data['timestamps']}]],
                    y: [[{latest_data['values']}]]
                }}, [0]);
                Plotly.relayout('chart', {{
                    'xaxis.range': [
                        new Date(Date.now() - 3600000),
                        new Date()
                    ]
                }});
            """
            await self.chart_container.evaluate_javascript(update_script)
            if run_once:
                break
            await asyncio.sleep(self.update_interval) 