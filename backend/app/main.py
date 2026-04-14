from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
import logging
import os
import json
import asyncio
from kafka import KafkaConsumer
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OSIN v9 Intelligence Backend")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Infrastructure Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://osin-graph:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Blind Mode (Simulation) Flag
BLIND_MODE = os.getenv("OSIN_BLIND_MODE", "false").lower() == "true"

# Infrastructure Drivers
driver = None

def get_neo4j_driver():
    global driver
    if not driver:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return driver

class IntelligenceOrchestrator:
    def __init__(self):
        self.consumer = None
        
    async def start_consumer(self):
        """Background task to consume and index intelligence"""
        if BLIND_MODE:
            logger.info("OSIN BLIND MODE ACTIVE: Skipping Kafka infrastructure initialization.")
            return

        while not self.consumer:
            try:
                self.consumer = KafkaConsumer(
                    "osin.processed.nlp", "osin.processed.cv", "osin.intelligence.correlations",
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                    group_id='osin-backend-group'
                )
                logger.info("Kafka Consumer connected to intelligence streams")
            except Exception as e:
                logger.warning(f"Waiting for Kafka in Backend... {e}")
                await asyncio.sleep(5)

        for message in self.consumer:
            try:
                data = message.value
                topic = message.topic
                
                with get_neo4j_driver().session() as session:
                    if "processed" in topic:
                        # Index a processed event node
                        session.execute_write(self._create_event_node, data)
                        logger.info(f"Indexed Event: {data.get('original_id')}")
                    elif "correlations" in topic:
                        # Create correlation relationship
                        session.execute_write(self._create_correlation, data)
                        logger.info(f"Connected Intelligence: {data.get('event_a')} <-> {data.get('event_b')}")
                        
            except Exception as e:
                logger.error(f"Error indexing intelligence: {e}")

    @staticmethod
    def _create_event_node(tx, data):
        query = (
            "MERGE (e:Event {id: $id}) "
            "SET e.source = $source, e.type = $type, e.timestamp = $timestamp, e.intelligence = $intel "
            "RETURN e"
        )
        tx.run(query, id=data.get('original_id'), source=data.get('source'), 
               type=data.get('processed_type'), timestamp=data.get('timestamp'),
               intel=json.dumps(data.get('intelligence')))

    @staticmethod
    def _create_correlation(tx, data):
        query = (
            "MATCH (a:Event {id: $id_a}), (b:Event {id: $id_b}) "
            "MERGE (a)-[r:CORRELATED_WITH {confidence: $confidence, reasons: $reasons}]-(b) "
            "RETURN r"
        )
        tx.run(query, id_a=data.get('event_a'), id_b=data.get('event_b'),
               confidence=data.get('confidence'), reasons=data.get('reasons'))

orchestrator = IntelligenceOrchestrator()

@app.on_event("startup")
async def startup_event():
    # Start the intelligence consumer in the background
    asyncio.create_task(orchestrator.start_consumer())

@app.get("/")
async def root():
    return {"status": "OSIN v9 Live", "components": ["Kafka", "Neo4j", "GraphIntelligence"]}

@app.get("/intelligence/graph")
async def get_graph_summary():
    """Returns metrics from the intelligence graph (supports Blind Mode)"""
    if BLIND_MODE:
        return {
            "total_events": 142,
            "total_correlations": 89,
            "status": "SIMULATED",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    try:
        with get_neo4j_driver().session() as session:
            result = session.run("MATCH (n:Event) RETURN count(n) as count")
            event_count = result.single()["count"]
            
            result = session.run("MATCH ()-[r:CORRELATED_WITH]->() RETURN count(r) as count")
            corr_count = result.single()["count"]
            
            return {
                "total_events": event_count,
                "total_correlations": corr_count,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {"error": str(e)}

@app.post("/intelligence/search")
async def search_intelligence(query: str):
    """Placeholder for graph-based semantic search"""
    return {"query": query, "results": [], "note": "Vector search integration pending"}
