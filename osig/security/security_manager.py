import asyncio
import base64
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

@dataclass
class SecurityAudit:
    timestamp: datetime
    event_type: str
    severity: str
    source_ip: str
    user_agent: str
    action: str
    resource: str
    outcome: str
    details: Dict[str, Any]

class MilitaryGradeSecurityManager:
    """Military-grade security implementation for OSIG"""
    
    def __init__(self):
        self.encryption_keys = {"default": secrets.token_bytes(32), "jwt_secret": secrets.token_hex(64)}
        self.audit_logger = AuditLogger()
    
    def encrypt_data(self, data: bytes, key_id: str = "default") -> Dict:
        key = self.encryption_keys[key_id]
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'tag': base64.b64encode(encryptor.tag).decode('utf-8'),
            'key_id': key_id,
            'algorithm': 'AES-256-GCM'
        }

    def decrypt_data(self, encrypted_data: Dict) -> bytes:
        key = self.encryption_keys[encrypted_data['key_id']]
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        iv = base64.b64decode(encrypted_data['iv'])
        tag = base64.b64decode(encrypted_data['tag'])
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def generate_secure_token(self, payload: Dict, expires_in: int = 3600) -> str:
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        return jwt.encode(payload, self.encryption_keys['jwt_secret'], algorithm='HS512')

class AuditLogger:
    """Security audit logging - SQLite backend"""
    def __init__(self):
        import sqlite3
        import os
        # Define base path relative to this file's location (osig/security/security_manager.py)
        # Going up 3 levels to reach the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        secure_dir = os.path.join(base_dir, 'secure', 'osig')
        os.makedirs(secure_dir, exist_ok=True)
        self.conn = sqlite3.connect(os.path.join(secure_dir, 'security_audit.db'))
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS security_events (id INTEGER PRIMARY KEY, timestamp TEXT, event_type TEXT, severity TEXT, action TEXT, details TEXT)')
        self.conn.commit()

    async def log_security_events(self, events: List[SecurityAudit]):
        cursor = self.conn.cursor()
        for e in events:
            cursor.execute('INSERT INTO security_events (timestamp, event_type, severity, action, details) VALUES (?,?,?,?,?)',
                         (e.timestamp.isoformat(), e.event_type, e.severity, e.action, json.dumps(e.details)))
        self.conn.commit()
