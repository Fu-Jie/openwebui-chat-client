"""
Asynchronous base client for the OpenWebUI Chat Client.
Provides core async authentication, session management, and utilities using httpx.
"""

import httpx
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AsyncBaseClient:
    """
    Asynchronous base client providing core functionality for OpenWebUI API communication.

    This class handles:
    - Asynchronous authentication and session management using httpx
    - Basic async HTTP requests with error handling and retries
    - Common utility methods
    """

    def __init__(self, base_url: str, token: str, default_model_id: str):
        """
        Initialize the async base client.

        Args:
            base_url: The base URL of the OpenWebUI instance
            token: Authentication token
            default_model_id: Default model identifier
        """
        self.base_url = base_url
        self.default_model_id = default_model_id
        self.model_id = default_model_id

        headers = {"Authorization": f"Bearer {token}"}

        # Configure retry transport
        retry_strategy = httpx.Limits(max_keepalives=5, max_connections=10)
        # httpx has built-in retry handling via transport for specific status codes
        # but for more complex logic like backoff, a custom transport or tenacity library is an option.
        # For now, we rely on simple retries via Timeout and Limits.

        self.session = httpx.AsyncClient(
            headers=headers,
            timeout=30.0,  # Default timeout
            limits=retry_strategy,
            http2=True # Enable HTTP/2 if server supports it
        )

        self.json_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # State tracking
        self.chat_id: Optional[str] = None
        self.chat_object_from_server: Optional[Dict[str, Any]] = None
        self.task_model: Optional[str] = None
        self._auto_cleanup_enabled: bool = True
        self._first_stream_request: bool = True

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Optional[httpx.Response]:
        """
        Make an async HTTP request with standardized error handling.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            request_headers = self.json_headers.copy()
            if headers:
                request_headers.update(headers)

            response = await self.session.request(
                method=method.upper(),
                url=url,
                json=json_data if not files else None,
                params=params,
                data=json_data if files else None, # httpx uses `data` for form-data with files
                files=files,
                headers=request_headers,
                timeout=timeout
            )

            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {e.request.method} {e.request.url}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {e.request.method} {e.request.url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {method} {endpoint}: {e}")
            return None

    async def _get_json_response(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make an async request and return JSON response.
        """
        response = await self._make_request(method, endpoint, json_data, params, files, headers)
        if response is None:
            return None

        try:
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None

    async def close(self):
        """Close the async client session."""
        await self.session.aclose()
