from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.db import connection
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import Character, Episode, Location, SearchHistory
from .serializers import (
    CharacterListSerializer, CharacterDetailSerializer,
    EpisodeSerializer, EpisodeDetailSerializer,
    LocationSerializer, LocationDetailSerializer,
    SearchHistorySerializer, SearchRequestSerializer,
    CharacterFilterSerializer, EpisodeFilterSerializer,
    LocationFilterSerializer
)
from .services import api_service, sync_service
import logging

logger = logging.getLogger(__name__)


# ====== WEB VIEWS (для HTML страниц) ======

def home_view(request):
    """Главная страница"""
    try:
        # Пытаемся получить статистику из базы данных
        characters_count = Character.objects.count()
        episodes_count = Episode.objects.count()
        locations_count = Location.objects.count()
        recent_searches = SearchHistory.objects.order_by('-created')[:5]
        data_source = "database"
    except Exception as e:
        logger.warning(f"Database not available for home view: {e}")
        # Fallback к API если БД недоступна
        try:
            # Получаем общую информацию из API
            api_info = api_service._make_request('character')
            characters_count = api_info.get('info', {}).get('count', 826) if api_info else 826
            
            api_info = api_service._make_request('episode')
            episodes_count = api_info.get('info', {}).get('count', 51) if api_info else 51
            
            api_info = api_service._make_request('location')
            locations_count = api_info.get('info', {}).get('count', 126) if api_info else 126
            
            recent_searches = []
            data_source = "api"
        except Exception as api_error:
            logger.error(f"API also failed: {api_error}")
            # Hardcoded fallback значения
            characters_count = 826
            episodes_count = 51
            locations_count = 126
            recent_searches = []
            data_source = "fallback"
    
    context = {
        'characters_count': characters_count,
        'episodes_count': episodes_count,
        'locations_count': locations_count,
        'recent_searches': recent_searches,
        'data_source': data_source,
    }
    return render(request, 'main/home.html', context)


def characters_view(request):
    """Страница списка персонажей"""
    # Получаем параметры фильтрации
    name = request.GET.get('name', '')
    status = request.GET.get('status', '')
    species = request.GET.get('species', '')
    gender = request.GET.get('gender', '')
    page = request.GET.get('page', 1)

    # Получаем данные из API
    api_data = api_service.get_characters(
        page=int(page),
        name=name if name else None,
        status=status if status else None,
        species=species if species else None,
        gender=gender if gender else None
    )
    
    characters = []
    pagination_info = {}
    
    if api_data and 'results' in api_data:
        characters = api_data['results']
        pagination_info = api_data.get('info', {})
        
        # Синхронизируем данные с локальной БД для популярных персонажей
        for char_data in characters[:5]:  # Синхронизируем первых 5
            try:
                sync_service.sync_character(char_data)
            except Exception as e:
                logger.error(f"Error syncing character {char_data.get('id')}: {e}")

    context = {
        'characters': characters,
        'pagination_info': pagination_info,
        'current_page': int(page),
        'filters': {
            'name': name,
            'status': status,
            'species': species,
            'gender': gender,
        },
        'status_choices': Character.STATUS_CHOICES,
        'gender_choices': Character.GENDER_CHOICES,
    }
    return render(request, 'main/characters.html', context)


def character_detail_view(request, character_id):
    """Страница детальной информации о персонаже"""
    try:
        # Сначала пытаемся получить из API
        api_data = api_service.get_character(character_id)
        
        if not api_data:
            # Если API недоступен, ищем в локальной БД
            character = get_object_or_404(Character, api_id=character_id)
            context = {'character': character, 'from_db': True}
        else:
            # Синхронизируем с БД
            try:
                character = sync_service.sync_character(api_data)
                context = {'character_data': api_data, 'character': character, 'from_db': False}
            except Exception as e:
                logger.error(f"Error syncing character {character_id}: {e}")
                context = {'character_data': api_data, 'from_db': False}
        
        return render(request, 'main/character_detail.html', context)
    except Exception as e:
        logger.error(f"Unexpected error in character_detail_view for {character_id}: {e}")
        # Fallback to 404 if something goes wrong
        raise Http404("Персонаж не найден")


def episodes_view(request):
    """Страница списка эпизодов"""
    name = request.GET.get('name', '')
    episode = request.GET.get('episode', '')
    page = request.GET.get('page', 1)

    api_data = api_service.get_episodes(
        page=int(page),
        name=name if name else None,
        episode=episode if episode else None
    )
    
    episodes = []
    pagination_info = {}
    
    if api_data and 'results' in api_data:
        episodes = api_data['results']
        pagination_info = api_data.get('info', {})

    context = {
        'episodes': episodes,
        'pagination_info': pagination_info,
        'current_page': int(page),
        'filters': {
            'name': name,
            'episode': episode,
        }
    }
    return render(request, 'main/episodes.html', context)


def episode_detail_view(request, episode_id):
    """Страница детальной информации об эпизоде"""
    try:
        api_data = api_service.get_episode(episode_id)
        
        if not api_data:
            episode = get_object_or_404(Episode, api_id=episode_id)
            context = {'episode': episode, 'from_db': True}
        else:
            try:
                episode = sync_service.sync_episode(api_data)
                context = {'episode_data': api_data, 'episode': episode, 'from_db': False}
            except Exception as e:
                logger.error(f"Error syncing episode {episode_id}: {e}")
                context = {'episode_data': api_data, 'from_db': False}
        
        return render(request, 'main/episode_detail.html', context)
    except Exception as e:
        logger.error(f"Unexpected error in episode_detail_view for {episode_id}: {e}")
        raise Http404("Эпизод не найден")


