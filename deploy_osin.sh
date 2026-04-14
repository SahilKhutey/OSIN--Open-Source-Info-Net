#!/bin/bash
# OSIN v9 - Real-Time Distributed Intelligence Deployment Script

echo "--- [OSIN v9] Orchestrating Intelligence Infrastructure ---"

# Check for .env file
if [ ! -f .env ]; then
    echo "Error: .env file not found. Pre-requisites not met."
    exit 1
fi

# Ensure Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker daemon is not running."
  exit 1
fi

# 1. Start Core Infrastructure (Kafka, Zookeeper, Neo4j)
echo "Starting Kafka & Neo4j Clusters..."
docker-compose up -d zookeeper kafka kafka-ui neo4j

# 2. Wait for Kafka to be ready
echo "Waiting for Kafka Broker initialization (30s)..."
sleep 30

# 3. Initialize Kafka Topics
echo "Initializing OSIN Message Bus Topics..."
docker-compose run --rm backend python infrastructure/topic_manager.py

# 4. Deploy Intelligence Layers
echo "Deploying Intelligent Processors (NLP, CV, Correlation)..."
docker-compose up -d nlp-processor cv-processor

# 5. Deploy Data Ingestion Layers
echo "Deploying Data Producers (Satellite, Social)..."
docker-compose up -d satellite-producer social-producer

# 6. Deploy Intelligence API
echo "Deploying OSIN Master Backend..."
docker-compose up -d backend

echo "--- [OSIN v9] Deployment Successful ---"
echo "API Endpoint: http://localhost:8000"
echo "Kafka UI: http://localhost:8080"
echo "Neo4j Browser: http://localhost:7474"
echo "----------------------------------------"
