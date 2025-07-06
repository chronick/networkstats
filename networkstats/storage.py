import sqlite3
import time
import pathlib
import polars as pl
from .config import load

cfg = load()
DB = pathlib.Path(cfg["sqlite_path"]).expanduser()
DB.parent.mkdir(parents=True, exist_ok=True)

DDL = """
CREATE TABLE IF NOT EXISTS pings (
  ts INTEGER NOT NULL,
  target TEXT NOT NULL,
  latency_ms REAL,
  success INTEGER,
  PRIMARY KEY (ts, target)
);
CREATE INDEX IF NOT EXISTS idx_target_ts ON pings(target, ts DESC);
"""


def _conn():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.executescript(DDL)
    return c


CONN = _conn()


def record(target: str, latency_ms: float, ok: bool) -> None:
    """Record a ping result in the database."""
    CONN.execute(
        "INSERT OR REPLACE INTO pings VALUES (?,?,?,?)",
        (int(time.time()), target, latency_ms, int(ok)),
    )
    CONN.commit()


def fetch_dataframe(since_sec: int) -> pl.DataFrame:
    """Return a Polars DF of pings within the last `since_sec` seconds."""
    t0 = int(time.time()) - since_sec
    query = f"SELECT ts, target, latency_ms, success FROM pings WHERE ts>={t0}"
    df = pl.read_database(
        query,
        connection=CONN,
    )
    return df.with_columns(pl.col("ts").cast(pl.Datetime).alias("datetime"))
