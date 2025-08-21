#!/usr/bin/env python3
"""
🧪 Тестирование локальной версии проекта
Проверяет, что все компоненты работают корректно в локальном окружении
"""
import os
import sys
import subprocess
import django
import time

# Добавляем проект в path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rick_and_morty_app.settings')

def run_command(command, description, timeout=30):
    """Выполняет команду с таймаутом"""
    print(f"🧪 {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(
                command, shell=True, check=True, 
                capture_output=True, text=True, timeout=timeout
            )
        else:
            result = subprocess.run(
                command, check=True, 
                capture_output=True, text=True, timeout=timeout
            )
        
        print(f"✅ {description} - OK")
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED: {e}")
        print(f"   Error output: {e.stderr}")
        return False, e.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False, "Timeout"

def test_django_setup():
    """Тестирует настройку Django"""
    print("🔧 Тестирование настройки Django...")
    try:
        django.setup()
        from django.conf import settings
        
        # Проверяем основные настройки
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   Database: {settings.DATABASES['default']['ENGINE']}")
        print(f"   Database path: {settings.DATABASES['default']['NAME']}")
        
        # Проверяем что middleware не включен в локальном режиме
        middleware_active = 'main.middleware.DatabaseInitMiddleware' in settings.MIDDLEWARE
        print(f"   Production middleware: {'Active' if middleware_active else 'Inactive'}")
        
        if not settings.DEBUG and not middleware_active:
            print("⚠️  WARNING: DEBUG=False but production middleware not active")
        
        print("✅ Django setup - OK")
        return True
    except Exception as e:
        print(f"❌ Django setup - FAILED: {e}")
        return False

def test_database():
    """Тестирует базу данных"""
    print("🗄️  Тестирование базы данных...")
    try:
        from django.db import connection
        
        # Проверяем подключение
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("   ✅ Database connection - OK")
        
        # Проверяем таблицы
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            
            expected_tables = ['main_character', 'main_episode', 'main_location']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                print(f"   ⚠️  Missing tables: {missing_tables}")
                print("   💡 Run: python manage.py migrate")
                return False
            else:
                print(f"   ✅ All tables present ({len(tables)} total)")
        
        return True
    except Exception as e:
        print(f"❌ Database test - FAILED: {e}")
        return False

def test_models():
    """Тестирует модели Django"""
    print("📊 Тестирование моделей...")
    try:
        from main.models import Character, Episode, Location
        
        # Проверяем количество данных
        char_count = Character.objects.count()
        episode_count = Episode.objects.count()
        location_count = Location.objects.count()
        
        print(f"   Characters: {char_count}")
        print(f"   Episodes: {episode_count}")
        print(f"   Locations: {location_count}")
        
        # Проверяем что модели работают
        if char_count > 0:
            char = Character.objects.first()
            print(f"   Sample character: {char.name}")
        
        print("✅ Models test - OK")
        return True
    except Exception as e:
        print(f"❌ Models test - FAILED: {e}")
        return False

def test_services():
    """Тестирует сервисы"""
    print("🌐 Тестирование сервисов...")
    try:
        from main.services import api_service
        
        # Проверяем API сервис
        api_data = api_service.get_character(1)
        if api_data and 'name' in api_data:
            print(f"   ✅ API service - OK (Got: {api_data['name']})")
        else:
            print("   ⚠️  API service - API may be down, but service works")
        
        return True
    except Exception as e:
        print(f"❌ Services test - FAILED: {e}")
        return False

def test_views():
    """Тестирует views"""
    print("🌐 Тестирование views...")
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Тест главной страницы
        response = client.get('/')
        if response.status_code == 200:
            print("   ✅ Home page - OK")
        else:
            print(f"   ❌ Home page - FAILED ({response.status_code})")
            return False
        
        # Тест health check
        response = client.get('/health/')
        if response.status_code == 200:
            print("   ✅ Health check - OK")
        else:
            print(f"   ❌ Health check - FAILED ({response.status_code})")
        
        # Тест поиска
        response = client.get('/search/?q=Rick&type=character')
        if response.status_code == 200:
            print("   ✅ Search page - OK")
        else:
            print(f"   ❌ Search page - FAILED ({response.status_code})")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Views test - FAILED: {e}")
        return False

def test_static_files():
    """Тестирует статические файлы"""
    print("📁 Тестирование статических файлов...")
    try:
        from django.contrib.staticfiles import finders
        
        # Проверяем основные статические файлы
        css_file = finders.find('css/style.css')
        js_file = finders.find('js/main.js')
        
        if css_file:
            print("   ✅ CSS file found")
        else:
            print("   ❌ CSS file not found")
            return False
        
        if js_file:
            print("   ✅ JS file found")
        else:
            print("   ❌ JS file not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Static files test - FAILED: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Rick and Morty Local Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Django Setup", test_django_setup),
        ("Database", test_database),
        ("Models", test_models),
        ("Services", test_services),
        ("Views", test_views),
        ("Static Files", test_static_files),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    # Итоговый отчет
    print("\n" + "="*50)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print(f"\n📊 Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Локальная версия работает корректно.")
        return True
    else:
        print("⚠️  Некоторые тесты не пройдены. Проверьте ошибки выше.")
        print("\n💡 Возможные решения:")
        print("   - python manage.py migrate")
        print("   - python manage.py collectstatic")
        print("   - python manage.py sync_data --limit 1")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
