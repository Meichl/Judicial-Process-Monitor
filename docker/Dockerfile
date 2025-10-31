FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Expose porta
EXPOSE 8000

# Comando padrão
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---

# docker/Dockerfile.worker
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando para Celery worker
CMD ["celery", "-A", "src.workers.tasks", "worker", "--loglevel=info", "--concurrency=4"]