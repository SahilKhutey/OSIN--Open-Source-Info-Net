FROM python:3.11-slim

WORKDIR /app

# Install build essential for RTKLIB
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
    make \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone and build RTKLIB (rtkrcv)
RUN git clone https://github.com/tomojitakasu/RTKLIB.git /tmp/RTKLIB \
    && cd /tmp/RTKLIB/app/consapp/rtkrcv \
    && make \
    && cp rtkrcv /usr/local/bin/ \
    && rm -rf /tmp/RTKLIB

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy config and app
COPY rtk.conf /app/rtk.conf
COPY . .

EXPOSE 8013

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8013/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8013", "--workers", "2"]
