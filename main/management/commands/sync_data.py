from django.core.management.base import BaseCommand, CommandError
from main.services import api_service, sync_service
from main.models import Character, Episode, Location
import time


class Command(BaseCommand):
    help = 'Синхронизирует данные с Rick and Morty API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--characters',
            action='store_true',
            help='Синхронизировать только персонажей',
        )
        parser.add_argument(
            '--episodes',
            action='store_true',
            help='Синхронизировать только эпизоды',
        )
        parser.add_argument(
            '--locations',
            action='store_true',
            help='Синхронизировать только локации',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Максимальное количество страниц для синхронизации (по умолчанию: 5)',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        
        if not any([options['characters'], options['episodes'], options['locations']]):
            # Если не указаны конкретные типы, синхронизируем все
            self.sync_characters(limit)
            self.sync_episodes(limit)
            self.sync_locations(limit)
        else:
            if options['characters']:
                self.sync_characters(limit)
            if options['episodes']:
                self.sync_episodes(limit)
            if options['locations']:
                self.sync_locations(limit)

        self.stdout.write(
            self.style.SUCCESS('✅ Синхронизация завершена!')
        )

    def sync_characters(self, limit):
        """Синхронизирует персонажей"""
        self.stdout.write('🚀 Синхронизация персонажей...')
        
        page = 1
        synced_count = 0
        
        while page <= limit:
            self.stdout.write(f'📄 Обрабатываем страницу {page}...')
            
            api_data = api_service.get_characters(page=page)
            if not api_data or 'results' not in api_data:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Не удалось получить данные со страницы {page}')
                )
                break
                
            for char_data in api_data['results']:
                try:
                    if not isinstance(char_data, dict) or 'id' not in char_data:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Пропущен невалидный персонаж: {char_data}')
                        )
                        continue
                        
                    character = sync_service.sync_character(char_data)
                    synced_count += 1
                    self.stdout.write(f'✅ {character.name}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка синхронизации {char_data.get("name", "Unknown")}: {e}')
                    )
            
            # Проверяем, есть ли следующая страница
            if not api_data.get('info', {}).get('next'):
                break
                
            page += 1
            time.sleep(0.5)  # Небольшая задержка между запросами
            
        self.stdout.write(
            self.style.SUCCESS(f'✅ Синхронизировано {synced_count} персонажей')
        )

    def sync_episodes(self, limit):
        """Синхронизирует эпизоды"""
        self.stdout.write('📺 Синхронизация эпизодов...')
        
        page = 1
        synced_count = 0
        
        while page <= limit:
            self.stdout.write(f'📄 Обрабатываем страницу {page}...')
            
            api_data = api_service.get_episodes(page=page)
            if not api_data or 'results' not in api_data:
                break
                
            for episode_data in api_data['results']:
                try:
                    if not isinstance(episode_data, dict) or 'id' not in episode_data:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Пропущен невалидный эпизод: {episode_data}')
                        )
                        continue
                        
                    episode = sync_service.sync_episode(episode_data)
                    synced_count += 1
                    self.stdout.write(f'✅ {episode.name}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка синхронизации {episode_data.get("name", "Unknown")}: {e}')
                    )
            
            if not api_data.get('info', {}).get('next'):
                break
                
            page += 1
            time.sleep(0.5)
            
        self.stdout.write(
            self.style.SUCCESS(f'✅ Синхронизировано {synced_count} эпизодов')
        )

    def sync_locations(self, limit):
        """Синхронизирует локации"""
        self.stdout.write('🌍 Синхронизация локаций...')
        
        page = 1
        synced_count = 0
        
        while page <= limit:
            self.stdout.write(f'📄 Обрабатываем страницу {page}...')
            
            api_data = api_service.get_locations(page=page)
            if not api_data or 'results' not in api_data:
                break
                
            for location_data in api_data['results']:
                try:
                    if not isinstance(location_data, dict) or 'id' not in location_data:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Пропущен невалидная локация: {location_data}')
                        )
                        continue
                        
                    location = sync_service.sync_location(location_data)
                    synced_count += 1
                    self.stdout.write(f'✅ {location.name}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка синхронизации {location_data.get("name", "Unknown")}: {e}')
                    )
            
            if not api_data.get('info', {}).get('next'):
                break
                
            page += 1
            time.sleep(0.5)
            
        self.stdout.write(
            self.style.SUCCESS(f'✅ Синхронизировано {synced_count} локаций')
        )

