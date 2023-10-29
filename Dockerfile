# Используем образ Python
FROM python:3.11

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Redis
RUN apt-get update && apt-get install -y redis-server

# Устанавливаем переменную окружения для отключения вывода буферизации
ENV PYTHONUNBUFFERED 1

# Создаем директорию приложения
RUN mkdir /app

# Копируем файлы приложения в директорию
COPY . /app

WORKDIR /app

# Устанавливаем зависимости Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Устанавливаем рабочую директорию
WORKDIR /app/backend

# Запускаем Redis
RUN service redis-server start

# Выполняем миграции
RUN python manage.py makemigrations
RUN python manage.py migrate

# Запускаем приложение
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]