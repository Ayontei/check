# Используем официальный Python образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry==2.3.2

# Копируем файлы с зависимостями
COPY pyproject.toml poetry.lock* ./

# Настраиваем Poetry: не создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Устанавливаем только зависимости, без проекта
RUN poetry install --only main --no-root

# Копируем остальные файлы проекта
COPY . .

# Указываем порт
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]