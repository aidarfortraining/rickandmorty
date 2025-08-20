from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from .models import Character, Episode, Location, SearchHistory
from .services import api_service, sync_service


class ModelTests(TestCase):
    """Простые тесты для моделей"""
    
    def setUp(self):
        self.location = Location.objects.create(
            api_id=1,
            name="Earth",
            type="Planet",
            dimension="C-137"
        )
        
        self.episode = Episode.objects.create(
            api_id=1,
            name="Pilot",
            air_date="December 2, 2013",
            episode="S01E01"
        )
        
        self.character = Character.objects.create(
            api_id=1,
            name="Rick Sanchez",
            status="alive",
            species="Human",
            gender="male",
            origin=self.location
        )
    
    def test_location_str(self):
        """Тест строкового представления локации"""
        self.assertEqual(str(self.location), "Earth")
    
    def test_episode_str(self):
        """Тест строкового представления эпизода"""
        self.assertEqual(str(self.episode), "S01E01 - Pilot")
    
    def test_character_str(self):
        """Тест строкового представления персонажа"""
        self.assertEqual(str(self.character), "Rick Sanchez")
    
    def test_character_status_display(self):
        """Тест отображения статуса персонажа"""
        self.assertEqual(self.character.status_display, "Живой")
    
    def test_character_gender_display(self):
        """Тест отображения пола персонажа"""
        self.assertEqual(self.character.gender_display, "Мужской")


class ViewTests(TestCase):
    """Простые тесты для views"""
    
    def setUp(self):
        self.client = Client()
    
    def test_home_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rick and Morty")
    
    def test_characters_view(self):
        """Тест страницы персонажей"""
        with patch('main.services.api_service.get_characters') as mock_api:
            mock_api.return_value = {
                'results': [],
                'info': {'count': 0, 'pages': 1}
            }
            response = self.client.get(reverse('main:characters'))
            self.assertEqual(response.status_code, 200)
    
    def test_episodes_view(self):
        """Тест страницы эпизодов"""
        with patch('main.services.api_service.get_episodes') as mock_api:
            mock_api.return_value = {
                'results': [],
                'info': {'count': 0, 'pages': 1}
            }
            response = self.client.get(reverse('main:episodes'))
            self.assertEqual(response.status_code, 200)
    
    def test_locations_view(self):
        """Тест страницы локаций"""
        with patch('main.services.api_service.get_locations') as mock_api:
            mock_api.return_value = {
                'results': [],
                'info': {'count': 0, 'pages': 1}
            }
            response = self.client.get(reverse('main:locations'))
            self.assertEqual(response.status_code, 200)
    
    def test_search_view(self):
        """Тест страницы поиска"""
        response = self.client.get(reverse('main:search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Поиск")
    
    def test_search_with_query(self):
        """Тест поиска с запросом"""
        with patch('main.services.api_service.get_characters') as mock_api:
            mock_api.return_value = {
                'results': [{'id': 1, 'name': 'Rick'}],
                'info': {'count': 1, 'pages': 1}
            }
            response = self.client.get(reverse('main:search'), {'q': 'Rick', 'type': 'character'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Rick")


class ServiceTests(TestCase):
    """Простые тесты для сервисов"""
    
    def test_api_service_exists(self):
        """Тест существования API сервиса"""
        self.assertIsNotNone(api_service)
    
    def test_sync_service_exists(self):
        """Тест существования сервиса синхронизации"""
        self.assertIsNotNone(sync_service)
    
    def test_search_history_creation(self):
        """Тест создания истории поиска"""
        initial_count = SearchHistory.objects.count()
        sync_service.save_search_history("Rick", "character", 5)
        self.assertEqual(SearchHistory.objects.count(), initial_count + 1)


class APITests(TestCase):
    """Простые тесты для API"""
    
    def test_api_search_endpoint(self):
        """Тест API поиска"""
        with patch('main.services.api_service.get_characters') as mock_api:
            mock_api.return_value = {
                'results': [{'id': 1, 'name': 'Rick'}],
                'info': {'count': 1}
            }
            response = self.client.get(reverse('main:api-search'), {
                'q': 'Rick',
                'type': 'character'
            })
            self.assertEqual(response.status_code, 200)


class IntegrationTests(TestCase):
    """Простые интеграционные тесты"""
    
    def test_character_detail_with_existing_character(self):
        """Тест детальной страницы существующего персонажа"""
        character = Character.objects.create(
            api_id=999,
            name="Test Character",
            status="alive",
            species="Human",
            gender="male"
        )
        
        with patch('main.services.api_service.get_character') as mock_api:
            mock_api.return_value = None  # API недоступен
            response = self.client.get(reverse('main:character-detail', kwargs={'character_id': 999}))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Test Character")
    
    def test_character_detail_nonexistent(self):
        """Тест детальной страницы несуществующего персонажа"""
        with patch('main.services.api_service.get_character') as mock_api:
            mock_api.return_value = None
            response = self.client.get(reverse('main:character-detail', kwargs={'character_id': 9999}))
            self.assertEqual(response.status_code, 404)
