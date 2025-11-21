Django-приложение для работы с базой данных SQLite

# Требования
- Python: 3.8+
- pip: 20.0+
# Установка
1. Скопировать `.env.example` в `.env` и настроить переменные.
2. Собрать и запустить сервисы:
   ```
   docker-compose build
   docker-compose up -d
   ```
3. Провести миграции и собрать статические файлы:
   ```
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py collectstatic
   ```
4. Открыть приложение на `http://localhost:8000/`

   

