#!/bin/bash
set -e
source "$(dirname "$0")/shared.env"

echo "🔧 Initializing base_lib"
cd "$BASE_LIB_PATH"

python$PYTHON_VER -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

