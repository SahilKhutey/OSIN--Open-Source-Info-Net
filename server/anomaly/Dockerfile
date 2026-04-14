FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    numpy \
    scikit-learn \
    prometheus_client

COPY . .

# Expose API and Metrics ports
EXPOSE 8004
EXPOSE 8005

CMD ["python", "anomaly_service.py"]
