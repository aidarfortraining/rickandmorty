#!/usr/bin/env python3
"""
🛠️ Локальная настройка проекта Rick and Morty
Этот скрипт поможет быстро настроить проект для локальной разработки
"""
import os
import sys
import subprocess
import platform

def run_command(command, description, check=True):
    """Выполняет команду с красивым выводом"""
    print(f"🔄 {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        if result.stderr and check:
            print(f"   ⚠️  {result.stderr.strip()}")
        
        print(f"✅ {description} завершено")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} не удалось: {e}")
        if not check:
            return None
        raise

def check_python_version():
    """Проверяет версию Python"""
    version = sys.version_info
    print(f"🐍 Python версия: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Требуется Python 3.10 или выше для Django 5.2.5")
        return False
    
    print("✅ Версия Python подходит")
    return True

def check_virtual_environment():
    """Проверяет активировано ли виртуальное окружение"""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print("✅ Виртуальное окружение активировано")
        return True
    else:
        print("⚠️  Виртуальное окружение не активировано")
        print("💡 Рекомендуется создать и активировать venv:")
        
        if platform.system() == "Windows":
            print("   python -m venv .venv")
            print("   .venv\\Scripts\\activate")
        else:
            print("   python -m venv .venv")
            print("   source .venv/bin/activate")
        
        response = input("\n❓ Продолжить без виртуального окружения? (y/N): ")
        return response.lower() in ['y', 'yes', 'да']

def install_dependencies():
    """Устанавливает зависимости"""
    run_command("pip install -r requirements.txt", "Установка зависимостей")

def setup_database():
    """Настраивает базу данных"""
    print("\n🗄️  Настройка базы данных...")
    
    # Проверяем существует ли БД
    if os.path.exists('db.sqlite3'):
        response = input("❓ База данных уже существует. Пересоздать? (y/N): ")
        if response.lower() in ['y', 'yes', 'да']:
            os.remove('db.sqlite3')
            print("🗑️  Старая база данных удалена")
    
    # Создаем миграции
    run_command("python manage.py makemigrations", "Создание миграций")
    run_command("python manage.py makemigrations main", "Создание миграций для main")
    
    # Применяем миграции
    run_command("python manage.py migrate", "Применение миграций")

def create_superuser():
    """Создает суперпользователя"""
    print("\n👤 Создание суперпользователя...")
    
    script = """
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Суперпользователь создан: admin/admin123')
else:
    print('ℹ️  Суперпользователь уже существует')
"""
    
    run_command(f'python manage.py shell -c "{script}"', "Создание суперпользователя")

def sync_initial_data():
    """Синхронизирует начальные данные"""
    response = input("\n❓ Загрузить данные из Rick and Morty API? (Y/n): ")
    
    if response.lower() not in ['n', 'no', 'нет']:
        run_command(
            "python manage.py sync_data --limit 3", 
            "Синхронизация данных с API", 
            check=False
        )

def collect_static():
    """Собирает статические файлы"""
    run_command("python manage.py collectstatic --no-input", "Сбор статических файлов")

def show_final_info():
    """Показывает финальную информацию"""
    print("\n" + "="*60)
    print("🎉 Локальная настройка завершена!")
    print("="*60)
    print("\n📝 Чтобы запустить сервер разработки:")
    print("   python manage.py runserver")
    print("\n🌐 Приложение будет доступно по адресу:")
    print("   http://localhost:8000")
    print("\n👤 Админ-панель:")
    print("   http://localhost:8000/admin/")
    print("   Логин: admin")
    print("   Пароль: admin123")
    print("\n🔧 Полезные команды:")
    print("   python manage.py sync_data          # Синхронизация данных")
    print("   python manage.py shell              # Django shell")
    print("   python manage.py createsuperuser    # Создать суперпользователя")
    print("\n💡 Для разработки рекомендуется установить:")
    print("   pip install django-debug-toolbar")

def main():
    """Основная функция"""
    print("🚀 Настройка Rick and Morty Django проекта")
    print("=" * 50)
    
    # Проверки
    if not check_python_version():
        return False
        
    if not check_virtual_environment():
        return False
    
    try:
        # Основная настройка
        install_dependencies()
        setup_database()
        create_superuser()
        collect_static()
        sync_initial_data()
        
        show_final_info()
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при настройке: {e}")
        print("💡 Попробуйте выполнить команды вручную:")
        print("   python manage.py migrate")
        print("   python manage.py createsuperuser")
        print("   python manage.py runserver")
        return False
    except KeyboardInterrupt:
        print("\n\n⛔ Настройка прервана пользователем")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
