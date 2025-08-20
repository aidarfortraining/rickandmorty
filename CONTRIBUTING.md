# Contributing to Rick and Morty Django Application

Спасибо за интерес к проекту! Мы приветствуем любые вклады.

## Как внести свой вклад

### Reporting Bugs

Если вы нашли баг:
1. Проверьте, что баг еще не был зарепорчен в [Issues](https://github.com/aidarfortraining/rickandmorty/issues)
2. Создайте новый issue с описанием проблемы
3. Используйте шаблон Bug Report
4. Приложите скриншоты если возможно

### Suggesting Features

Для предложения новой функциональности:
1. Проверьте, что функция не предлагалась ранее
2. Создайте Feature Request issue
3. Детально опишите предлагаемую функциональность

### Pull Requests

1. **Fork** репозиторий
2. Создайте **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** ваши изменения (`git commit -m 'Add amazing feature'`)
4. **Push** в branch (`git push origin feature/amazing-feature`)
5. Создайте **Pull Request**

### Требования к коду

- Следуйте PEP 8 для Python кода
- Добавляйте тесты для новой функциональности
- Обновляйте документацию при необходимости
- Проверьте, что все тесты проходят

### Настройка окружения разработки

```bash
# Клонируйте репозиторий
git clone https://github.com/aidarfortraining/rickandmorty.git
cd rickandmorty

# Создайте виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Выполните миграции
python manage.py migrate

# Запустите тесты
python manage.py test

# Запустите сервер
python manage.py runserver
```

## Стиль кода

- **Python**: PEP 8
- **JavaScript**: ESLint (если будет добавлен)
- **HTML**: Семантическая разметка
- **CSS**: BEM методология

## Лицензия

Внося свой вклад, вы соглашаетесь с тем, что ваши изменения будут лицензированы под MIT License.
