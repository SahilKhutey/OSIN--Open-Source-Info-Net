#!/bin/bash
# OSIN Geo-Intelligence Service Deployment Script v2.1.0

set -e

echo "🛰️  Deploying OSIN Geo-Intelligence Service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
SERVICE_DIR="services/geo_intelligence"
IMAGE_NAME="osin-geo-intelligence:2.1.0"
K8S_NAMESPACE="osin"

# Function for colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl not found, skipping Kubernetes deployment"
        K8S_AVAILABLE=false
    else
        K8S_AVAILABLE=true
    fi
}

# Build Docker image
build_docker_image() {
    print_status "Building Docker image ${IMAGE_NAME}..."
    docker build -t "$IMAGE_NAME" "$SERVICE_DIR"
    
    if [ $? -eq 0 ]; then
        print_status "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    if [ "$K8S_AVAILABLE" = false ]; then
        print_warning "Skipping Kubernetes deployment"
        return
    fi
    
    print_status "Deploying to Kubernetes (Namespace: $K8S_NAMESPACE)..."
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace "$K8S_NAMESPACE" &> /dev/null; then
        kubectl create namespace "$K8S_NAMESPACE"
    fi
    
    # Apply manifests
    kubectl apply -f "$SERVICE_DIR/deployment.yaml" -n "$K8S_NAMESPACE"
    
    # Wait for rollout
    print_status "Waiting for rollout to complete..."
    kubectl rollout status deployment/osin-geo-intelligence -n "$K8S_NAMESPACE" --timeout=300s
    
    print_status "Kubernetes deployment completed"
}

# Main process
main() {
    check_prerequisites
    build_docker_image
    deploy_to_kubernetes
    
    print_status "✅ Geo-Intelligence Service v2.1.0 deployed successfully!"
    print_status "Service available internally at: http://osin-geo-intelligence.osin.svc.cluster.local:8003"
}

main "$@"
