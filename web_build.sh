#!/usr/bin/env bash
set -e

echo "Detecting Python..."
which python || echo "Python not found!"

echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput || true

echo "Skipping collectstatic..."