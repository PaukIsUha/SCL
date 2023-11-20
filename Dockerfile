FROM python:3.9

RUN pip install aiogram==2.23.1

COPY . /app
COPY Labels_data.db /app

WORKDIR /app

# Запускаем бота при старте контейнера
CMD ["python", "main.py"]