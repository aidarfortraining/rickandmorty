#!/usr/bin/env python3
"""
Debug script for database migration issues on Render.com
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rick_and_morty_app.settings')

# Setup Django
try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.db import connection
from django.core.management import execute_from_command_line
from django.conf import settings

def check_database_path():
    """Check database path and permissions"""
    db_path = settings.DATABASES['default']['NAME']
    print(f"Database path: {db_path}")
    
    if isinstance(db_path, str) and db_path != ':memory:':
        db_dir = os.path.dirname(db_path)
        print(f"Database directory: {db_dir}")
        
        # Check if directory exists and is writable
        if os.path.exists(db_dir):
            print(f"✅ Directory exists: {db_dir}")
            if os.access(db_dir, os.W_OK):
                print("✅ Directory is writable")
            else:
                print("❌ Directory is not writable")
        else:
            print(f"❌ Directory does not exist: {db_dir}")
            try:
                os.makedirs(db_dir, exist_ok=True)
                print(f"✅ Created directory: {db_dir}")
            except Exception as e:
                print(f"❌ Failed to create directory: {e}")
        
        # Check if database file exists
        if os.path.exists(db_path):
            print(f"✅ Database file exists: {db_path}")
            size = os.path.getsize(db_path)
            print(f"Database file size: {size} bytes")
        else:
            print(f"❌ Database file does not exist: {db_path}")

def check_tables():
    """Check what tables exist in database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Check for specific Django tables
            django_tables = ['django_migrations', 'django_content_type', 'auth_user']
            main_tables = ['main_character', 'main_episode', 'main_location']
            
            for table_name in django_tables + main_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                if cursor.fetchone():
                    print(f"✅ Table exists: {table_name}")
                else:
                    print(f"❌ Table missing: {table_name}")
                    
        return True
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_migrations():
    """Check migration status"""
    try:
        print("\n🔍 Checking migration status...")
        execute_from_command_line(['manage.py', 'showmigrations', '--verbosity=2'])
        return True
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False

def run_migrations():
    """Try to run migrations"""
    try:
        print("\n🔧 Making migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', 'main', '--verbosity=2'])
        
        print("\n🔧 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Django Database Debug Script")
    print("=" * 50)
    
    # Определяем окружение
    is_render = os.environ.get('RENDER') is not None
    is_debug = settings.DEBUG
    
    print(f"🐍 Python version: {sys.version}")
    print(f"🌐 Django version: {django.get_version()}")
    print(f"🛠️  Debug mode: {is_debug}")
    print(f"☁️  Render.com: {is_render}")
    print(f"🗄️  Database engine: {settings.DATABASES['default']['ENGINE']}")
    
    if is_render:
        print("📦 Running on Render.com - production mode")
    else:
        print("💻 Running locally - development mode")
    
    print("\n1. Checking database path and permissions...")
    check_database_path()
    
    print("\n2. Checking existing tables...")
    db_accessible = check_tables()
    
    if db_accessible:
        print("\n3. Checking migration status...")
        check_migrations()
    else:
        print("\n3. Database not accessible, trying to run migrations...")
        if run_migrations():
            print("\n4. Rechecking tables after migration...")
            check_tables()
        else:
            print("❌ Migration failed - database may need manual setup")
            if not is_render:
                print("💡 For local development, try:")
                print("   python setup_local.py")
    
    print("\n" + "=" * 50)
    print("✅ Debug completed!")
