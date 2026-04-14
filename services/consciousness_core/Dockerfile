FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies for consciousness simulation
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.2 \
    numpy==1.24.3

COPY . .

# Add services/ to PYTHONPATH for OSINGraphBuilder access
ENV PYTHONPATH=$PYTHONPATH:/app

EXPOSE 8025

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8025/status || exit 1

CMD ["uvicorn", "main_consciousness:app", "--host", "0.0.0.0", "--port", "8025", "--workers", "1"]
