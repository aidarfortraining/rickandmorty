#!/usr/bin/env python3
"""
Debug script to check database status
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rick_and_morty_app.settings')
django.setup()

from django.db import connection
from django.conf import settings

def debug_database():
    """Debug database configuration and status"""
    print("=== DATABASE DEBUG ===")
    print(f"Django settings: {settings.DATABASES}")
    print(f"Environment variables:")
    print(f"  DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    print(f"  RENDER: {os.environ.get('RENDER', 'Not set')}")
    print(f"  DEBUG: {os.environ.get('DEBUG', 'Not set')}")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Database tables found: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
                
            # Check if main_character table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='main_character';")
            main_char_table = cursor.fetchone()
            if main_char_table:
                print("✅ main_character table exists")
                cursor.execute("SELECT COUNT(*) FROM main_character;")
                count = cursor.fetchone()[0]
                print(f"  Records in main_character: {count}")
            else:
                print("❌ main_character table missing")
                
    except Exception as e:
        print(f"Database error: {e}")
    
    print("=== END DEBUG ===")

if __name__ == '__main__':
    debug_database()
