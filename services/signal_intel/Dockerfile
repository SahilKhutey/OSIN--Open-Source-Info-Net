FROM python:3.11-slim

WORKDIR /app

# Install signal reconnaissance toolchain
RUN apt-get update && apt-get install -y \
    curl \
    theharvester \
    masscan \
    metagoofil \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install FOCA (Python-based metadata extractor)
RUN git clone https://github.com/ElevenPaths/FOCA.git /opt/foca \
    && cd /opt/foca \
    && pip install -r requirements.txt \
    && ln -s /opt/foca/foca.py /usr/local/bin/foca

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 8016

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8016/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8016", "--workers", "2"]
