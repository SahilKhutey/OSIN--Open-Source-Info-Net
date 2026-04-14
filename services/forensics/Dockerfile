FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for forensic tools
RUN apt-get update && apt-get install -y \
    curl \
    libimage-exiftool-perl \
    binwalk \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python-specific forensic helpers
RUN pip install exiflooter

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Ensure binaries are available
RUN exiftool -ver && binwalk --version

EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8010/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "2"]
