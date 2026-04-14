FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY server/health_monitor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/health_monitor/main.py .
COPY server/health_monitor/static/ ./static/

EXPOSE 8002
EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
