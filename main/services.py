import requests
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from .models import Character, Episode, Location, SearchHistory
import logging

logger = logging.getLogger(__name__)


class RickAndMortyAPIService:
    """Сервис для работы с Rick and Morty API"""
    
    def __init__(self):
        self.base_url = settings.RICK_AND_MORTY_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Rick and Morty Django App/1.0'
        })

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Выполняет HTTP запрос к API"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            # Валидация URL перед запросом
            if not url.startswith(('http://', 'https://')):
                logger.error(f"Invalid URL scheme for {url}")
                return None
                
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Проверяем content-type
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.warning(f"Unexpected content-type for {endpoint}: {content_type}")
            
            data = response.json()
            
            # Проверяем, что получили валидные данные
            if not isinstance(data, dict):
                logger.warning(f"API returned non-dict data for {endpoint}: {type(data)}")
                return None
                
            return data
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timeout for {endpoint}: {e}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"API connection error for {endpoint}: {e}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error for {endpoint}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Invalid JSON response for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API request for {endpoint}: {e}")
            return None

    def get_characters(self, page: int = 1, name: str = None, status: str = None, 
                      species: str = None, gender: str = None) -> Optional[Dict]:
        """Получает список персонажей с фильтрацией"""
        cache_key = f"characters_p{page}_{name}_{status}_{species}_{gender}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        params = {'page': page}
        if name:
            params['name'] = name
        if status:
            params['status'] = status
        if species:
            params['species'] = species
        if gender:
            params['gender'] = gender
            
        result = self._make_request('character', params)
        if result:
            cache.set(cache_key, result, 300)  # Кэш на 5 минут
            
        return result

    def get_character(self, character_id: int) -> Optional[Dict]:
        """Получает данные конкретного персонажа"""
        cache_key = f"character_{character_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        result = self._make_request(f'character/{character_id}')
        if result:
            cache.set(cache_key, result, 600)  # Кэш на 10 минут
            
        return result

    def get_episodes(self, page: int = 1, name: str = None, episode: str = None) -> Optional[Dict]:
        """Получает список эпизодов с фильтрацией"""
        cache_key = f"episodes_p{page}_{name}_{episode}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        params = {'page': page}
        if name:
            params['name'] = name
        if episode:
            params['episode'] = episode
            
        result = self._make_request('episode', params)
        if result:
            cache.set(cache_key, result, 300)
            
        return result

    def get_episode(self, episode_id: int) -> Optional[Dict]:
        """Получает данные конкретного эпизода"""
        cache_key = f"episode_{episode_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        result = self._make_request(f'episode/{episode_id}')
        if result:
            cache.set(cache_key, result, 600)
            
        return result

    def get_locations(self, page: int = 1, name: str = None, type: str = None, 
                     dimension: str = None) -> Optional[Dict]:
        """Получает список локаций с фильтрацией"""
        cache_key = f"locations_p{page}_{name}_{type}_{dimension}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        params = {'page': page}
        if name:
            params['name'] = name
        if type:
            params['type'] = type
        if dimension:
            params['dimension'] = dimension
            
        result = self._make_request('location', params)
        if result:
            cache.set(cache_key, result, 300)
            
        return result

    def get_location(self, location_id: int) -> Optional[Dict]:
        """Получает данные конкретной локации"""
        cache_key = f"location_{location_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        result = self._make_request(f'location/{location_id}')
        if result:
            cache.set(cache_key, result, 600)
            
        return result


