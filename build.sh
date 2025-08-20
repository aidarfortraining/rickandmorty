#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Sync data from API (optional, may fail if API is down)
python manage.py sync_data || echo "API sync failed, continuing..."
