FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for psutil
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY producers/satellite/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and shared library
COPY producers/satellite/satellite_producer.py .
COPY server/lib /app/server/lib

# Ensure library is importable
ENV PYTHONPATH=/app

CMD ["python", "satellite_producer.py"]
