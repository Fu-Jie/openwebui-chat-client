"""
Base client functionality for OpenWebUI Chat Client.
Provides core authentication, session management, and common utilities.
"""

import requests
import json
import logging
from typing import Optional, Dict, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseClient:
    """
    Base client class providing core functionality for OpenWebUI API communication.
    
    This class handles:
    - Authentication and session management
    - Basic HTTP requests with error handling
    - Common utility methods
    """
    
    def __init__(self, base_url: str, token: str, default_model_id: str):
        """
        Initialize the base client.
        
        Args:
            base_url: The base URL of the OpenWebUI instance
            token: Authentication token
            default_model_id: Default model identifier
        """
        self.base_url = base_url
        self.default_model_id = default_model_id
        self.model_id = default_model_id
        
        # Session setup with retry logic
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[500, 502, 503, 504],  # Retry on these server error codes
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
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
        
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[requests.Response]:
        """
        Make an HTTP request with standardized error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            json_data: JSON payload for request body
            params: URL parameters
            files: Files for multipart upload
            headers: Additional headers
            
        Returns:
            Response object or None if request failed
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                if files:
                    # For file uploads, don't use json_headers (multipart/form-data)
                    response = self.session.post(url, data=json_data, files=files, headers=headers)
                else:
                    # For JSON data
                    request_headers = self.json_headers.copy()
                    if headers:
                        request_headers.update(headers)
                    response = self.session.post(url, json=json_data, headers=request_headers)
            elif method.upper() == "PUT":
                request_headers = self.json_headers.copy()
                if headers:
                    request_headers.update(headers)
                response = self.session.put(url, json=json_data, headers=request_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers or self.json_headers)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
                
            # The retry adapter will handle raising an exception for status codes
            # in the status_forcelist after all retries are exhausted.
            # We still call it here to handle non-retryable error codes immediately.
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {method} {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {method} {endpoint}: {e}")
            return None
    
    def _get_json_response(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request and return JSON response.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            json_data: JSON payload
            params: URL parameters
            files: Files for upload
            headers: Additional headers
            
        Returns:
            Parsed JSON response or None if failed
        """
        response = self._make_request(method, endpoint, json_data, params, files, headers)
        if response is None:
            return None
            
        try:
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
    
    def _validate_required_params(self, params: Dict[str, Any], required: List[str]) -> bool:
        """
        Validate that required parameters are present and not empty.
        
        Args:
            params: Parameter dictionary to validate
            required: List of required parameter names
            
        Returns:
            True if all required parameters are present and valid
        """
        for param in required:
            if param not in params or not params[param]:
                logger.error(f"Required parameter '{param}' is missing or empty")
                return False
    
    def _upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Upload a file to the OpenWebUI server.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            File metadata dictionary or None if upload failed
        """
        import os
        
        if not os.path.exists(file_path):
            logger.error(f"File not found at path: {file_path}")
            return None
            
        file_name = os.path.basename(file_path)
        url = f"{self.base_url}/api/v1/files/"
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f, "application/octet-stream")}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                file_metadata = response.json()
                logger.info(f"Successfully uploaded file: {file_name}")
                return file_metadata
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload file '{file_name}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file '{file_name}': {e}")
            return None

    def _get_task_model(self) -> Optional[str]:
        """Get the task model for AI tasks (tags, titles, follow-ups)."""
        # Use parent client's method if available (for test mocking)
        parent_client = getattr(self, '_parent_client', None)
        if parent_client and hasattr(parent_client, '_get_task_model'):
            return parent_client._get_task_model()
        
        if hasattr(self, "task_model") and self.task_model:
            return self.task_model

        logger.info("Fetching task model configuration...")
        url = f"{self.base_url}/api/v1/tasks/config"
        try:
            response = self.session.get(url, headers=self.json_headers)
            response.raise_for_status()
            config = response.json()
            task_model = config.get("TASK_MODEL")
            if task_model:
                logger.info(f"   ✅ Found task model: {task_model}")
                self.task_model = task_model
                return task_model
            else:
                logger.error("   ❌ 'TASK_MODEL' not found in config response.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch task config: {e}")
            return None
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from task config response.")
            return None