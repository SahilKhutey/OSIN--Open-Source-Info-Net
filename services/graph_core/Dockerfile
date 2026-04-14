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
    networkx==3.1 \
    numpy==1.24.3 \
    scikit-learn==1.3.0 \
    sentence-transformers==2.2.2 \
    scipy==1.10.1

# Pre-download MiniLM model (Optional, omitted for speed in dev)
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8020

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8020/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8020", "--workers", "2"]
