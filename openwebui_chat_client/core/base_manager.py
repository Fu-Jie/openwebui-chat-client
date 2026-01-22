"""
Base Manager for OpenWebUI Chat Client.
Provides unified dependency injection pattern for all service managers.
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from openwebui_chat_client.core.base_client import BaseClient

logger = logging.getLogger(__name__)


class BaseManager:
    """
    Base class for all service managers.
    
    Provides:
    - Unified dependency injection pattern
    - Common logging utilities
    - Access to base client functionality
    """
    
    def __init__(self, base_client: "BaseClient"):
        """
        Initialize the base manager.
        
        Args:
            base_client: The base client instance providing core functionality
        """
        self.base_client = base_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug(f"Initialized {self.__class__.__name__}")
    
    @property
    def session(self):
        """Access to HTTP session from base client."""
        return self.base_client.session
    
    @property
    def base_url(self) -> str:
        """Access to base URL from base client."""
        return self.base_client.base_url
    
    @property
    def json_headers(self):
        """Access to JSON headers from base client."""
        return self.base_client.json_headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> Optional[Any]:
        """
        Make an HTTP request through the base client.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response data or None on failure
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Return JSON if available
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            return response.text
            
        except Exception as e:
            self.logger.error(f"Request to {endpoint} failed: {e}")
            return None
    
    def _log_operation(self, operation: str, **context: Any) -> None:
        """
        Log an operation with context.
        
        Args:
            operation: Operation description
            **context: Additional context information
        """
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        self.logger.info(f"{operation} [{context_str}]")
