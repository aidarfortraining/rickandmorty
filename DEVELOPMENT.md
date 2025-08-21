# 🛠️ Руководство для разработчиков

## 🎯 Для новых разработчиков

### Быстрый старт
```bash
git clone <repository-url>
cd rickandmorty
python setup_local.py
python manage.py runserver
```

## 🏗️ Архитектура проекта

### Разделение окружений

Проект автоматически определяет окружение:

- **Локальная разработка**: `DEBUG=True`, SQLite в корне проекта
- **Render.com**: `RENDER=1`, SQLite в `/tmp/`, `DEBUG=False`

### Ключевые файлы

- `setup_local.py` - автоматическая настройка для разработки
- `build.sh` - build скрипт для Render.com (НЕ запускать локально)
- `debug_migration.py` - диагностика проблем с БД
- `main/middleware.py` - включается только в production

## 🔧 Команды разработки

### Основные команды
```bash
# Запуск сервера разработки
python manage.py runserver

# Создание миграций
python manage.py makemigrations
python manage.py makemigrations main

# Применение миграций
python manage.py migrate

# Синхронизация с API
python manage.py sync_data --limit 3

# Django shell
python manage.py shell

# Тесты
python manage.py test

# Сбор статики
python manage.py collectstatic
```

### Диагностика
```bash
# Проверка состояния БД
python debug_migration.py

# Health check (только после запуска сервера)
curl http://localhost:8000/health/
```

## 📊 Структура базы данных

### Модели
- `Character` - персонажи Rick and Morty
- `Episode` - эпизоды сериала  
- `Location` - локации
- `SearchHistory` - история поиска

### Связи
- Character -> Location (origin, current location)
- Character <-> Episode (many-to-many)

## 🌐 API интеграция

### Внешний API
- **URL**: https://rickandmortyapi.com/api/
- **Документация**: https://rickandmortyapi.com/documentation
- **Rate limit**: 1000 запросов/день

### Стратегия работы
1. **Первичный источник**: Внешний API
2. **Fallback**: Локальная БД при недоступности API
3. **Синхронизация**: Через `manage.py sync_data`

## 🎨 Frontend разработка

### Технологии
- Bootstrap 5 для UI
- Vanilla JavaScript (ES6+)
- CSS Custom Properties для тем

### Ключевые файлы
- `static/js/main.js` - основная логика
- `static/css/style.css` - стили и темы
- `templates/base.html` - базовый шаблон

### Особенности
- Система тем (светлая/темная)
- Skeleton loaders для лучшего UX
- Адаптивный дизайн (mobile-first)

## 🧪 Тестирование

### Локальное тестирование
```bash
# Все тесты
python manage.py test

# Конкретное приложение
python manage.py test main

# С подробным выводом
python manage.py test --verbosity=2
```

### Тестирование API
```bash
# Локально
curl http://localhost:8000/api/search/?q=Rick&type=character

# Production
curl https://rickandmorty-n0mo.onrender.com/api/search/?q=Rick&type=character
```

## 🚀 Деплой и CI/CD

### Локальная подготовка к деплою
```bash
# Проверка миграций
python manage.py makemigrations --check --dry-run

# Проверка статики
python manage.py collectstatic --dry-run

# Симуляция production настроек
DEBUG=False python manage.py check --deploy
```

### Деплой на Render.com
1. Пуш в main ветку автоматически деплоит
2. Build команда: `./build.sh`
3. Start команда: `gunicorn rick_and_morty_app.wsgi:application`

## 🔍 Отладка

### Частые проблемы

#### "Table doesn't exist"
```bash
python debug_migration.py
python manage.py migrate
```

#### "API недоступен"
```bash
# Проверка сети
curl https://rickandmortyapi.com/api/character/1

# Использование локальных данных
python manage.py sync_data --limit 1
```

#### "Static files not found"
```bash
python manage.py collectstatic --clear
```

### Логирование

#### Локально
Логи выводятся в консоль при `DEBUG=True`

#### Production (Render.com)
Логи доступны в Render Dashboard

### Инструменты разработчика

#### Django Debug Toolbar (опционально)
```bash
pip install django-debug-toolbar
# Добавить в INSTALLED_APPS в settings.py для локальной разработки
```

#### Django Extensions (опционально)
```bash
pip install django-extensions
# Добавляет команды: shell_plus, show_urls, graph_models
```

## 📝 Coding Standards

### Python
- Следуем PEP 8
- Используем type hints где возможно
- Документируем функции docstrings
- Максимальная длина строки: 100 символов

### JavaScript
- ES6+ синтаксис
- Используем const/let вместо var
- Документируем функции JSDoc комментариями

### CSS
- Mobile-first подход
- CSS Custom Properties для переменных
- БЭМ методология для классов

## 🤝 Контрибьюция

### Workflow
1. Создать feature branch от main
2. Внести изменения
3. Протестировать локально
4. Создать Pull Request
5. Code review
6. Merge в main

### Commit сообщения
```
feat: добавить новую функцию
fix: исправить баг
docs: обновить документацию
style: форматирование кода
refactor: рефакторинг без изменения функциональности
test: добавить или обновить тесты
```

## 📚 Полезные ссылки

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Rick and Morty API](https://rickandmortyapi.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Render.com Docs](https://render.com/docs)
