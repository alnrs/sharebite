#!/bin/sh
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then exec python3 tools/run_local.py; fi
if command -v python >/dev/null 2>&1; then exec python tools/run_local.py; fi
echo 'Install Python 3 or open the extracted folder with VS Code Live Server.'
