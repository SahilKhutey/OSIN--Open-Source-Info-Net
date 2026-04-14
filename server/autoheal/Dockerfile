FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psutil and docker
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir \
    requests \
    docker \
    psutil

# Copy the specific service code
COPY ./server/autoheal/autoheal_manager.py .

# Copy shared libraries
COPY ./server/lib /app/lib

# Set PYTHONPATH to allow imports from /app/lib
ENV PYTHONPATH=/app

CMD ["python", "autoheal_manager.py"]
