#!/usr/bin/env python3
"""
Initialization script for database setup on production
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rick_and_morty_app.settings')

# Setup Django
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth.models import User

def check_database():
    """Check if database exists and has tables"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Found {len(tables)} tables in database")
            return len(tables) > 0
    except Exception as e:
        print(f"Database check failed: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    print("Running makemigrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    print("Running migrate...")
    execute_from_command_line(['manage.py', 'migrate'])

def create_superuser():
    """Create superuser if it doesn't exist"""
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print('Superuser created: admin/admin123')
        else:
            print('Superuser already exists')
    except Exception as e:
        print(f"Failed to create superuser: {e}")

def sync_data():
    """Sync data from Rick and Morty API"""
    try:
        execute_from_command_line(['manage.py', 'sync_data'])
        print('Data synchronization completed')
    except Exception as e:
        print(f"Data sync failed: {e}")

if __name__ == '__main__':
    print("Initializing database...")
    
    # Check if database needs initialization
    if not check_database():
        print("Database not found or empty, initializing...")
        run_migrations()
    else:
        print("Database already initialized")
    
    # Create superuser
    create_superuser()
    
    # Sync data
    sync_data()
    
    print("Database initialization completed!")
