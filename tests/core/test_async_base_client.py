"""
Tests for AsyncBaseClient core functionality.
"""

import json
import unittest
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from openwebui_chat_client.core.async_base_client import AsyncBaseClient


class TestAsyncBaseClient(unittest.TestCase):
    """Test cases for AsyncBaseClient class"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://test-server.com"
        self.token = "test_token"
        self.model = "test-model"

    def test_initialization(self):
        """Test AsyncBaseClient initialization"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)

        self.assertEqual(client.base_url, self.base_url)
        self.assertEqual(client.default_model_id, self.model)
        self.assertEqual(client.model_id, self.model)
        self.assertEqual(client.token, self.token)
        self.assertEqual(client.timeout, 60.0)
        self.assertIsNotNone(client.client)
        self.assertIsNone(client.chat_id)
        self.assertIsNone(client.chat_object_from_server)
        self.assertTrue(client._auto_cleanup_enabled)
        self.assertTrue(client._first_stream_request)

    def test_initialization_with_custom_timeout(self):
        """Test initialization with custom timeout"""
        client = AsyncBaseClient(self.base_url, self.token, self.model, timeout=120.0)

        self.assertEqual(client.timeout, 120.0)

    def test_initialization_with_custom_headers(self):
        """Test initialization with custom headers"""
        custom_headers = {"X-Custom-Header": "custom-value"}
        client = AsyncBaseClient(
            self.base_url, self.token, self.model, headers=custom_headers
        )

        # Verify Authorization header is still present
        self.assertIn("Authorization", client.client.headers)
        self.assertEqual(
            client.client.headers["Authorization"], f"Bearer {self.token}"
        )

    def test_json_headers(self):
        """Test JSON headers are properly configured"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)

        self.assertIn("Authorization", client.json_headers)
        self.assertIn("Content-Type", client.json_headers)
        self.assertEqual(client.json_headers["Content-Type"], "application/json")
        self.assertEqual(client.json_headers["Authorization"], f"Bearer {self.token}")

    @pytest.mark.asyncio
    async def test_close(self):
        """Test client close method"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.aclose = AsyncMock()

        await client.close()

        client.client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager protocol"""
        async with AsyncBaseClient(self.base_url, self.token, self.model) as client:
            self.assertIsNotNone(client)
            self.assertIsNotNone(client.client)

    @pytest.mark.asyncio
    async def test_make_request_get_success(self):
        """Test successful GET request"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        client.client.get = AsyncMock(return_value=mock_response)

        response = await client._make_request("GET", "/api/test")

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        client.client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_post_with_json(self):
        """Test POST request with JSON data"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        client.client.post = AsyncMock(return_value=mock_response)

        json_data = {"key": "value"}
        response = await client._make_request("POST", "/api/test", json_data=json_data)

        self.assertIsNotNone(response)
        client.client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_put(self):
        """Test PUT request"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        client.client.put = AsyncMock(return_value=mock_response)

        json_data = {"update": "value"}
        response = await client._make_request("PUT", "/api/test", json_data=json_data)

        self.assertIsNotNone(response)
        client.client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_delete(self):
        """Test DELETE request"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 204
        client.client.delete = AsyncMock(return_value=mock_response)

        response = await client._make_request("DELETE", "/api/test/123")

        self.assertIsNotNone(response)
        client.client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_unsupported_method(self):
        """Test unsupported HTTP method"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)

        response = await client._make_request("PATCH", "/api/test")

        self.assertIsNone(response)

    @pytest.mark.asyncio
    async def test_make_request_network_error(self):
        """Test network error handling"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.get = AsyncMock(
            side_effect=httpx.ConnectError("Network error")
        )

        response = await client._make_request("GET", "/api/test")

        self.assertIsNone(response)

    @pytest.mark.asyncio
    async def test_make_request_http_error(self):
        """Test HTTP error handling"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=Mock()
        )
        client.client.get = AsyncMock(return_value=mock_response)

        response = await client._make_request("GET", "/api/test")

        self.assertIsNone(response)

    @pytest.mark.asyncio
    async def test_make_request_unexpected_error(self):
        """Test unexpected error handling"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.get = AsyncMock(side_effect=Exception("Unexpected error"))

        response = await client._make_request("GET", "/api/test")

        self.assertIsNone(response)

    @pytest.mark.asyncio
    async def test_get_json_response_success(self):
        """Test successful JSON response parsing"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test", "status": "ok"}
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client._get_json_response("GET", "/api/test")

        self.assertIsNotNone(result)
        self.assertEqual(result["data"], "test")
        self.assertEqual(result["status"], "ok")

    @pytest.mark.asyncio
    async def test_get_json_response_json_decode_error(self):
        """Test JSON decode error handling"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client._get_json_response("GET", "/api/test")

        self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_get_json_response_request_failed(self):
        """Test JSON response when request fails"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.get = AsyncMock(side_effect=httpx.ConnectError("Network error"))

        result = await client._get_json_response("GET", "/api/test")

        self.assertIsNone(result)

    def test_validate_required_params_all_present(self):
        """Test validation with all required params present"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        params = {"name": "test", "value": "123", "type": "string"}
        required = ["name", "value"]

        result = client._validate_required_params(params, required)

        self.assertTrue(result)

    def test_validate_required_params_missing_param(self):
        """Test validation with missing required param"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        params = {"name": "test"}
        required = ["name", "value"]

        result = client._validate_required_params(params, required)

        self.assertFalse(result)

    def test_validate_required_params_empty_value(self):
        """Test validation with empty param value"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        params = {"name": "test", "value": ""}
        required = ["name", "value"]

        result = client._validate_required_params(params, required)

        self.assertFalse(result)

    @pytest.mark.asyncio
    async def test_upload_file_not_found(self):
        """Test file upload when file doesn't exist"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)

        with patch("os.path.exists", return_value=False):
            result = await client._upload_file("/nonexistent/file.txt")

        self.assertIsNone(result)

    @pytest.mark.asyncio
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

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "file123")

    @pytest.mark.asyncio
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

        self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_get_task_model_from_config(self):
        """Test getting task model from server config"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"TASK_MODEL": "task-model-id"}
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client._get_task_model()

        self.assertEqual(result, "task-model-id")
        self.assertEqual(client.task_model, "task-model-id")

    @pytest.mark.asyncio
    async def test_get_task_model_cached(self):
        """Test task model is cached after first fetch"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.task_model = "cached-model"
        client.client.get = AsyncMock()

        result = await client._get_task_model()

        self.assertEqual(result, "cached-model")
        client.client.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_task_model_fallback_to_default(self):
        """Test task model falls back to default model"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # No TASK_MODEL in config
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client._get_task_model()

        self.assertEqual(result, self.model)

    @pytest.mark.asyncio
    async def test_get_task_model_request_error(self):
        """Test task model fetch with request error"""
        client = AsyncBaseClient(self.base_url, self.token, self.model)
        client.client.get = AsyncMock(side_effect=httpx.ConnectError("Network error"))

        result = await client._get_task_model()

        self.assertEqual(result, self.model)

    def test_url_construction_with_trailing_slash(self):
        """Test URL construction handles trailing slashes correctly"""
        client = AsyncBaseClient("http://test.com/", self.token, self.model)

        # The base_url should be stripped of trailing slash during init
        self.assertEqual(client.client.base_url, httpx.URL("http://test.com"))

    def test_initialization_with_custom_transport(self):
        """Test initialization with custom transport"""
        custom_transport = httpx.AsyncHTTPTransport(retries=5)
        client = AsyncBaseClient(
            self.base_url, self.token, self.model, transport=custom_transport
        )

        self.assertIsNotNone(client.client)

    def test_initialization_ensures_authorization_header(self):
        """Test that Authorization header is always present"""
        # Even if user provides headers without Authorization
        custom_headers = {"X-Custom": "value"}
        client = AsyncBaseClient(
            self.base_url, self.token, self.model, headers=custom_headers
        )

        self.assertIn("Authorization", client.client.headers)
        self.assertEqual(
            client.client.headers["Authorization"], f"Bearer {self.token}"
        )


if __name__ == "__main__":
    unittest.main()
