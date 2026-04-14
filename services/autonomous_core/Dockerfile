FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.2 \
    numpy==1.24.3 \
    scikit-learn==1.3.0 \
    psutil==5.9.5 \
    openai==0.28.0 \
    networkx==3.1

COPY . .

# Add services/ to PYTHONPATH for OSINGraphBuilder access
ENV PYTHONPATH=$PYTHONPATH:/app

EXPOSE 8022

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8022/status || exit 1

CMD ["uvicorn", "main_autonomous:app", "--host", "0.0.0.0", "--port", "8022", "--workers", "1"]
