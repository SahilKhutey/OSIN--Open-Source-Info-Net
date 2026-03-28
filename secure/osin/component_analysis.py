# FILE: secure/osin/component_analysis.py
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class MaturityLevel(Enum):
    EXPERIMENTAL = 1
    STABLE = 2
    PRODUCTION = 3
    ENTERPRISE = 4

@dataclass
class ComponentAnalysis:
    """Detailed analysis of OSS components"""
    name: str
    github_stars: int
    language: str
    license: str
    maturity: MaturityLevel
    use_case: str
    pros: List[str]
    cons: List[str]
    integration_effort: int  # 1-10 scale

# INGESTION COMPONENTS ANALYSIS
INGESTION_COMPONENTS = {
    'twitter': [
        ComponentAnalysis(
            name="snscrape",
            github_stars=5300,
            language="Python",
            license="GPL-3.0",
            maturity=MaturityLevel.PRODUCTION,
            use_case="Twitter scraping without API limits",
            pros=["No rate limits", "Comprehensive data", "Active development"],
            cons=["Legal gray area", "Requires maintenance"],
            integration_effort=3
        ),
        ComponentAnalysis(
            name="Tweepy",
            github_stars=11100,
            language="Python", 
            license="MIT",
            maturity=MaturityLevel.ENTERPRISE,
            use_case="Official Twitter API wrapper",
            pros=["Legal", "Stable", "Good documentation"],
            cons=["API rate limits", "Costly at scale"],
            integration_effort=2
        )
    ],
    
    'instagram': [
        ComponentAnalysis(
            name="instaloader",
            github_stars=12000,
            language="Python",
            license="MIT",
            maturity=MaturityLevel.PRODUCTION,
            use_case="Instagram scraping",
            pros=["Comprehensive", "Resilient", "Good community"],
            cons=["Frequent breakages", "Anti-bot challenges"],
            integration_effort=5
        )
    ],
    
    'youtube': [
        ComponentAnalysis(
            name="yt-dlp",
            github_stars=153000,
            language="Python",
            license="Unlicense",
            maturity=MaturityLevel.ENTERPRISE,
            use_case="YouTube video & metadata download",
            pros=["Extremely robust", "Massive community", "Regular updates"],
            cons=["Legal considerations", "Large dependencies"],
            integration_effort=3
        )
    ],
    
    'reddit': [
        ComponentAnalysis(
            name="PRAW",
            github_stars=4100,
            language="Python",
            license="BSD-2-Clause",
            maturity=MaturityLevel.ENTERPRISE,
            use_case="Official Reddit API wrapper",
            pros=["Official support", "Reliable", "Good docs"],
            cons=["Rate limited", "Some data restricted"],
            integration_effort=2
        )
    ]
}

# STREAMING & PROCESSING ANALYSIS
STREAMING_COMPONENTS = {
    'kafka_operators': [
        ComponentAnalysis(
            name="Strimzi",
            github_stars=5800,
            language="Java",
            license="Apache-2.0",
            maturity=MaturityLevel.ENTERPRISE,
            use_case="Kubernetes-native Kafka operator",
            pros=["Production-ready", "K8s native", "Comprehensive"],
            cons=["Complex setup", "Java ecosystem"],
            integration_effort=6
        ),
        ComponentAnalysis(
            name="Redpanda",
            github_stars=12000,
            language="C++",
            license="BSL",
            maturity=MaturityLevel.PRODUCTION,
            use_case="Kafka-compatible streaming",
            pros=["High performance", "Simpler operation", "Modern"],
            cons=["Less mature ecosystem", "Proprietary features"],
            integration_effort=4
        )
    ],
    
    'stream_processing': [
        ComponentAnalysis(
            name="Apache Flink",
            github_stars=25900,
            language="Java/Scala",
            license="Apache-2.0",
            maturity=MaturityLevel.ENTERPRISE,
            use_case="Real-time stream processing",
            pros=["Industry standard", "Powerful", "Scalable"],
            cons=["Java ecosystem", "Steep learning curve"],
            integration_effort=8
        ),
        ComponentAnalysis(
            name="Faust",
            github_stars=1900,
            language="Python",
            license="BSD-3-Clause",
            maturity=MaturityLevel.PRODUCTION,
            use_case="Python stream processing",
            pros=["Python native", "Kafka integration", "Simplicity"],
            cons=["Less powerful than Flink", "Smaller community"],
            integration_effort=4
        )
    ]
}

