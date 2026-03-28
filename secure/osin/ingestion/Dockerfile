# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY twitter_pipeline.py .
COPY architecture.py .
COPY config.yaml .

# Create non-root user
RUN useradd -m -u 1000 twitterworker
USER twitterworker

# Start ingestion
CMD ["python", "twitter_pipeline.py"]
