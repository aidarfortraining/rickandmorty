# 🔍 Проверка совместимости локальной и production версий

## ✅ Что было сделано для совместимости

### 1. 🛠️ Умное определение окружения
- `build.sh` выполняет миграции только на Render.com (`$RENDER` переменная)
- Middleware включается только в production (`RENDER=1` или `DEBUG=False`)
- Локально - обычная разработка без ограничений

### 2. 📁 Раздельные скрипты
- `setup_local.py` - **ТОЛЬКО для локальной разработки**
- `build.sh` - **ТОЛЬКО для Render.com**
- `test_local.py` - проверка локальной версии

### 3. 🗄️ Безопасная работа с БД
- Локально: `db.sqlite3` в корне проекта
- Production: `/tmp/db.sqlite3` на Render.com
- Middleware не мешает локальной разработке

## 🧪 Как проверить совместимость

### Локальная проверка:
```bash
# Автоматическая проверка
python test_local.py

# Ручная проверка
python setup_local.py
python manage.py runserver
# Открыть http://localhost:8000
```

### Production проверка:
```bash
# После деплоя на Render.com
curl https://rickandmorty-n0mo.onrender.com/health/
curl "https://rickandmorty-n0mo.onrender.com/search/?q=Rick&type=character"
```

## 📋 Checklist совместимости

### ✅ Локальная разработка
- [ ] `python manage.py runserver` запускается без ошибок
- [ ] Страницы загружаются корректно
- [ ] Поиск работает
- [ ] Нет middleware ошибок
- [ ] База данных создается в корне проекта

### ✅ Production (Render.com)
- [ ] Build процесс проходит успешно
- [ ] Health check возвращает "healthy"
- [ ] Поиск работает без 500 ошибок  
- [ ] Middleware корректно проверяет БД
- [ ] База данных создается в `/tmp/`

## 🔧 Конфигурация окружений

### Локальное окружение
```python
# Автоматически определяется
DEBUG = True
RENDER = None  # не установлена
MIDDLEWARE = [...] # без DatabaseInitMiddleware
DATABASE = "db.sqlite3"  # в корне проекта
```

### Production окружение (Render.com)
```python
# Через переменные окружения
DEBUG = False
RENDER = "1" 
MIDDLEWARE = [..., 'main.middleware.DatabaseInitMiddleware']
DATABASE = "/tmp/db.sqlite3"
```

## 🚨 Важные замечания

### ❌ НЕ делайте локально:
```bash
# НЕ запускайте build.sh локально!
./build.sh  # ❌

# НЕ устанавливайте RENDER=1 локально!
export RENDER=1  # ❌
```

### ✅ Правильно локально:
```bash
# Используйте специальные скрипты
python setup_local.py  # ✅
python test_local.py   # ✅
python manage.py runserver  # ✅
```

### ✅ Правильно на Render.com:
- Автоматический деплой через git push
- `build.sh` выполняется автоматически
- `gunicorn` запускается автоматически

## 🔄 Процесс обновления

### 1. Локальная разработка
```bash
git pull origin main
python setup_local.py  # если нужно
python manage.py migrate  # если новые миграции
python manage.py runserver
```

### 2. Деплой изменений
```bash
git add .
git commit -m "Your changes"
git push origin main
# Render.com автоматически деплоит
```

### 3. Проверка после деплоя
```bash
# Проверить health
curl https://rickandmorty-n0mo.onrender.com/health/

# Проверить функциональность
open https://rickandmorty-n0mo.onrender.com/
```

## 🆘 Решение проблем

### Проблема: "Middleware ошибки локально"
**Решение**: Убедитесь что не установлена переменная `RENDER`
```bash
unset RENDER
echo $RENDER  # должно быть пусто
```

### Проблема: "База данных не найдена локально"
**Решение**: 
```bash
python manage.py migrate
# или
python setup_local.py
```

### Проблема: "500 ошибки на Render.com"
**Решение**: Проверить health check и логи
```bash
curl https://rickandmorty-n0mo.onrender.com/health/
# Проверить логи в Render Dashboard
```

## ✨ Итог

Все изменения полностью совместимы:
- 🟢 **Локальная разработка** работает как обычно
- 🟢 **Production на Render.com** работает с исправлениями
- 🟢 **Нет конфликтов** между окружениями
- 🟢 **Простой workflow** для разработчиков
