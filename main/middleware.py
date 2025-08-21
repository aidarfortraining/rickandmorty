"""
Middleware для мониторинга базы данных (только для production)
"""
import logging
import os
from django.db import connection
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class DatabaseInitMiddleware:
    """Middleware для мониторинга базы данных (только на production)"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.db_checked = False
        
        # Запускаем проверку только в production окружении
        self.is_production = os.environ.get('RENDER') or not settings.DEBUG
        
        if self.is_production:
            logger.info("Production environment detected, will monitor database")
        else:
            logger.info("Development environment, skipping database monitoring")
    
    def check_database_health(self):
        """Проверка состояния базы данных"""
        if self.db_checked or not self.is_production:
            return True
            
        try:
            # Проверяем есть ли основные таблицы
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'main_%';")
                tables = cursor.fetchall()
                
                expected_tables = ['main_character', 'main_episode', 'main_location']
                found_tables = [table[0] for table in tables]
                missing_tables = [t for t in expected_tables if t not in found_tables]
                
                if missing_tables:
                    logger.error(f"Missing database tables: {missing_tables}")
                    return False
                else:
                    logger.info("All database tables found")
                    return True
                    
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
        finally:
            self.db_checked = True
    
    def __call__(self, request):
        # Для health endpoint - всегда проверяем БД
        if request.path == '/health/':
            # Пропускаем middleware для health check
            response = self.get_response(request)
            return response
        
        # Для остальных запросов - проверяем БД только в production при первом запросе
        if not self.db_checked and self.is_production:
            db_healthy = self.check_database_health()
            
            # Если БД нездорова, возвращаем 503 Service Unavailable
            if not db_healthy:
                logger.error("Database is unhealthy, returning 503")
                return JsonResponse({
                    'error': 'Database not initialized',
                    'message': 'Please wait for database initialization to complete',
                    'status': 503
                }, status=503)
            
        response = self.get_response(request)
        return response
