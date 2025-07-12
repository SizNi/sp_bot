# Telegram Bot with Web App

Телеграм-бот с веб-приложением, включающим интерактивную карту и таблицы рейтинга.

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env на основе .env.example и заполните необходимые переменные окружения:
```bash
cp .env.example .env
```

5. Создайте базу данных PostgreSQL и обновите DATABASE_URL в файле .env

6. Примените миграции базы данных:
```bash
alembic upgrade head
```

## Запуск

1. Запустите бота:
```bash
python app/bot/main.py
```

2. Запустите веб-приложение:
```bash
uvicorn app.web.main:app --reload
```

## Структура проекта

```
├── alembic/              # Миграции базы данных
├── app/
│   ├── bot/             # Код телеграм-бота
│   ├── database/        # Модели и конфигурация базы данных
│   └── web/             # Веб-приложение (FastAPI)
├── .env.example         # Пример конфигурации
├── requirements.txt     # Зависимости проекта
└── README.md           # Документация
``` 