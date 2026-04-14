FROM python:3.10-slim

WORKDIR /app

COPY processors/correlation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY processors/correlation/correlation_engine.py .

CMD ["python", "correlation_engine.py"]
