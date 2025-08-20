from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API роутер
router = DefaultRouter()

app_name = 'main'

urlpatterns = [
    # Главная страница
    path('', views.home_view, name='home'),
    
    # Страницы персонажей
    path('characters/', views.characters_view, name='characters'),
    path('characters/<int:character_id>/', views.character_detail_view, name='character-detail'),
    
    # Страницы эпизодов
    path('episodes/', views.episodes_view, name='episodes'),
    path('episodes/<int:episode_id>/', views.episode_detail_view, name='episode-detail'),
    
    # Страницы локаций
    path('locations/', views.locations_view, name='locations'),
    path('locations/<int:location_id>/', views.location_detail_view, name='location-detail'),
    
    # Поиск
    path('search/', views.search_view, name='search'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/search/', views.SearchAPIView.as_view(), name='api-search'),
]
