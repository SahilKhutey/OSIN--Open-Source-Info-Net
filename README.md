# OSIN: Open-Source Intelligence Network Ingestion Suite

A production-grade, multi-platform intelligence gathering engine designed for high-throughput, compliant, and observable data ingestion.

## 🚀 Overview

The OSIN Ingestion Suite provides modular, robust pipelines for collecting data from major social media and news platforms. Each pipeline is built with enterprise-level features including:

- **Multi-Strategy Ingestion**: Fallback mechanisms combining official APIs, browser automation (Playwright), and scraping.
- **Advanced Intelligence**: Built-in trend detection, sentiment analysis, entity extraction, and content categorization.
- **Production Observability**: Full Prometheus metrics, health checks, data quality assurance, and Grafana dashboards.
- **Cloud-Native Deployment**: Kubernetes manifests with Horizontal Pod Autoscaling (HPA) and ServiceMonitors.
- **Compliance First**: Automated rate limiting, metadata-only modes, and adherence to platform-specific policies.

## 📦 Supported Platforms

| Platform | Ingestion Strategy | Key Features |
| :--- | :--- | :--- |
| **Twitter** | snscrape + Official API | Real-time monitoring, metric tracking |
| **Reddit** | PRAW + RSS + Pushshift | Subreddit intelligence, anomaly detection |
| **YouTube** | yt-dlp + Data API v3 | Quota-aware extraction, video metadata |
| **Instagram** | Instaloader + Playwright | Non-invasive scraping, data quality checks |
| **LinkedIn** | Playwright + Proxy Rotation | Job market trends, company profiling |
| **News** | newspaper3k + RSS + GDELT | Event correlation, cross-source verification |

## 🛠️ Architecture

### Streaming & Storage
- **Kafka**: All raw data is streamed into `raw.*` topics using Strimzi-managed clusters.
- **Schema Registry**: Unified data formats across all platforms.

### Monitoring Stack
- **Prometheus**: Real-time metrics for throughput, latency, and error rates.
- **Grafana**: Pre-configured dashboards for operational visibility.
- **Alertmanager**: Critical alerting for rate limits and source degradation.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Kubernetes Cluster
- Kafka / Strimzi Operator
- Prometheus Operator

### 1. Installation
```bash
pip install -r requirements.txt
playwright install
```

### 2. Configuration
Configure platform credentials in `secure/osin/ingestion/<platform>/k8s-deployment.yaml` via ConfigMaps and Secrets.

### 3. Deployment
```bash
# Example: Deploy News Ingestion
kubectl apply -f secure/osin/ingestion/news/k8s-deployment.yaml
```

## 📜 Compliance & Ethics
This suite is designed for ethical data collection. Users are responsible for complying with platform Terms of Service and local data protection regulations. Use the `COMPLIANCE_MODE=strict` environment variable for maximum adherence to privacy standards.

---
*Developed by Antigravity for the OSINT Intelligence Community.*
