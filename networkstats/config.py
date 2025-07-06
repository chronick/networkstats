from pathlib import Path
import tomllib
import tomli_w

DEFAULT = {
    "targets": ["8.8.8.8", "1.1.1.1"],
    "interval_sec": 30,
    "sqlite_path": "~/Library/Application Support/NetworkStats/ping.db",
}

CFG_FILE = Path.home() / ".config" / "networkstats" / "settings.toml"


def load() -> dict:
    """Load settings from the config file, or create with defaults if missing."""
    if not CFG_FILE.exists():
        save(DEFAULT)
        return DEFAULT.copy()
    with CFG_FILE.open("rb") as f:
        return tomllib.load(f)


def save(data: dict) -> None:
    """Save settings to the config file."""
    CFG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CFG_FILE.write_bytes(tomli_w.dumps(data).encode())
