#!/usr/bin/env bash
# Usage: scripts/clean_build.sh
# Cleans build artifacts for a fresh build
set -e
[ -d build ] && rm -rf build
[ -d dist ] && rm -rf dist
[ -d .eggs ] && rm -rf .eggs
[ -d .pytest_cache ] && rm -rf .pytest_cache
[ -d .mypy_cache ] && rm -rf .mypy_cache
[ -d __pycache__ ] && rm -rf __pycache__
[ -f .DS_Store ] && rm -f .DS_Store
# Remove *.egg-info in root
for d in *.egg-info; do [ -e "$d" ] && rm -rf "$d"; done
# Recursively remove artifacts
find . -name '__pycache__' -type d -exec rm -rf {} +
find . -name '*.egg-info' -type d -exec rm -rf {} +
find . -name '.DS_Store' -type f -delete
find . -name '.pytest_cache' -type d -exec rm -rf {} +
find . -name '.mypy_cache' -type d -exec rm -rf {} + 