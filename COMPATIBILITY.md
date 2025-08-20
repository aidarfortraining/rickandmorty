# 🔧 Совместимость и требования

## 📋 Системные требования

### Python версии
- **Рекомендуется**: Python 3.11+
- **Минимум**: Python 3.10
- **Не поддерживается**: Python 3.9 и ниже (из-за Django 5.2.5)

### Операционные системы
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Ubuntu 20.04+
- ✅ Debian 11+

## 🐍 Проверка версии Python

```bash
python --version
# Должно быть 3.10.0 или выше
```

## 🔄 Если у вас Python 3.9 или ниже

### Вариант 1: Обновить Python (рекомендуется)

**Windows:**
- Скачайте Python 3.11+ с [python.org](https://python.org)
- Установите, выбрав "Add to PATH"

**macOS (через Homebrew):**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip
```

### Вариант 2: Использовать Django 4.2 LTS

Если обновление Python невозможно, замените в `requirements.txt`:

```txt
Django==4.2.16  # вместо Django==5.2.5
```

**Примечание**: Django 4.2 - это LTS версия с поддержкой до 2026 года.

## 📦 Совместимость зависимостей

### Основные пакеты
- Django 5.2.5 → Требует Python 3.10+
- djangorestframework 3.16.1 → Совместимо с Python 3.8+
- gunicorn 23.0.0 → Совместимо с Python 3.8+

### Проблемы и решения

**Ошибка**: `ERROR: No matching distribution found for Django==5.2.5`
**Причина**: Python версия ниже 3.10
**Решение**: Обновите Python или используйте Django 4.2.16

**Ошибка**: `ImportError: cannot import name 'force_text'`
**Причина**: Устаревшие зависимости
**Решение**: Обновите все пакеты через `pip install -r requirements.txt --upgrade`

## 🐳 Docker альтернатива

Если не можете обновить Python на хосте:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

```bash
docker build -t rickandmorty .
docker run -p 8000:8000 rickandmorty
```

## ☁️ GitHub Actions

CI/CD настроен для тестирования на:
- Python 3.10
- Python 3.11  
- Python 3.12

Если ваша локальная версия отличается, это не повлияет на deployment.

## 🆘 Поддержка

Если у вас проблемы с совместимостью:

1. Проверьте версию Python: `python --version`
2. Обновите pip: `python -m pip install --upgrade pip`
3. Пересоздайте виртуальное окружение
4. Установите зависимости заново

Для быстрого решения используйте Docker или обновите Python до 3.11+.
