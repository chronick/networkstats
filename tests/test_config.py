from networkstats import config

def test_load_creates_default(tmp_path, monkeypatch):
    cfg_file = tmp_path / "settings.toml"
    monkeypatch.setattr(config, "CFG_FILE", cfg_file)
    # Remove if exists
    if cfg_file.exists():
        cfg_file.unlink()
    data = config.load()
    assert data == config.DEFAULT
    assert cfg_file.exists()


def test_save_and_load(tmp_path, monkeypatch):
    cfg_file = tmp_path / "settings.toml"
    monkeypatch.setattr(config, "CFG_FILE", cfg_file)
    test_data = {
        "targets": ["1.2.3.4"],
        "interval_sec": 10,
        "sqlite_path": "/tmp/test.db",
    }
    config.save(test_data)
    loaded = config.load()
    assert loaded == test_data
