from setuptools import setup

APP = ["networkstats/menubar.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "iconfile": None,
    "packages": ["rumps", "toga", "polars", "plotly", "typer"],
}

setup(
    app=APP,
    name="NetworkStats",
    version="0.1.0",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
