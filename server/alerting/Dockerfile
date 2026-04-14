FROM python:3.11-slim

WORKDIR /app

# Install python dependencies
RUN pip install --no-cache-dir \
    requests \
    psutil

# Copy the specific service code
COPY ./server/alerting/alert_manager.py .

# Copy shared libraries
COPY ./server/lib /app/lib

# Set PYTHONPATH to allow imports from /app/lib
ENV PYTHONPATH=/app

CMD ["python", "alert_manager.py"]
