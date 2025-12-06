#!/usr/bin/env bash
# Render startup script that ensures venv is activated

set -e

echo "Starting application..."
echo "Python location: $(which python)"
echo "Python version: $(python --version)"

# Find and activate the virtual environment
if [ -d "/opt/render/project/src/.venv" ]; then
    echo "Found venv at /opt/render/project/src/.venv"
    source /opt/render/project/src/.venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Found venv at .venv"
    source .venv/bin/activate
fi

echo "Activated Python: $(which python)"
echo "Checking for gunicorn..."
which gunicorn || echo "gunicorn not found in PATH"

# Start gunicorn
PORT=${PORT:-10000}
echo "Starting gunicorn on port $PORT..."
exec gunicorn pdf_analyzer_backend:app \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
