# Statistics and Visualization Specification: Current Implementation

## Basic Statistics Window
```python
import toga
import plotly.express as px
import polars as pl

class StatsWindow(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title="Network Stats")
        
        # Time range selector
        self.timeframe = toga.Selection(
            items=[
                ("Last hour", 3600),
                ("24 hours", 86400),
                ("7 days", 604800),
            ]
        )
        
        # Chart container
        self.web = toga.WebView()
        
        # Refresh data and render
        self.refresh(None)

```
