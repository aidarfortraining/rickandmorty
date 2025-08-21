#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."

# Check if this is a Render.com deployment
if [ -n "$RENDER" ]; then
    echo "📦 Render.com deployment detected"
    IS_PRODUCTION=true
else
    echo "🛠️  Local development build"
    IS_PRODUCTION=false
fi

# Install dependencies
echo "📋 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files (works everywhere)
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Database initialization (only on Render.com)
if [ "$IS_PRODUCTION" = true ]; then
    echo "🗄️  Initializing production database..."
    
    # Make migrations for main app
    echo "📝 Creating migrations..."
    python manage.py makemigrations main || echo "⚠️  Migrations may already exist"
    
    # Apply all migrations
    echo "🔄 Applying migrations..."
    python manage.py migrate
    
    # Create superuser for production
    echo "👤 Creating superuser..."
    python manage.py shell << 'EOF'
from django.contrib.auth.models import User
import os
try:
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')  
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f'✅ Superuser created: {username}')
    else:
        print(f'ℹ️  Superuser {username} already exists')
except Exception as e:
    print(f'❌ Error creating superuser: {e}')
EOF

    # Sync initial data from API (production only)
    echo "🔄 Syncing initial data from Rick and Morty API..."
    python manage.py sync_data --limit 2 || echo "⚠️  API sync failed, continuing..."
    
else
    echo "⚠️  Skipping database initialization for local development"
    echo "💡 Run 'python manage.py migrate' and 'python manage.py sync_data' manually"
fi

echo "✅ Build process completed successfully!"
