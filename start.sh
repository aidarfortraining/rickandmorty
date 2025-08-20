#!/usr/bin/env bash
# Startup script for Render deployment

echo "Starting application..."

# Initialize database on startup
echo "Initializing database..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if needed
echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('Superuser created: admin/admin123')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f'Error creating superuser: {e}')
EOF

# Sync data from API in background
echo "Syncing data from Rick and Morty API..."
python manage.py sync_data || echo "API sync failed, continuing..."

# Start the application
echo "Starting gunicorn server..."
exec gunicorn rick_and_morty_app.wsgi:application
