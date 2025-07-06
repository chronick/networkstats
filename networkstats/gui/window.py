import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import polars as pl
import plotly.express as px
from ..storage import fetch_dataframe


class StatsWindow(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title="Uptime Stats")
        self.timeframe = toga.Selection(
            items=[
                ("Last hour", 3600),
                ("24 hours", 86400),
                ("7 days", 604800),
            ]
        )
        self.timeframe.on_select = self.refresh
        self.web = toga.WebView()
        box = toga.Box(
            children=[self.timeframe, self.web], style=Pack(direction=COLUMN)
        )
        self.main_window.content = box
        self.refresh(None)
        self.main_window.show()

    def refresh(self, widget):
        span = self.timeframe.value or 3600
        df: pl.DataFrame = fetch_dataframe(span)
        if df.is_empty():
            html = "<h3>No data yet…</h3>"
        else:
            uptime = (
                df.groupby("target")
                .agg(pl.col("success").mean() * 100)
                .rename({"success": "uptime_pct"})
            )
            fig = px.bar(
                uptime.to_pandas(),
                x="target",
                y="uptime_pct",
                labels={"uptime_pct": "Uptime %"},
                title=f"Uptime over last {span//3600} h",
            )
            html = fig.to_html(include_plotlyjs="cdn")
        self.web.set_content(html, "text/html")
