#!/bin/bash
# Script chạy production server với Gunicorn

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment
source venv/bin/activate

# Số workers (thường là 2-4 x số CPU cores)
WORKERS=${WORKERS:-4}

# Timeout (giây)
TIMEOUT=${TIMEOUT:-120}

# Bind address
BIND=${HOST:-0.0.0.0}:${PORT:-5001}

echo "=========================================="
echo "Starting Internal Management System"
echo "=========================================="
echo "Workers: $WORKERS"
echo "Timeout: $TIMEOUT seconds"
echo "Binding to: $BIND"
echo "=========================================="

# Chạy Gunicorn
gunicorn \
    --bind $BIND \
    --workers $WORKERS \
    --timeout $TIMEOUT \
    --access-logfile data/logs/access.log \
    --error-logfile data/logs/error.log \
    --log-level info \
    --capture-output \
    wsgi:application