# INTELLIGENCE STORAGE ANALYSIS
STORAGE_COMPONENTS = {
    'vector_dbs': [
        ComponentAnalysis(
            name="Qdrant",
            github_stars=29900,
            language="Rust",
            license="Apache-2.0",
            maturity=MaturityLevel.PRODUCTION,
            use_case="High-performance vector search",
            pros=["Fast", "Rust performance", "Good API"],
            cons=["Less mature", "Smaller ecosystem"],
            integration_effort=4
        ),
        ComponentAnalysis(
            name="Weaviate",
            github_stars=15900,
            language="Go",
            license="BSD-3-Clause",
            maturity=MaturityLevel.PRODUCTION,
            use_case="Vector search with GraphQL",
            pros=["GraphQL interface", "Hybrid search", "Good docs"],
            cons=["Complex setup", "Resource intensive"],
            integration_effort=5
        ),
        ComponentAnalysis(
            name="pgvector",
            github_stars=20500,
            language="C",
            license="PostgreSQL License",
            maturity=MaturityLevel.PRODUCTION,
            use_case="PostgreSQL vector extension",
            pros=["PostgreSQL integration", "Simple", "Reliable"],
            cons=["Less specialized", "Performance limits"],
            integration_effort=3
        )
    ],
    
    'graph_dbs': [
        ComponentAnalysis(
            name="ArangoDB",
            github_stars=14100,
            language="C++",
            license="Apache-2.0",
            maturity=MaturityLevel.ENTERPRISE,
            use_case="Multi-model database (document + graph)",
            pros=["Flexible", "Good performance", "SQL-like queries"],
            cons=["Complexity", "Smaller community"],
            integration_effort=6
        ),
        ComponentAnalysis(
            name="JanusGraph",
            github_stars=5700,
            language="Java",
            license="Apache-2.0",
            maturity=MaturityLevel.PRODUCTION,
            use_case="Scalable graph database",
            pros=["TinkerPop compatible", "Scalable", "Open source"],
            cons=["Complex setup", "Java ecosystem"],
            integration_effort=7
        )
    ]
}

# AI/ML COMPONENTS ANALYSIS
AI_COMPONENTS = {
    'nlp_frameworks': [
        ComponentAnalysis(
            name="HuggingFace Transformers",
            github_stars=100000,  # Approximate
            language="Python",
            license="Apache-2.0",
            maturity=MaturityLevel.ENTERPRISE,
            use_case="State-of-the-art NLP models",
            pros=["SOTA models", "Easy API", "Massive community"],
            cons=["Large models", "GPU requirements"],
            integration_effort=3
        )
    ],
    
    'multimodal_ai': [
        ComponentAnalysis(
            name="OpenAI Whisper",
            github_stars=96700,
            language="Python",
            license="MIT",
            maturity=MaturityLevel.PRODUCTION,
            use_case="Speech-to-text transcription",
            pros=["High accuracy", "Multiple languages", "Easy use"],
            cons=["Computationally intensive", "Large models"],
            integration_effort=4
        ),
        ComponentAnalysis(
            name="OpenCV",
            github_stars=66900,
            language="C++/Python",
            license="Apache-2.0",
            maturity=MaturityLevel.ENTERPRISE,
            use_case="Computer vision processing",
            pros=["Comprehensive", "Fast", "Great community"],
            cons=["Steep learning curve", "C++ complexity"],
            integration_effort=5
        ),
        ComponentAnalysis(
            name="DeepFace",
            github_stars=30400,
            language="Python",
            license="MIT",
            maturity=MaturityLevel.PRODUCTION,
            use_case="Face recognition and analysis",
            pros=["Easy to use", "Multiple backends", "Good accuracy"],
            cons=["Ethical considerations", "Privacy concerns"],
            integration_effort=3
        )
    ]
}

# COMPONENT SELECTION MATRIX
# Recommended Stack by Use Case
RECOMMENDED_STACK_MATRIX = {
    'Twitter Ingestion': ('snscrape', 'Tweepy API', 'No limits vs official API'),
    'Instagram': ('instaloader', 'Custom playwright', 'Most robust solution'),
    'YouTube': ('yt-dlp', 'youtube-dl', 'More active development'),
    'Streaming': ('Apache Kafka + Strimzi', 'Redpanda', 'Industry standard'),
    'Processing': ('Apache Flink', 'Faust', 'Enterprise capability'),
    'Vector DB': ('Qdrant', 'Weaviate', 'Performance balance'),
    'Graph DB': ('ArangoDB', 'JanusGraph', 'Multi-model flexibility'),
    'NLP': ('HuggingFace', 'spaCy', 'SOTA models'),
    'Speech': ('Whisper', 'SpeechRecognition', 'Best accuracy'),
    'Vision': ('OpenCV + DeepFace', 'MediaPipe', 'Comprehensive')
}
