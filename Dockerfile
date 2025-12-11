FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y build-essential python3-dev gcc && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/model /app/templates

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

ENV FLASK_ENV=production
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000", "--no-debugger", "--no-reload"]
