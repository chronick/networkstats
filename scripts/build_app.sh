#!/usr/bin/env bash
# Usage: scripts/build_app.sh [main_script.py] [AppName] [icon.icns]
set -e
# Clean previous build artifacts
scripts/clean_build.sh

MAIN_SCRIPT="${1:-main.py}"
APP_NAME="${2:-NetworkStats}"
ICON_ARG=""
if [[ -n "$3" ]]; then
  ICON_ARG="--icon=$3"
fi

# Install dependencies using Poetry
poetry install
# Ensure PyInstaller is installed
poetry run pip install pyinstaller
# Build the .app bundle using PyInstaller
poetry run pyinstaller --windowed --name "$APP_NAME" $ICON_ARG "$MAIN_SCRIPT"

if [[ -d "dist/$APP_NAME.app" ]]; then
  echo "Built dist/$APP_NAME.app successfully."
else
  echo "Failed to build .app bundle. Check PyInstaller output for errors."
  exit 1
fi 