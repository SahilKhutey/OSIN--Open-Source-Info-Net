#!/bin/bash
# OSIN Deduplication Service Deployment Script v2.1.0

set -e

echo "🚀 Deploying OSIN Deduplication Service v2.1.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
SERVICE_DIR="services/deduplication"
DOCKER_IMAGE="osin-deduplication:2.1.0"
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
    
    # Check if kubectl is installed (optional but recommended for full deployment)
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl not found, skipping Kubernetes deployment"
        K8S_AVAILABLE=false
    else
        K8S_AVAILABLE=true
    fi
    
    return 0
}

# Build Docker image
build_docker_image() {
    print_status "Building Docker image ${DOCKER_IMAGE}..."
    
    # We assume we are in the project root
    docker build -t "$DOCKER_IMAGE" "$SERVICE_DIR"
    
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
        print_warning "Skipping Kubernetes deployment due to missing kubectl"
        return
    fi
    
    print_status "Deploying to Kubernetes in namespace: $K8S_NAMESPACE"
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace "$K8S_NAMESPACE" &> /dev/null; then
        print_status "Creating namespace $K8S_NAMESPACE..."
        kubectl create namespace "$K8S_NAMESPACE"
    fi
    
    # Apply deployment and service
    kubectl apply -f "$SERVICE_DIR/deployment.yaml" -n "$K8S_NAMESPACE"
    
    # Wait for deployment to be ready (300s timeout for ML model loading)
    print_status "Waiting for pods to be ready (this may take up to 5 minutes)..."
    kubectl rollout status deployment/osin-deduplication -n "$K8S_NAMESPACE" --timeout=300s
    
    print_status "Kubernetes deployment completed successfully"
}

# Run local verification tests
run_verification() {
    print_status "Running local verification tests..."
    
    # Check if a local instance is running for testing
    if curl -s http://localhost:8002/health &> /dev/null; then
        print_status "Local service detected, running tests..."
        if python -m pytest tests/test_deduplication.py -v; then
            print_status "Tests passed successfully"
        else
            print_error "Tests failed"
            exit 1
        fi
    else
        print_warning "Local service not running at http://localhost:8002. Skipping local tests."
        print_status "Note: You can start the service locally with: uvicorn services.deduplication.main:app --port 8002"
    fi
}

# Main deployment process
main() {
    check_prerequisites
    
    # Build
    build_docker_image
    
    # Test (Optional - depends on local environment)
    run_verification
    
    # Deploy
    deploy_to_kubernetes
    
    print_status "✅ OSIN Deduplication Engine v2.1.0 deployment completed!"
    print_status "Endpoints (if port-forwarded):"
    print_status "  - Health: http://localhost:8002/health"
    print_status "  - Metrics: http://localhost:8002/metrics"
    print_status "  - API Docs: http://localhost:8002/docs"
}

# Execute main function
main "$@"
