from rest_framework import serializers
from .models import Character, Episode, Location, SearchHistory


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор для локаций"""
    
    class Meta:
        model = Location
        fields = [
            'id', 'api_id', 'name', 'type', 'dimension', 
            'url', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']


class EpisodeSerializer(serializers.ModelSerializer):
    """Сериализатор для эпизодов"""
    
    class Meta:
        model = Episode
        fields = [
            'id', 'api_id', 'name', 'air_date', 'episode', 
            'url', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']


class CharacterListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка персонажей (упрощенный)"""
    origin_name = serializers.CharField(source='origin.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    status_display = serializers.CharField(read_only=True)
    gender_display = serializers.CharField(read_only=True)
    episodes_count = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = [
            'id', 'api_id', 'name', 'status', 'status_display',
            'species', 'type', 'gender', 'gender_display',
            'origin_name', 'location_name', 'image', 'episodes_count'
        ]

    def get_episodes_count(self, obj):
        return obj.episodes.count()


class CharacterDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для персонажа"""
    origin = LocationSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    episodes = EpisodeSerializer(many=True, read_only=True)
    status_display = serializers.CharField(read_only=True)
    gender_display = serializers.CharField(read_only=True)

    class Meta:
        model = Character
        fields = [
            'id', 'api_id', 'name', 'status', 'status_display',
            'species', 'type', 'gender', 'gender_display',
            'origin', 'location', 'image', 'episodes', 'url',
            'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']


class EpisodeDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для эпизода"""
    characters = CharacterListSerializer(many=True, read_only=True)
    characters_count = serializers.SerializerMethodField()

    class Meta:
        model = Episode
        fields = [
            'id', 'api_id', 'name', 'air_date', 'episode',
            'characters', 'characters_count', 'url', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']

    def get_characters_count(self, obj):
        return obj.characters.count()


class LocationDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для локации"""
    origin_characters = CharacterListSerializer(many=True, read_only=True)
    current_characters = CharacterListSerializer(many=True, read_only=True)
    origin_characters_count = serializers.SerializerMethodField()
    current_characters_count = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            'id', 'api_id', 'name', 'type', 'dimension',
            'origin_characters', 'current_characters',
            'origin_characters_count', 'current_characters_count',
            'url', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']

    def get_origin_characters_count(self, obj):
        return obj.origin_characters.count()

    def get_current_characters_count(self, obj):
        return obj.current_characters.count()


class SearchHistorySerializer(serializers.ModelSerializer):
    """Сериализатор для истории поиска"""
    
    class Meta:
        model = SearchHistory
        fields = [
            'id', 'query', 'search_type', 'results_count', 'created'
        ]
        read_only_fields = ['created']


class SearchRequestSerializer(serializers.Serializer):
    """Сериализатор для поискового запроса"""
    q = serializers.CharField(max_length=500, required=True, source='query')
    type = serializers.ChoiceField(
        choices=['character', 'episode', 'location'],
        default='character',
        source='search_type'
    )
    page = serializers.IntegerField(min_value=1, default=1)


class CharacterFilterSerializer(serializers.Serializer):
    """Сериализатор для фильтрации персонажей"""
    name = serializers.CharField(max_length=200, required=False)
    status = serializers.ChoiceField(
        choices=['alive', 'dead', 'unknown'],
        required=False
    )
    species = serializers.CharField(max_length=100, required=False)
    gender = serializers.ChoiceField(
        choices=['female', 'male', 'genderless', 'unknown'],
        required=False
    )
    page = serializers.IntegerField(min_value=1, default=1)


class EpisodeFilterSerializer(serializers.Serializer):
    """Сериализатор для фильтрации эпизодов"""
    name = serializers.CharField(max_length=200, required=False)
    episode = serializers.CharField(max_length=20, required=False)
    page = serializers.IntegerField(min_value=1, default=1)


class LocationFilterSerializer(serializers.Serializer):
    """Сериализатор для фильтрации локаций"""
    name = serializers.CharField(max_length=200, required=False)
    type = serializers.CharField(max_length=100, required=False)
    dimension = serializers.CharField(max_length=200, required=False)
    page = serializers.IntegerField(min_value=1, default=1)
