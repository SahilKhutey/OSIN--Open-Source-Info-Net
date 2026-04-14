FROM python:3.11-slim

WORKDIR /app

# Install advanced reconnaissance toolchain
RUN apt-get update && apt-get install -y \
    curl \
    dnsenum \
    nmap \
    dnsrecon \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Recon-ng (Professional OSINT Framework)
RUN git clone https://github.com/lanmaster53/recon-ng.git /opt/recon-ng \
    && cd /opt/recon-ng \
    && pip install -r REQUIREMENTS \
    && ln -s /opt/recon-ng/recon-ng /usr/local/bin/recon-ng

# Copy requirements and install Python SDKs
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 8015

# Health check (verify tool availability)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8015/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8015", "--workers", "2"]
