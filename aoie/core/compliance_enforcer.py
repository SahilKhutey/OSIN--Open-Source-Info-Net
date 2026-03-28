import functools
import logging
from typing import Any, Callable, Dict, List, Optional
from .philosophy import AOIEPrinciples

# Configure AOIE Compliance Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AOIE-Compliance")

class ComplianceViolationError(Exception):
    """Raised when an ingestion task attempts to access a prohibited source"""
    pass

class ComplianceEnforcer:
    """
    Automated Legal & Ethical Compliance Enforcer for AOIE.
    Uses decorators to wrap ingestion functions and validate sources.
    """
    
    def __init__(self):
        self.principles = AOIEPrinciples()
        self.audit_log: List[Dict[str, Any]] = []

    def validate_source_access(self, source: str):
        """
        Validates if a source is permitted under AOIE guidelines.
        """
        is_legal = self.principles.validate_source(source)
        
        # Check against prohibited activities (string matching for safety)
        is_prohibited = any(
            p.lower() in source.lower() 
            for p in self.principles.PROHIBITED_ACTIVITIES.keys()
        )
        
        if not is_legal or is_prohibited:
            error_msg = f"COMPLIANCE VIOLATION: Source '{source}' is prohibited or not in the legal whitelist."
            logger.error(error_msg)
            self._log_audit(source, "REJECTED", error_msg)
            raise ComplianceViolationError(error_msg)
            
        self._log_audit(source, "APPROVED")
        logger.info(f"Compliance Check Passed: Source '{source}'")

    def _log_audit(self, source: str, status: str, detail: str = ""):
        """Maintains an internal immutable-style audit trail for the session"""
        entry = {
            "timestamp": logging.time.strftime("%Y-%m-%dT%H:%M:%SZ", logging.time.gmtime()),
            "source": source,
            "status": status,
            "detail": detail
        }
        self.audit_log.append(entry)

    @staticmethod
    def enforce_compliance(source_arg_index: int = 0):
        """
        Decorator to enforce AOIE compliance on ingestion methods.
        
        Args:
            source_arg_index: The index of the argument representing the data source.
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                enforcer = ComplianceEnforcer()
                
                # Extract source name from args or kwargs
                source = args[source_arg_index] if len(args) > source_arg_index else kwargs.get('source')
                
                if not source:
                    logger.warning(f"Compliance check skipped for {func.__name__}: No source provided.")
                    return await func(*args, **kwargs)

                # Validate source before execution
                enforcer.validate_source_access(str(source))
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Returns the current session's compliance audit trail"""
        return self.audit_log
