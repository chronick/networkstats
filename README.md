# Net-Uptime-App 📶

> Menu-bar utility that records ping latency & uptime, stores it in
> SQLite, crunches stats with **Polars**, and shows pretty charts in a
> **Toga** window.

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

## Development

- **Dependency management:** This project uses [uv](https://github.com/astral-sh/uv) for Python package management.
  - To install dependencies:
    ```bash
    uv pip install -r requirements.txt
    ```
  - To add a new dependency:
    ```bash
    uv pip install <package>
    ```
  - To create a new virtual environment:
    ```bash
    uv venv venv && source venv/bin/activate
    ```
- `cursor-rules.mdc` keeps commit style consistent.
- `pytest -q` runs unit tests.
- `black . && ruff . && mypy networkstats` before every PR.

> **Note:** `requirements.txt` is only used for py2app packaging. For all development, use `uv` and `pyproject.toml`.

## Packaging

Merge → tag → draft release → publish → Intel & Silicon binaries land on Releases automatically.

---

### Next steps

* 🔧 Flesh out the TODOs (alerting, UI polish, installer DMG).  
* 🧩 Swap SQLite for **DuckDB** with the `motherduck` extension if you want super-fast queries.  
* 📊 Replace Plotly with **Altair/Vega-Lite** if you prefer pure JSON spec charts.

Happy hacking — and enjoy seamless dev in Cursor!
