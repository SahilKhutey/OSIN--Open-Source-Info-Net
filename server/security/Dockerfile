FROM python:3.11-slim

WORKDIR /app

COPY server/security/requirements.txt . 2>/dev/null || :
# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    httpx \
    slowapi \
    prometheus_client \
    certifi

COPY . .

# Expose Gateway and Metrics ports
EXPOSE 8443
EXPOSE 8006

CMD ["python", "zero_trust_gateway.py"]
