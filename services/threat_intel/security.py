"""
Security validation utilities for OSIN Threat Intelligence
Ensures all operations are lawful and defensive
"""

import re
from typing import List, Set

class SecurityValidator:
    def __init__(self):
        self.prohibited_patterns = [
            r"\.onion$",  # Tor hidden services
            r"\.i2p$",    # I2P
            r"^192\.168\.",  # Private
            r"^10\.",        # Private
            r"^127\.",       # Localhost
            r"^localhost$"
        ]
        
        self.allowed_tlds = {
            ".com", ".org", ".net", ".io", ".ai", ".tech",
            ".edu", ".info", ".co", ".uk", ".de"
        }
    
    def validate_target(self, target: str) -> bool:
        """Validate that a target is permissible for defensive scanning"""
        for pattern in self.prohibited_patterns:
            if re.search(pattern, target, re.IGNORECASE):
                return False
        
        if not any(target.endswith(tld) for tld in self.allowed_tlds):
            return False
            
        prohibited_terms = ["login", "admin", "dashboard", "controlpanel", "internal", "private"]
        if any(term in target.lower() for term in prohibited_terms):
            return False
            
        return True
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate OSIN API key"""
        return api_key.startswith("osin_") and len(api_key) > 32
