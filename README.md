Habit Tracker (Mini Project)
Веб-приложение для отслеживания привычек с REST API, фронтендом на vanilla JS и тестами pytest.

Технологический стек
Backend: Python 3.10, Flask 3.x, Flask-SQLAlchemy, Flask-CORS
База данных: SQLite
Frontend: HTML5, CSS3, JavaScript (Fetch API)
Тестирование: pytest
CI: GitHub Actions
Контейнеризация: Docker, docker-compose
Функциональность
Создание привычек с категорией и частотой (daily/weekly)
Просмотр списка привычек
Обновление полей привычки
Удаление привычки
Отметка выполнения за день (toggle)
Статистика: всего привычек, выполнено сегодня, процент выполнения, лучший streak
Структура проекта
app.py - Flask backend + API
templates/index.html - главная страница
static/style.css - стили интерфейса
static/app.js - логика фронтенда
tests/test_app.py - автотесты API
.github/workflows/ci.yml - CI pipeline
Dockerfile, docker-compose.yml - локальный запуск в контейнере
Запуск локально
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
Открыть: http://localhost:5000

Запуск тестов
pytest tests/test_app.py -v
API
GET /api/habits - список привычек
POST /api/habits - создать привычку
PUT /api/habits/<id> - обновить привычку
DELETE /api/habits/<id> - удалить привычку
PATCH /api/habits/<id>/toggle - отметить/снять отметку за сегодня
GET /api/stats - агрегированная статистика
