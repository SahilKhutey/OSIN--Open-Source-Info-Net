FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies for cognitive modeling
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.2 \
    numpy==1.24.3 \
    scikit-learn==1.3.0 \
    sentence-transformers==2.2.2 \
    lmdb==1.4.1 \
    transformers==4.35.2 \
    torch --index-url https://download.pytorch.org/whl/cpu

COPY . .

# Add services/ to PYTHONPATH for OSINGraphBuilder access
ENV PYTHONPATH=$PYTHONPATH:/app

EXPOSE 8023

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:8023/status || exit 1

CMD ["uvicorn", "main_learning:app", "--host", "0.0.0.0", "--port", "8023", "--workers", "1"]
