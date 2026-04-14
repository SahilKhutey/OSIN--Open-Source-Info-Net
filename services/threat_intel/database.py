"""
OSIN Threat Intelligence Database Integration
"""

from typing import Dict, List, Optional
from datetime import datetime
import sqlite3
import json
import os

class OSINDatabase:
    def __init__(self, db_path: str = "osin_threat_intel.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    threat_score REAL NOT NULL,
                    threat_level TEXT NOT NULL,
                    components TEXT NOT NULL,
                    correlations TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def store_threat_assessment(self, assessment: Dict):
        """Store threat assessment in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO threat_assessments 
                (target, timestamp, threat_score, threat_level, components, correlations, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment["target"],
                    assessment["timestamp"],
                    assessment["threat_score"],
                    assessment["threat_level"],
                    json.dumps(assessment["components"]),
                    json.dumps(assessment["correlations"]),
                    json.dumps(assessment["recommendations"])
                )
            )
            conn.commit()

    def get_history(self, target: str, limit: int = 10) -> List[Dict]:
        """Get assessment history for a target"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM threat_assessments WHERE target = ? ORDER BY created_at DESC LIMIT ?",
                (target, limit)
            )
            return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
