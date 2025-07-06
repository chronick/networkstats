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
- [Network Monitoring](docs/spec/network-monitoring/index.md) - Monitoring engine and native Python ping implementation
- [Database](docs/spec/database/index.md) - SQLite/DuckDB storage architecture
- [Menu Bar](docs/spec/menubar/index.md) - macOS menu bar application design
- [Settings GUI](docs/spec/settings-gui/index.md) - Configuration interface specification
- [Statistics & Visualization](docs/spec/statistics-visualization/index.md) - Data visualization and analytics
- [Packaging & Deployment](docs/spec/packaging-deployment/index.md) - Build, sign, and distribute

---

## Phase 2 Features

NetworkStats now includes the following advanced features:

### Native Python Ping (ICMP)
- Uses a native Python implementation for ICMP ping, improving cross-platform compatibility and performance.
- See [Network Monitoring Spec](docs/spec/network-monitoring/index.md) for details.

### Settings GUI
- User-friendly interface for configuring all aspects of the app.
- Tabs include:
  - **General**: Monitoring interval, launch at login, auto-update, log level.
  - **Targets**: Add/edit/remove network targets, quick add, advanced options.
  - **Alerts**: Enable/disable alerts, set thresholds for downtime, latency, packet loss, notification preferences, cooldowns.
  - **Display**: Menu bar style, icon style, default timeframe, chart type, grid lines, animation, theme.
  - **Advanced**: Database engine, data retention, performance (max workers, batch writes), network (IPv6, DNS), export/import/reset.
- All settings are validated before saving. See [Settings GUI Spec](docs/spec/settings-gui/index.md) and [Tab Specifications](docs/spec/settings-gui/tab-specifications.md).

#### How to Use the Settings GUI
- Open the Settings window from the menu bar or main app.
- Navigate tabs to adjust settings.
- Invalid settings will be highlighted and cannot be saved until fixed.
- Settings are persisted to `~/.config/networkstats/settings.toml`.

### Alert System
- Configurable alerts for downtime, high latency, and packet loss.
- Notification options: sound, badge, Notification Center.
- Adjustable thresholds and cooldowns.
- Alerts can be toggled on/off per condition.
- See [Settings GUI Spec](docs/spec/settings-gui/index.md) and [Network Monitoring Spec](docs/spec/network-monitoring/index.md).

#### How to Use Alerts
- Configure alert thresholds and notification preferences in the Settings GUI (Alerts tab).
- Alerts will appear as system notifications and/or badges when triggered.

### Enhanced Visualizations
- Interactive charts: Uptime, Latency, Packet Loss, Anomaly, Timeline, Heatmap, Combined metrics.
- Summary cards for Uptime and Latency.
- Drill-down: Click on chart points for detailed views.
- Real-time updates (auto-refresh).
- Export data and charts as PDF, PNG, CSV, Excel, or JSON.
- See [Statistics Visualization Spec](docs/spec/statistics-visualization/index.md).

#### How to Use Visualizations
- Open the statistics window from the menu bar or main app.
- Select chart type, time range, and metrics.
- Use the export button to save data or charts.
- Click on chart points for drill-down analysis.

---

For more details, see the full product specifications in the `docs/spec/` directory.
