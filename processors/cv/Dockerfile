FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV and psutil
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY processors/cv/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and shared library
COPY processors/cv/cv_processor.py .
COPY server/lib /app/server/lib

# Ensure library is importable
ENV PYTHONPATH=/app

CMD ["python", "cv_processor.py"]
