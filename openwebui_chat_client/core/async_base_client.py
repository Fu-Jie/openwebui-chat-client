"""
Async Base client functionality for OpenWebUI Chat Client.
Provides core authentication, session management, and common utilities for asynchronous operations.
"""

import httpx
import json
import logging
import os
from typing import Optional, Dict, Any, TYPE_CHECKING


logger = logging.getLogger(__name__)


class AsyncBaseClient:
    """
    Async Base client class providing core functionality for OpenWebUI API communication.

    This class handles:
    - Authentication and session management (using httpx.AsyncClient)
    - Basic HTTP requests with error handling
    - Common utility methods
    """

    def __init__(self, base_url: str, token: str, default_model_id: str, timeout: float = 60.0, **kwargs):
        """
        Initialize the async base client.

        Args:
            base_url: The base URL of the OpenWebUI instance
            token: Authentication token
            default_model_id: Default model identifier
            timeout: Request timeout in seconds
            **kwargs: Additional arguments to pass to httpx.AsyncClient (e.g., verify, proxies, limits)
        """
        self.base_url = base_url
        self.default_model_id = default_model_id
        self.model_id = default_model_id
        self.token = token
        self.timeout = timeout

        # Prepare client kwargs
        client_kwargs = {
            "base_url": base_url.rstrip('/'),
            "headers": {"Authorization": f"Bearer {token}"},
            "timeout": timeout,
            "follow_redirects": True,
        }

        # Set default transport if not provided in kwargs
        if "transport" not in kwargs:
            client_kwargs["transport"] = httpx.AsyncHTTPTransport(retries=3)

        # Handle headers merging
        if "headers" in kwargs:
            user_headers = kwargs.pop("headers")
            if user_headers:
                client_kwargs["headers"].update(user_headers)

        # Ensure Authorization header is present
        if "Authorization" not in client_kwargs["headers"]:
             client_kwargs["headers"]["Authorization"] = f"Bearer {token}"

        # Update with any remaining kwargs (overriding defaults if provided)
        client_kwargs.update(kwargs)

        self.client = httpx.AsyncClient(**client_kwargs)

        # JSON headers for POST requests
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

        # Parent reference
        self._parent_client = None

    async def close(self):
        """Close the async client session."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

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
        Make an asynchronous HTTP request with standardized error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            json_data: JSON payload for request body
            params: URL parameters
            files: Files for multipart upload
            headers: Additional headers
            timeout: Request timeout

        Returns:
            Response object or None if request failed
        """
        url = endpoint.lstrip('/')
        request_headers = self.json_headers.copy() if not files else {"Authorization": f"Bearer {self.token}"}
        if headers:
            request_headers.update(headers)

        try:
            if method.upper() == "GET":
                response = await self.client.get(url, params=params, headers=request_headers, timeout=timeout)
            elif method.upper() == "POST":
                if files:
                    response = await self.client.post(url, data=json_data, files=files, headers=request_headers, timeout=timeout)
                else:
                    response = await self.client.post(url, json=json_data, headers=request_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=json_data, headers=request_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=request_headers, timeout=timeout)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {method} {endpoint}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {endpoint}: {e}")
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

    async def _upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Upload a file to the OpenWebUI server asynchronously.

        Args:
            file_path: Path to the file to upload

        Returns:
            File metadata dictionary or None if upload failed
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found at path: {file_path}")
            return None

        file_name = os.path.basename(file_path)
        endpoint = "/api/v1/files/"

        try:
            # Note: Using synchronous file I/O in async context. This is acceptable for small files
            # as httpx internally handles the file reading efficiently. For large files, consider
            # using asyncio.to_thread() or the aiofiles library to avoid blocking the event loop.
            # httpx files parameter expects opened file objects.

            with open(file_path, "rb") as f:
                files = {"file": (file_name, f, "application/octet-stream")}
                response = await self._make_request("POST", endpoint, files=files)

                if response:
                    file_metadata = response.json()
                    logger.info(f"Successfully uploaded file: {file_name}")
                    return file_metadata
                return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file '{file_name}': {e}")
            return None

    async def _get_task_model(self) -> Optional[str]:
        """Get the task model for AI tasks (tags, titles, follow-ups)."""
        if self.task_model:
            return self.task_model

        logger.info("Fetching task model configuration...")
        config = await self._get_json_response("GET", "/api/v1/tasks/config")

        if config:
            task_model = config.get("TASK_MODEL")
            if task_model:
                logger.info(f"   ✅ Found task model: {task_model}")
                self.task_model = task_model
                return task_model
            else:
                logger.error("   ❌ 'TASK_MODEL' not found in config response.")
                return None

        return None
