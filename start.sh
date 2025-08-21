#!/usr/bin/env bash
# Simple startup script for Render deployment

echo "Starting Rick and Morty application..."

# Quick database health check
echo "Checking database health..."
python debug_migration.py || echo "Debug check failed, continuing..."

# Start the application directly
echo "Starting gunicorn server..."
exec gunicorn rick_and_morty_app.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
