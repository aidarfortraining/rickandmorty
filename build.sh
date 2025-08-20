#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Make migrations (in case they're not in git)
echo "Making migrations..."
python manage.py makemigrations

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Create superuser if needed (optional)
echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF

# Sync data from API (optional, may fail if API is down)
echo "Syncing data from Rick and Morty API..."
python manage.py sync_data || echo "API sync failed, continuing with empty database..."

echo "Build process completed successfully!"
