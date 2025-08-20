from django.db import models
from django.urls import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class Location(models.Model):
    """Модель для локаций из Rick and Morty"""
    api_id = models.IntegerField(unique=True, help_text="ID из Rick and Morty API")
    name = models.CharField(max_length=200, help_text="Название локации")
    type = models.CharField(max_length=100, blank=True, help_text="Тип локации")
    dimension = models.CharField(max_length=200, blank=True, help_text="Измерение")
    url = models.URLField(blank=True, help_text="URL в API")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('location-detail', kwargs={'pk': self.pk})


class Episode(models.Model):
    """Модель для эпизодов Rick and Morty"""
    api_id = models.IntegerField(unique=True, help_text="ID из Rick and Morty API")
    name = models.CharField(max_length=200, help_text="Название эпизода")
    air_date = models.CharField(max_length=100, blank=True, help_text="Дата выхода")
    episode = models.CharField(max_length=20, blank=True, help_text="Номер эпизода (например, S01E01)")
    url = models.URLField(blank=True, help_text="URL в API")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Эпизод"
        verbose_name_plural = "Эпизоды"
        ordering = ['episode']

    def __str__(self):
        return f"{self.episode} - {self.name}"

    def get_absolute_url(self):
        return reverse('episode-detail', kwargs={'pk': self.pk})


class Character(models.Model):
    """Модель для персонажей Rick and Morty"""
    
    STATUS_CHOICES = [
        ('alive', 'Живой'),
        ('dead', 'Мертвый'),
        ('unknown', 'Неизвестно'),
    ]
    
    GENDER_CHOICES = [
        ('female', 'Женский'),
        ('male', 'Мужской'),
        ('genderless', 'Бесполый'),
        ('unknown', 'Неизвестно'),
    ]

    api_id = models.IntegerField(unique=True, help_text="ID из Rick and Morty API")
    name = models.CharField(max_length=200, help_text="Имя персонажа")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='unknown',
        help_text="Статус персонажа"
    )
    species = models.CharField(max_length=100, blank=True, help_text="Вид")
    type = models.CharField(max_length=100, blank=True, help_text="Подтип/вариация")
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='unknown',
        help_text="Пол персонажа"
    )
    origin = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='origin_characters',
        help_text="Место происхождения"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_characters',
        help_text="Текущее местоположение"
    )
    image = models.URLField(blank=True, help_text="URL изображения персонажа")
    episodes = models.ManyToManyField(
        Episode,
        blank=True,
        related_name='characters',
        help_text="Эпизоды с участием персонажа"
    )
    url = models.URLField(blank=True, help_text="URL в API")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('character-detail', kwargs={'pk': self.pk})

    @property
    def status_display(self):
        """Возвращает человекочитаемое название статуса"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def gender_display(self):
        """Возвращает человекочитаемое название пола"""
        return dict(self.GENDER_CHOICES).get(self.gender, self.gender)
    
    def clean(self):
        """Дополнительная валидация"""
        super().clean()
        
        # Валидация изображения URL
        if self.image:
            url_validator = URLValidator()
            try:
                url_validator(self.image)
            except ValidationError:
                raise ValidationError({'image': 'Некорректный URL изображения'})
        
        # Валидация API URL
        if self.url:
            url_validator = URLValidator()
            try:
                url_validator(self.url)
            except ValidationError:
                raise ValidationError({'url': 'Некорректный API URL'})


class SearchHistory(models.Model):
    """Модель для хранения истории поисковых запросов"""
    query = models.CharField(max_length=500, help_text="Поисковый запрос")
    search_type = models.CharField(
        max_length=20,
        choices=[
            ('character', 'Персонаж'),
            ('episode', 'Эпизод'),
            ('location', 'Локация'),
        ],
        help_text="Тип поиска"
    )
    results_count = models.IntegerField(default=0, help_text="Количество найденных результатов")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "История поиска"
        verbose_name_plural = "История поиска"
        ordering = ['-created']

    def __str__(self):
        return f"{self.query} ({self.search_type})"