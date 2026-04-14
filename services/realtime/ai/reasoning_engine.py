"""
AI Reasoning Engine with LLM Integration
Graph-based intelligence synthesis and narrative generation
"""

import openai
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

class AIReasoningEngine:
    def __init__(self, entity_store, relationship_engine, openai_api_key: str):
        self.entity_store = entity_store
        self.relationship_engine = relationship_engine
        openai.api_key = openai_api_key
        self.logger = logging.getLogger("osin-ai-reasoning")
    
    async def analyze_context(self, entity_id: str, query: Optional[str] = None) -> str:
        """Analyze graph context around an entity using GPT-4o-mini"""
        # 1. Build context from graph (Entity + Neighbors)
        context = self._build_context(entity_id)
        if not context:
            return "Entity not found in graph."
            
        # 2. Build Prompt
        prompt = self._create_prompt(context, query)
        
        # 3. Call LLM
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are OSIN, a high-level strategic intelligence reasoning engine."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM Reasoning failed: {e}")
            return f"Reasoning Error: {str(e)}"

    def _build_context(self, entity_id: str) -> Optional[Dict]:
        entity = self.entity_store.get_entity(entity_id)
        if not entity: return None
        
        relationships = self.relationship_engine.get_relationships(entity_id=entity_id)
        return {
            "focus_entity": entity,
            "relationships": [
                {"type": r.type.value, "target": r.target_id, "confidence": r.confidence}
                for r in relationships[:10]
            ]
        }

    def _create_prompt(self, context: Dict, query: Optional[str]) -> str:
        base = f"Analyze the following intelligence cluster:\n{json.dumps(context, indent=2, default=str)}\n\n"
        if query: base += f"Specific Request: {query}\n"
        base += "Provide a summary of causal relationships, identified risks, and recommended investigative actions."
        return base
