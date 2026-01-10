"""
Tests for AsyncBaseClient core functionality.
"""

import json
import unittest
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from openwebui_chat_client.core.async_base_client import AsyncBaseClient

# Configure pytest to recognize asyncio tests
pytestmark = pytest.mark.asyncio


class TestAsyncBaseClient:
    """Test cases for AsyncBaseClient class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.base_url = "http://test-server.com"
        self.token = "test_token"
        self.model = "test-model"

    def test_initialization(self):
        """Test AsyncBaseClient initialization"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)

        assert client.base_url == self.base_url
        assert client.default_model_id == self.model
        assert client.model_id == self.model
        assert client.token == self.token
        assert client.timeout == 60.0
        assert client.client is not None
        assert client.chat_id is None
        assert client.chat_object_from_server is None
        assert client._auto_cleanup_enabled is True
        assert client._first_stream_request is True

    def test_initialization_with_custom_timeout(self):
        """Test initialization with custom timeout"""
        client = AsyncBaseClient(self.base_url, self.token, self.model, timeout=120.0)

        assert client.timeout == 120.0

    def test_initialization_with_custom_headers(self):
        """Test initialization with custom headers"""
        custom_headers = {"X-Custom-Header": "custom-value"}
        client = AsyncBaseClient(
            self.base_url, self.token, self.model, headers=custom_headers
        )

        # Verify Authorization header is still present
        assert "Authorization" in client.client.headers
        assert client.client.headers["Authorization"] == f"Bearer {self.token}"

    def test_json_headers(self):
        """Test JSON headers are properly configured"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)

        assert "Authorization" in client.json_headers
        assert "Content-Type" in client.json_headers
        assert client.json_headers["Content-Type"] == "application/json"
        assert client.json_headers["Authorization"] == f"Bearer {self.token}"

    async def test_close(self):
        """Test client close method"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.aclose = AsyncMock()

        await client.close()

        client.client.aclose.assert_called_once()

    async def test_context_manager(self):
        """Test async context manager protocol"""
        async with AsyncBaseClient(self.base_url, self.token, self.model) as client:
            assert client is not None
            assert client.client is not None

    async def test_make_request_get_success(self):
        """Test successful GET request"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        client.client.get = AsyncMock(return_value=mock_response)

        response = await client._make_request("GET", "/api/test")

        assert response is not None
        assert response.status_code == 200
        client.client.get.assert_called_once()

    async def test_make_request_post_with_json(self):
        """Test POST request with JSON data"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        client.client.post = AsyncMock(return_value=mock_response)

        json_data = {"key": "value"}
        response = await client._make_request("POST", "/api/test", json_data=json_data)

        assert response is not None
        client.client.post.assert_called_once()

    async def test_make_request_put(self):
        """Test PUT request"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        client.client.put = AsyncMock(return_value=mock_response)

        json_data = {"update": "value"}
        response = await client._make_request("PUT", "/api/test", json_data=json_data)

        assert response is not None
        client.client.put.assert_called_once()

    async def test_make_request_delete(self):
        """Test DELETE request"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 204
        client.client.delete = AsyncMock(return_value=mock_response)

        response = await client._make_request("DELETE", "/api/test/123")

        assert response is not None
        client.client.delete.assert_called_once()

    async def test_make_request_unsupported_method(self):
        """Test unsupported HTTP method"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)

        response = await client._make_request("PATCH", "/api/test")

        assert response is None

    async def test_make_request_network_error(self):
        """Test network error handling"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.get = AsyncMock(side_effect=httpx.ConnectError("Network error"))

        response = await client._make_request("GET", "/api/test")

        assert response is None

    async def test_make_request_http_error(self):
        """Test HTTP error handling"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=Mock()
        )
        client.client.get = AsyncMock(return_value=mock_response)

        response = await client._make_request("GET", "/api/test")

        assert response is None

    async def test_make_request_unexpected_error(self):
        """Test unexpected error handling"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.get = AsyncMock(side_effect=Exception("Unexpected error"))

        response = await client._make_request("GET", "/api/test")

        assert response is None

    async def test_get_json_response_success(self):
        """Test successful JSON response parsing"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test", "status": "ok"}
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client._get_json_response("GET", "/api/test")

        assert result is not None
        assert result["data"] == "test"
        assert result["status"] == "ok"

    async def test_get_json_response_json_decode_error(self):
        """Test JSON decode error handling"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client._get_json_response("GET", "/api/test")

        assert result is None

    async def test_get_json_response_request_failed(self):
        """Test JSON response when request fails"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.get = AsyncMock(side_effect=httpx.ConnectError("Network error"))

        result = await client._get_json_response("GET", "/api/test")

        assert result is None

    async def test_upload_file_not_found(self):
        """Test file upload when file doesn't exist"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)

        with patch("os.path.exists", return_value=False):
            result = await client._upload_file("/nonexistent/file.txt")

        assert result is None

    async def test_upload_file_success(self):
        """Test successful file upload"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "file123",
            "filename": "test.txt",
            "size": 100,
        }
        client.client.post = AsyncMock(return_value=mock_response)

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", unittest.mock.mock_open(read_data=b"content")):
                result = await client._upload_file("/path/to/test.txt")

        assert result is not None
        assert result["id"] == "file123"

    async def test_upload_file_http_error(self):
        """Test file upload with HTTP error"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error", request=Mock(), response=Mock()
        )
        client.client.post = AsyncMock(return_value=mock_response)

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", unittest.mock.mock_open(read_data=b"content")):
                result = await client._upload_file("/path/to/test.txt")

        assert result is None

    async def test_get_task_model_from_config(self):
        """Test getting task model from server config"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"TASK_MODEL": "task-model-id"}
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client._get_task_model()

        assert result == "task-model-id"
        assert client.task_model == "task-model-id"

    async def test_get_task_model_cached(self):
        """Test task model is cached after first fetch"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.task_model = "cached-model"
        client.client.get = AsyncMock()

        result = await client._get_task_model()

        assert result == "cached-model"
        client.client.get.assert_not_called()

    async def test_get_task_model_missing_in_config(self):
        """Test task model when TASK_MODEL is missing from config"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # No TASK_MODEL in config
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client._get_task_model()

        assert result is None

    async def test_get_task_model_request_error(self):
        """Test task model fetch with request error"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.get = AsyncMock(side_effect=httpx.ConnectError("Network error"))

        result = await client._get_task_model()

        assert result is None

    def test_url_construction_with_trailing_slash(self):
        """Test URL construction handles trailing slashes correctly"""
        client = AsyncBaseClient("http://test.com/", self.token, self.model)

        # The base_url should be stripped of trailing slash during init
        assert client.client.base_url == httpx.URL("http://test.com")

    def test_initialization_with_custom_transport(self):
        """Test initialization with custom transport"""
        custom_transport = httpx.AsyncHTTPTransport(retries=5)
        client = AsyncBaseClient(
            self.base_url, self.token, self.model, transport=custom_transport
        )

        assert client.client is not None

    def test_initialization_ensures_authorization_header(self):
        """Test that Authorization header is always present"""
        # Even if user provides headers without Authorization
        custom_headers = {"X-Custom": "value"}
        client = AsyncBaseClient(
            self.base_url, self.token, self.model, headers=custom_headers
        )

        assert "Authorization" in client.client.headers
        assert client.client.headers["Authorization"] == f"Bearer {self.token}"
