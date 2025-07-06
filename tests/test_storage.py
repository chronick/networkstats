import pytest
import polars as pl
from networkstats import storage
from networkstats import config as config_mod
import pathlib


def test_record_and_fetch_dataframe(tmp_path, monkeypatch):
    # Patch DB path to temp
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(storage, "DB", db_path)
    # Re-init connection
    storage.CONN = storage._conn()
    # Record a ping
    storage.record("8.8.8.8", 42.0, True)
    df = storage.fetch_dataframe(60)
    assert isinstance(df, pl.DataFrame)
    assert not df.is_empty()
    assert df["target"].to_list() == ["8.8.8.8"]
    assert df["latency_ms"].to_list() == [42.0]
    assert df["success"].to_list() == [1]
