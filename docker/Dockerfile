# syntax=docker/dockerfile:1

# Base setup for python environment
FROM python:3.10-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ==============================================================================
# Backend build stage
# ==============================================================================
FROM base AS backend

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY uploads /app/uploads
COPY logs /app/logs

EXPOSE 8000
WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# ==============================================================================
# Frontend build stage
# ==============================================================================
FROM base AS frontend

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir streamlit==1.35.0

COPY frontend /app/frontend

EXPOSE 8501
WORKDIR /app/frontend

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
