"""
Middleware для автоматической инициализации базы данных (только для production)
"""
import logging
import os
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

class DatabaseInitMiddleware:
    """Middleware для проверки и инициализации базы данных (только на production)"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.db_checked = False
        
        # Запускаем проверку только в production окружении
        self.is_production = os.environ.get('RENDER') or not settings.DEBUG
        
        if self.is_production:
            logger.info("Production environment detected, will check database")
        else:
            logger.info("Development environment, skipping auto database init")
    
    def check_database_lazy(self):
        """Ленивая проверка базы данных (только при первом запросе)"""
        if self.db_checked or not self.is_production:
            return
            
        try:
            # Проверяем есть ли основные таблицы
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='main_character';")
                if cursor.fetchone():
                    logger.info("Database tables found")
                else:
                    logger.warning("Database tables not found, but auto-migration disabled in middleware")
                    
            self.db_checked = True
            
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            self.db_checked = True  # Не проверяем снова
    
    def __call__(self, request):
        # Проверяем БД только при первом запросе в production
        if not self.db_checked and self.is_production:
            self.check_database_lazy()
            
        response = self.get_response(request)
        return response
