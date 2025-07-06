# Network Stats

A network uptime monitor CLI and GUI app.

## Setup

Install dependencies:

```bash
poetry install
```

## Running the App

To run the app:

```bash
poetry run python main.py
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
scripts/build_app.sh        # local .app for your arch
open dist/NetworkStats.app          # runs in menu bar

CLI mode:

netuptime run

Settings live at ~/.config/networkstats/settings.toml.
```

## Packaging

Merge → tag → draft release → publish → Intel & Silicon binaries land on Releases automatically.

---

### Next steps

* 🔧 Flesh out the TODOs (alerting, UI polish, installer DMG).  
* 🧩 Swap SQLite for **DuckDB** with the `motherduck` extension if you want super-fast queries.  
* 📊 Replace Plotly with **Altair/Vega-Lite** if you prefer pure JSON spec charts.

Happy hacking — and enjoy seamless dev in Cursor!
