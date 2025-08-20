from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Character, Episode, Location, SearchHistory


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'dimension', 'api_id', 'created']
    list_filter = ['type', 'dimension', 'created']
    search_fields = ['name', 'type', 'dimension']
    readonly_fields = ['api_id', 'url', 'created', 'updated']
    ordering = ['name']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'type', 'dimension')
        }),
        ('API данные', {
            'fields': ('api_id', 'url'),
            'classes': ['collapse']
        }),
        ('Системная информация', {
            'fields': ('created', 'updated'),
            'classes': ['collapse']
        }),
    )


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'episode', 'air_date', 'api_id', 'characters_count']
    list_filter = ['air_date', 'created']
    search_fields = ['name', 'episode']
    readonly_fields = ['api_id', 'url', 'created', 'updated', 'characters_count']
    ordering = ['episode']

    def characters_count(self, obj):
        return obj.characters.count()
    characters_count.short_description = 'Персонажей'

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'episode', 'air_date')
        }),
        ('API данные', {
            'fields': ('api_id', 'url'),
            'classes': ['collapse']
        }),
        ('Статистика', {
            'fields': ('characters_count',),
            'classes': ['collapse']
        }),
        ('Системная информация', {
            'fields': ('created', 'updated'),
            'classes': ['collapse']
        }),
    )


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'status', 'species', 'gender', 
        'origin_name', 'location_name', 'api_id', 'image_preview'
    ]
    list_filter = ['status', 'species', 'gender', 'created']
    search_fields = ['name', 'species', 'type']
    readonly_fields = [
        'api_id', 'url', 'created', 'updated', 
        'image_preview', 'episodes_count'
    ]
    filter_horizontal = ['episodes']
    ordering = ['name']

    def origin_name(self, obj):
        return obj.origin.name if obj.origin else '-'
    origin_name.short_description = 'Происхождение'

    def location_name(self, obj):
        return obj.location.name if obj.location else '-'
    location_name.short_description = 'Местоположение'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.image
            )
        return '-'
    image_preview.short_description = 'Изображение'

    def episodes_count(self, obj):
        return obj.episodes.count()
    episodes_count.short_description = 'Эпизодов'

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'status', 'species', 'type', 'gender')
        }),
        ('Локации', {
            'fields': ('origin', 'location')
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview')
        }),
        ('Эпизоды', {
            'fields': ('episodes', 'episodes_count')
        }),
        ('API данные', {
            'fields': ('api_id', 'url'),
            'classes': ['collapse']
        }),
        ('Системная информация', {
            'fields': ('created', 'updated'),
            'classes': ['collapse']
        }),
    )


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['query', 'search_type', 'results_count', 'created']
    list_filter = ['search_type', 'created']
    search_fields = ['query']
    readonly_fields = ['created']
    ordering = ['-created']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Поисковый запрос', {
            'fields': ('query', 'search_type', 'results_count')
        }),
        ('Системная информация', {
            'fields': ('created',),
        }),
    )