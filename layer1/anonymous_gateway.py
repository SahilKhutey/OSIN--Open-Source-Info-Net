import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from architecture.privacy_core import PRIVACY_LEVELS

@dataclass
class EphemeralSession:
    """Temporary session without persistence"""
    session_id: str
    created_at: float
    expires_at: float
    privacy_level: str
    client_fingerprint: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class AnonymousGateway:
    """Stateless anonymous access gateway for OSIN"""
    
    def __init__(self):
        self.sessions = {}  # In-memory only
        self.session_ttl = 3600
        self.max_sessions = 10000
        
    def create_session(self, request_metadata: Dict) -> EphemeralSession:
        client_fingerprint = self._generate_anonymous_fingerprint(request_metadata)
        privacy_level = self._determine_privacy_level(request_metadata)
        
        session = EphemeralSession(
            session_id=hashlib.sha256(str(time.time()).encode()).hexdigest(),
            created_at=time.time(),
            expires_at=time.time() + self.session_ttl,
            privacy_level=privacy_level,
            client_fingerprint=client_fingerprint,
            metadata={
                'user_agent_hash': self._hash_user_agent(request_metadata.get('user_agent')),
                'privacy_features': PRIVACY_LEVELS[privacy_level].features
            }
        )
        self._store_session(session)
        return session
    
    def _generate_anonymous_fingerprint(self, metadata: Dict) -> str:
        fingerprint_data = {
            'ua_hash': self._hash_user_agent(metadata.get('user_agent')),
            'lang': metadata.get('accept_language', 'en'),
            'tz': metadata.get('timezone', 'UTC')
        }
        return hashlib.sha256(str(sorted(fingerprint_data.items())).encode()).hexdigest()[:16]
    
    def _hash_user_agent(self, user_agent: Optional[str]) -> str:
        if not user_agent: return 'unknown'
        # Simple extraction of browser/os for low-friction fingerprinting
        return hashlib.sha256(user_agent.lower().split('/')[0].encode()).hexdigest()[:8]
    
    def _determine_privacy_level(self, metadata: Dict) -> str:
        if metadata.get('via_tor'): return 'TOR'
        if metadata.get('dnt') == '1': return 'ENHANCED'
        return 'PUBLIC'
    
    def _store_session(self, session: EphemeralSession):
        self._cleanup_expired_sessions()
        if len(self.sessions) >= self.max_sessions:
            oldest = sorted(self.sessions.items(), key=lambda x: x[1].created_at)[0][0]
            del self.sessions[oldest]
        self.sessions[session.session_id] = session
    
    def _cleanup_expired_sessions(self):
        expired = [sid for sid, sess in self.sessions.items() if sess.is_expired]
        for sid in expired: del self.sessions[sid]

    def validate_request(self, session_id: str, request_data: Dict) -> bool:
        if session_id not in self.sessions: return False
        session = self.sessions[session_id]
        if session.is_expired:
            del self.sessions[session_id]
            return False
        return session.client_fingerprint == self._generate_anonymous_fingerprint(request_data)
