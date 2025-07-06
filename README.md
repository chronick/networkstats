# Network Stats

A network uptime monitor CLI and GUI app.

## Setup

Install dependencies:

```bash
poetry install
```

## Running the App

### CLI Mode

To run the CLI app:

```bash
poetry run networkstats run [OPTIONS]
```

**Options:**
- `--log-level [LEVEL]`  Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: WARNING
- `-v`, `--verbose`      Pass -v to ping for verbose output (overrides log level mapping)
- `-q`, `--quiet`        Pass -q to ping for quiet output (overrides log level mapping)
- `--ping-args [ARGS]`   Extra arguments to pass to ping (as a single string)

**Example:**
```bash
poetry run networkstats run --log-level INFO -v --ping-args "-c 3"
```

### GUI Mode (macOS Menu Bar)

To run the GUI menu bar app (macOS only):

```bash
scripts/build_app.sh        # Build the .app for your architecture
open dist/NetworkStats.app  # Launches the menu bar app
```

## Running Tests

```bash
poetry run pytest
```

## Adding Dependencies

```bash
poetry add <package>
```

## Development

- Use `poetry shell` to activate the virtual environment.
- Use `poetry add` and `poetry remove` to manage dependencies.
- Use `poetry update` to update dependencies.

## Notes

- This project uses [Poetry](https://python-poetry.org/) for dependency and environment management.
- Do not use `pip` or `uv` for dependency management.

## Quick start

```bash
git clone https://github.com/you/net-uptime-app
cd net-uptime-app
poetry install

# CLI mode
poetry run networkstats run

# GUI mode (macOS only)
scripts/build_app.sh
open dist/NetworkStats.app
```

Settings live at ~/.config/networkstats/settings.toml.

## Packaging

Merge → tag → draft release → publish → Intel & Silicon binaries land on Releases automatically.

## Documentation

Comprehensive product specifications are available in the `docs/spec/` directory:

- [Product Overview](docs/spec/index.md) - High-level product specification
- [Network Monitoring](docs/spec/network-monitoring.md) - Monitoring engine and native Python ping implementation
- [Database](docs/spec/database.md) - SQLite/DuckDB storage architecture
- [Menu Bar](docs/spec/menubar.md) - macOS menu bar application design
- [Settings GUI](docs/spec/settings-gui.md) - Configuration interface specification
- [Statistics & Visualization](docs/spec/statistics-visualization.md) - Data visualization and analytics
- [Packaging & Deployment](docs/spec/packaging-deployment.md) - Build, sign, and distribute

---

### Next steps

* 🔧 Flesh out the TODOs (alerting, UI polish, installer DMG).  
* 🧩 Swap SQLite for **DuckDB** with the `motherduck` extension if you want super-fast queries.  
* 📊 Replace Plotly with **Altair/Vega-Lite** if you prefer pure JSON spec charts.

Happy hacking — and enjoy seamless dev in Cursor!

## Enhanced Statistics & Visualization (Phase 2)

NetworkStats now includes advanced visualizations and analytics:

- **Chart Types:**
  - Uptime (bar, line, area)
  - Latency (percentiles, min/max, trend)
  - Timeline (up/down events)
  - Heatmap (hour/day patterns)
  - Anomaly Detection (outlier highlighting)
- **Summary Cards:**
  - Uptime and Latency at a glance
- **Export:**
  - PDF, PNG, CSV, Excel, JSON
- **Interactive Features:**
  - Drill-down to detail views
  - Real-time updates (auto-refresh)
- **How to Use:**
  - Select chart type and time range in the statistics window
  - Use export button to save data or charts
  - Click on chart points for detailed analysis

See [docs/spec/statistics-visualization/index.md](docs/spec/statistics-visualization/index.md) for full details.
