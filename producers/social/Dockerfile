FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY producers/social/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and shared library
COPY producers/social/social_producer.py .
COPY server/lib /app/server/lib

# Ensure library is importable
ENV PYTHONPATH=/app

CMD ["python", "social_producer.py"]
