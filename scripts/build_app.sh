#!/usr/bin/env bash
# Usage: scripts/build_app.sh [arm64|x86_64]
set -e
ARCH="${1:-$(uname -m)}"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt py2app
python setup.py py2app
echo "Built dist/NetworkStats.app for $ARCH" 