def locations_view(request):
    """Страница списка локаций"""
    name = request.GET.get('name', '')
    type_filter = request.GET.get('type', '')
    dimension = request.GET.get('dimension', '')
    page = request.GET.get('page', 1)

    api_data = api_service.get_locations(
        page=int(page),
        name=name if name else None,
        type=type_filter if type_filter else None,
        dimension=dimension if dimension else None
    )
    
    locations = []
    pagination_info = {}
    
    if api_data and 'results' in api_data:
        locations = api_data['results']
        pagination_info = api_data.get('info', {})

    context = {
        'locations': locations,
        'pagination_info': pagination_info,
        'current_page': int(page),
        'filters': {
            'name': name,
            'type': type_filter,
            'dimension': dimension,
        }
    }
    return render(request, 'main/locations.html', context)


def location_detail_view(request, location_id):
    """Страница детальной информации о локации"""
    try:
        api_data = api_service.get_location(location_id)
        
        if not api_data:
            location = get_object_or_404(Location, api_id=location_id)
            context = {'location': location, 'from_db': True}
        else:
            try:
                location = sync_service.sync_location(api_data)
                context = {'location_data': api_data, 'location': location, 'from_db': False}
            except Exception as e:
                logger.error(f"Error syncing location {location_id}: {e}")
                context = {'location_data': api_data, 'from_db': False}
        
        return render(request, 'main/location_detail.html', context)
    except Exception as e:
        logger.error(f"Unexpected error in location_detail_view for {location_id}: {e}")
        raise Http404("Локация не найдена")


def search_view(request):
    """Универсальная страница поиска"""
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'character')
    page = request.GET.get('page', 1)
    
    results = []
    pagination_info = {}
    results_count = 0
    
    if query:
        if search_type == 'character':
            # Улучшенный поиск персонажей - пробуем разные параметры
            api_data = api_service.get_characters(page=int(page), name=query)
            # Если ничего не найдено по имени, пробуем поиск по виду
            if not api_data or not api_data.get('results'):
                api_data = api_service.get_characters(page=int(page), species=query)
        elif search_type == 'episode':
            api_data = api_service.get_episodes(page=int(page), name=query)
            # Если ничего не найдено по названию, пробуем поиск по номеру эпизода
            if not api_data or not api_data.get('results'):
                api_data = api_service.get_episodes(page=int(page), episode=query)
        elif search_type == 'location':
            api_data = api_service.get_locations(page=int(page), name=query)
            # Если ничего не найдено по названию, пробуем поиск по типу
            if not api_data or not api_data.get('results'):
                api_data = api_service.get_locations(page=int(page), type=query)
        else:
            api_data = None
            
        if api_data and 'results' in api_data:
            results = api_data['results']
            pagination_info = api_data.get('info', {})
            results_count = pagination_info.get('count', 0)
            
        # Сохраняем в историю поиска
        if query and results_count > 0:
            sync_service.save_search_history(query, search_type, results_count)

    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
        'pagination_info': pagination_info,
        'current_page': int(page),
        'results_count': results_count,
        'search_types': [
            ('character', 'Персонажи'),
            ('episode', 'Эпизоды'),
            ('location', 'Локации'),
        ]
    }
    return render(request, 'main/search.html', context)


# API ViewSets
class SearchAPIView(APIView):
    """Универсальный API для поиска"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        serializer = SearchRequestSerializer(data=request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            query = data['query']
            search_type = data['search_type']
            page = data['page']
            
            if search_type == 'character':
                api_data = api_service.get_characters(page=page, name=query)
            elif search_type == 'episode':
                api_data = api_service.get_episodes(page=page, name=query)
            elif search_type == 'location':
                api_data = api_service.get_locations(page=page, name=query)
            else:
                return Response(
                    {'error': 'Неверный тип поиска'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if api_data:
                # Сохраняем в историю поиска
                results_count = api_data.get('info', {}).get('count', 0)
                if results_count > 0:
                    sync_service.save_search_history(query, search_type, results_count)
                
                return Response(api_data)
            else:
                return Response(
                    {'error': 'API недоступен'}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def health_check(request):
    """Health check endpoint for monitoring and debugging"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "OK"
            
            # Check if main tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            
            main_tables = ['main_character', 'main_episode', 'main_location']
            missing_tables = [table for table in main_tables if table not in tables]
            
        # Check models
        try:
            character_count = Character.objects.count()
            episode_count = Episode.objects.count()
            location_count = Location.objects.count()
            models_status = "OK"
        except Exception as e:
            character_count = episode_count = location_count = 0
            models_status = f"Error: {e}"
        
        # Check API service
        try:
            api_status = "OK" if api_service else "Not available"
        except:
            api_status = "Error"
            
        health_data = {
            "status": "healthy" if db_status == "OK" and models_status == "OK" else "unhealthy",
            "timestamp": "2025-01-20T12:00:00Z",
            "database": {
                "status": db_status,
                "tables_found": len(tables),
                "missing_tables": missing_tables,
                "database_path": str(settings.DATABASES['default']['NAME']),
            },
            "models": {
                "status": models_status,
                "characters": character_count,
                "episodes": episode_count,
                "locations": location_count,
            },
            "api_service": {
                "status": api_status
            },
            "settings": {
                "debug": settings.DEBUG,
                "allowed_hosts": settings.ALLOWED_HOSTS,
                "database_engine": settings.DATABASES['default']['ENGINE'],
            }
        }
        
        return JsonResponse(health_data)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "settings": {
                "debug": settings.DEBUG,
                "allowed_hosts": settings.ALLOWED_HOSTS,
            }
        }, status=500)
