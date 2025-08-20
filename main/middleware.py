"""
Middleware для автоматической инициализации базы данных
"""
import logging
from django.db import connection
from django.core.management import execute_from_command_line
from django.conf import settings

logger = logging.getLogger(__name__)

class DatabaseInitMiddleware:
    """Middleware для проверки и инициализации базы данных"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.db_initialized = False
        self.check_and_init_database()
    
    def check_and_init_database(self):
        """Проверяет и инициализирует базу данных если нужно"""
        if self.db_initialized:
            return
            
        try:
            # Проверяем есть ли таблицы
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='main_character';")
                if cursor.fetchone():
                    logger.info("Database already initialized")
                    self.db_initialized = True
                    return
                    
            logger.info("Database not initialized, running migrations...")
            
            # Выполняем миграции
            execute_from_command_line(['manage.py', 'makemigrations'])
            execute_from_command_line(['manage.py', 'migrate'])
            
            logger.info("Database migrations completed")
            self.db_initialized = True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def __call__(self, request):
        # Проверяем БД только если еще не инициализирована
        if not self.db_initialized:
            self.check_and_init_database()
            
        response = self.get_response(request)
        return response
