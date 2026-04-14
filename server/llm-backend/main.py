from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import logging
import os
from typing import List, Dict, Any
import json

app = FastAPI(title="OSIN v11 LLM & Voice Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "REPLACE_ME")
openai.api_key = OPENAI_API_KEY

class VoiceInput(BaseModel):
    text: str

class LLMQuery(BaseModel):
    text: str
    history: List[Dict[str, str]] = []
    context: Dict[str, Any] = {}

@app.post("/voice-intent")
async def parse_voice_intent(input: VoiceInput):
    """Parse voice commands into actionable intents using heuristic-first approach"""
    text = input.text.lower()
    
    # Pre-defined operational keywords
    intents = {
        "ZOOM_EARTH": ["zoom", "closer", "larger", "magnify"],
        "SHOW_THREATS": ["show threats", "display threats", "active threats", "targets"],
        "ANALYZE_NODE": ["analyze", "examine", "investigate", "details"],
        "FILTER_INTELLIGENCE": ["filter", "show only", "display only"],
        "RESET_VIEW": ["reset", "clear", "home", "restore"]
    }
    
    detected_intent = "CORE_SEARCH"
    confidence = 0.5
    
    for intent, keywords in intents.items():
        if any(keyword in text for keyword in keywords):
            detected_intent = intent
            confidence = 0.9
            break
    
    return {
        "action": detected_intent,
        "confidence": confidence,
        "original_text": input.text
    }

@app.post("/agent")
async def process_llm_query(query: LLMQuery):
    """Deep conversational analysis for the OSIN XR Assistant"""
    try:
        if OPENAI_API_KEY == "REPLACE_ME":
            return {
                "response": "SIMULATED_AI_RESPONSE: Logic active. Integrated analysis of current sector shows no immediate anomalies. Please provide API key for deep LLM reasoning.",
                "intent": "MOCK_ADVICE",
                "actions": ["SHOW_STATUS"],
                "parameters": {}
            }

        # Context-aware system prompt
        messages = [
            {
                "role": "system",
                "content": """You are OSIN XR-SENTINEL Assistant. You help analysts navigate a 3D global intelligence map.
                Your job is to provide tactical insights and control the XR environment.
                Return responses in JSON format: { "response": "...text...", "intent": "...", "actions": ["ACTION_NAME"], "parameters": {} }
                Available Actions: ZOOM_EARTH, SHOW_THREATS, ANALYZE_NODE, RESET_VIEW."""
            }
        ]
        
        messages.extend(query.history)
        messages.append({"role": "user", "content": query.text})
        
        # Call LLM
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600,
            temperature=0.6,
            response_format={ "type": "json_object" }
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        logging.error(f"LLM Error: {e}")
        return {"response": f"System Error: {str(e)}", "intent": "ERROR", "actions": []}

@app.get("/health")
async def health():
    return {"status": "online", "version": "v11.0.0"}
