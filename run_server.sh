#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=${PORT:-5000}

echo "==> Updating package list..."
sudo apt-get update -y

echo "==> Installing Python3, pip, and virtualenv..."
sudo apt-get install -y python3 python3-pip python3-venv

echo "==> Creating virtual environment..."
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo "==> Initialising database..."
python3 -c "from app import init_db; init_db()"

echo "==> Starting server on port $PORT..."
exec gunicorn --bind "0.0.0.0:$PORT" --workers 2 app:app
