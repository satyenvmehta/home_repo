#!/bin/bash
set -e

# Load shared paths (optional)
source scripts/shared.env

echo "🌱 Creating virtual environment..."

#PYTHON_BIN=$(command -v python3.10 || command -v python3.11 || command -v python3.12 || command -v python3)
#$PYTHON_BIN -m venv .venv

#python3.10 -m venv .venv

py.exe -3.10 -m venv .venv

source .venv/bin/activate

echo "⬆️  Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing base_lib in editable mode..."
pip install -e base_lib

echo "📦 Installing tp requirements..."
pip install -r tp/requirements.txt

echo "✅ All setup complete!"

