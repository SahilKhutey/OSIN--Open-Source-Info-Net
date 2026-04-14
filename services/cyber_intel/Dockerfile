FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for cyber reconnaissance
RUN apt-get update && apt-get install -y \
    curl \
    whois \
    nmap \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Amass (via binary download for precision)
RUN curl -L https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_linux_amd64.zip -o amass.zip \
    && apt-get install -y unzip && unzip amass.zip && mv amass_linux_amd64/amass /usr/local/bin/ \
    && rm -rf amass.zip amass_linux_amd64

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 8014

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8014/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8014", "--workers", "2"]
