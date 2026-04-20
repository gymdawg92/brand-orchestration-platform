#!/bin/sh
set -e

echo "=== Platform API starting ==="
echo "PORT=${PORT:-8000}"
echo "DATABASE_URL=${DATABASE_URL:-sqlite:///./platform.db}"

if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -q "^postgres"; then
    echo "Running Alembic migrations..."
    alembic upgrade head
    echo "Migrations done."
fi

echo "Starting uvicorn..."
exec uvicorn platform_api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