class DataSyncService:
    """Сервис для синхронизации данных с локальной БД"""
    
    def __init__(self):
        self.api_service = RickAndMortyAPIService()

    def sync_location(self, location_data: Dict) -> Location:
        """Синхронизирует данные локации"""
        try:
            location, created = Location.objects.get_or_create(
                api_id=location_data['id'],
                defaults={
                    'name': location_data.get('name', 'Unknown'),
                    'type': location_data.get('type', ''),
                    'dimension': location_data.get('dimension', ''),
                    'url': location_data.get('url', ''),
                }
            )
            
            if not created:
                # Обновляем существующую запись
                location.name = location_data.get('name', 'Unknown')
                location.type = location_data.get('type', '')
                location.dimension = location_data.get('dimension', '')
                location.url = location_data.get('url', '')
                location.save()
                
            return location
        except KeyError as e:
            logger.error(f"Missing required field in location_data: {e}")
            raise ValueError(f"Неполные данные локации: отсутствует поле {e}")
        except Exception as e:
            logger.error(f"Error syncing location: {e}")
            raise

    def sync_episode(self, episode_data: Dict) -> Episode:
        """Синхронизирует данные эпизода"""
        try:
            episode, created = Episode.objects.get_or_create(
                api_id=episode_data['id'],
                defaults={
                    'name': episode_data.get('name', 'Unknown'),
                    'air_date': episode_data.get('air_date', ''),
                    'episode': episode_data.get('episode', ''),
                    'url': episode_data.get('url', ''),
                }
            )
            
            if not created:
                episode.name = episode_data.get('name', 'Unknown')
                episode.air_date = episode_data.get('air_date', '')
                episode.episode = episode_data.get('episode', '')
                episode.url = episode_data.get('url', '')
                episode.save()
                
            return episode
        except KeyError as e:
            logger.error(f"Missing required field in episode_data: {e}")
            raise ValueError(f"Неполные данные эпизода: отсутствует поле {e}")
        except Exception as e:
            logger.error(f"Error syncing episode: {e}")
            raise

    def sync_character(self, character_data: Dict) -> Character:
        """Синхронизирует данные персонажа"""
        try:
            with transaction.atomic():
                # Синхронизируем связанные локации
                origin_location = None
                if character_data.get('origin') and character_data['origin'].get('url'):
                    try:
                        origin_id = int(character_data['origin']['url'].split('/')[-1])
                        origin_data = self.api_service.get_location(origin_id)
                        if origin_data:
                            origin_location = self.sync_location(origin_data)
                    except (ValueError, IndexError, KeyError):
                        logger.warning(f"Could not parse origin location for character {character_data.get('id')}")
                        pass

                current_location = None
                if character_data.get('location') and character_data['location'].get('url'):
                    try:
                        location_id = int(character_data['location']['url'].split('/')[-1])
                        location_data = self.api_service.get_location(location_id)
                        if location_data:
                            current_location = self.sync_location(location_data)
                    except (ValueError, IndexError, KeyError):
                        logger.warning(f"Could not parse current location for character {character_data.get('id')}")
                        pass

                # Создаем или обновляем персонажа
                character, created = Character.objects.get_or_create(
                    api_id=character_data['id'],
                    defaults={
                        'name': character_data.get('name', 'Unknown'),
                        'status': character_data.get('status', 'unknown').lower(),
                        'species': character_data.get('species', ''),
                        'type': character_data.get('type', ''),
                        'gender': character_data.get('gender', 'unknown').lower(),
                        'origin': origin_location,
                        'location': current_location,
                        'image': character_data.get('image', ''),
                        'url': character_data.get('url', ''),
                    }
                )
                
                if not created:
                    character.name = character_data.get('name', 'Unknown')
                    character.status = character_data.get('status', 'unknown').lower()
                    character.species = character_data.get('species', '')
                    character.type = character_data.get('type', '')
                    character.gender = character_data.get('gender', 'unknown').lower()
                    character.origin = origin_location
                    character.location = current_location
                    character.image = character_data.get('image', '')
                    character.url = character_data.get('url', '')
                    character.save()

                # Синхронизируем эпизоды
                episode_urls = character_data.get('episode', [])
                for episode_url in episode_urls:
                    try:
                        episode_id = int(episode_url.split('/')[-1])
                        episode_data = self.api_service.get_episode(episode_id)
                        if episode_data:
                            episode = self.sync_episode(episode_data)
                            character.episodes.add(episode)
                    except (ValueError, IndexError, KeyError):
                        logger.warning(f"Could not parse episode URL: {episode_url}")
                        continue

            return character
        except KeyError as e:
            logger.error(f"Missing required field in character_data: {e}")
            raise ValueError(f"Неполные данные персонажа: отсутствует поле {e}")
        except Exception as e:
            logger.error(f"Error syncing character: {e}")
            raise

    def save_search_history(self, query: str, search_type: str, results_count: int):
        """Сохраняет историю поиска"""
        SearchHistory.objects.create(
            query=query,
            search_type=search_type,
            results_count=results_count
        )


# Глобальные экземпляры сервисов
api_service = RickAndMortyAPIService()
sync_service = DataSyncService()

