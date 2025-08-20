#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files first (doesn't need DB)
echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build process completed successfully!"
