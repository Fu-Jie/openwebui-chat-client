"""
Extended tests for BaseClient core functionality.
"""

import json
import unittest
from unittest.mock import Mock, patch, mock_open

import requests

from openwebui_chat_client.core.base_client import BaseClient


class TestBaseClientExtended(unittest.TestCase):
    """Extended test cases for BaseClient class"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://test-server.com"
        self.token = "test_token"
        self.model = "test-model"
        self.client = BaseClient(self.base_url, self.token, self.model)

    def test_initialization(self):
        """Test BaseClient initialization"""
        self.assertEqual(self.client.base_url, self.base_url)
        self.assertEqual(self.client.default_model_id, self.model)
        self.assertEqual(self.client.model_id, self.model)
        self.assertIsNotNone(self.client.session)
        self.assertEqual(
            self.client.session.headers["Authorization"], f"Bearer {self.token}"
        )
        self.assertIsNone(self.client.chat_id)
        self.assertIsNone(self.client.chat_object_from_server)
        self.assertTrue(self.client._auto_cleanup_enabled)
        self.assertTrue(self.client._first_stream_request)

    def test_session_headers(self):
        """Test session headers are properly set"""
        self.assertIn("Authorization", self.client.session.headers)
        self.assertEqual(
            self.client.session.headers["Authorization"], f"Bearer {self.token}"
        )

    def test_json_headers(self):
        """Test JSON headers are properly configured"""
        self.assertIn("Authorization", self.client.json_headers)
        self.assertIn("Content-Type", self.client.json_headers)
        self.assertEqual(self.client.json_headers["Content-Type"], "application/json")

    @patch("requests.Session.get")
    def test_make_request_get_success(self, mock_get):
        """Test successful GET request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        response = self.client._make_request("GET", "/api/test")

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

    @patch("requests.Session.post")
    def test_make_request_post_with_json(self, mock_post):
        """Test POST request with JSON data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        json_data = {"key": "value"}
        response = self.client._make_request("POST", "/api/test", json_data=json_data)

        self.assertIsNotNone(response)
        mock_post.assert_called_once()
        # Verify JSON data was passed
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs["json"], json_data)

    @patch("requests.Session.post")
    def test_make_request_post_with_files(self, mock_post):
        """Test POST request with file upload"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        files = {"file": ("test.txt", b"content")}
        response = self.client._make_request("POST", "/api/upload", files=files)

        self.assertIsNotNone(response)
        mock_post.assert_called_once()

    @patch("requests.Session.put")
    def test_make_request_put(self, mock_put):
        """Test PUT request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        json_data = {"update": "value"}
        response = self.client._make_request("PUT", "/api/test", json_data=json_data)

        self.assertIsNotNone(response)
        mock_put.assert_called_once()

    @patch("requests.Session.delete")
    def test_make_request_delete(self, mock_delete):
        """Test DELETE request"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        response = self.client._make_request("DELETE", "/api/test/123")

        self.assertIsNotNone(response)
        mock_delete.assert_called_once()

    def test_make_request_unsupported_method(self):
        """Test unsupported HTTP method"""
        response = self.client._make_request("PATCH", "/api/test")

        self.assertIsNone(response)

    @patch("requests.Session.get")
    def test_make_request_network_error(self, mock_get):
        """Test network error handling"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        response = self.client._make_request("GET", "/api/test")

        self.assertIsNone(response)

    @patch("requests.Session.get")
    def test_make_request_http_error(self, mock_get):
        """Test HTTP error handling"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        response = self.client._make_request("GET", "/api/test")

        self.assertIsNone(response)

    @patch("requests.Session.get")
    def test_make_request_unexpected_error(self, mock_get):
        """Test unexpected error handling"""
        mock_get.side_effect = Exception("Unexpected error")

        response = self.client._make_request("GET", "/api/test")

        self.assertIsNone(response)

    @patch("requests.Session.get")
    def test_get_json_response_success(self, mock_get):
        """Test successful JSON response parsing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test", "status": "ok"}
        mock_get.return_value = mock_response

        result = self.client._get_json_response("GET", "/api/test")

        self.assertIsNotNone(result)
        self.assertEqual(result["data"], "test")
        self.assertEqual(result["status"], "ok")

    @patch("requests.Session.get")
    def test_get_json_response_json_decode_error(self, mock_get):
        """Test JSON decode error handling"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        result = self.client._get_json_response("GET", "/api/test")

        self.assertIsNone(result)

    @patch("requests.Session.get")
    def test_get_json_response_request_failed(self, mock_get):
        """Test JSON response when request fails"""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = self.client._get_json_response("GET", "/api/test")

        self.assertIsNone(result)

    def test_validate_required_params_all_present(self):
        """Test validation with all required params present"""
        params = {"name": "test", "value": "123", "type": "string"}
        required = ["name", "value"]

        result = self.client._validate_required_params(params, required)

        self.assertTrue(result)

    def test_validate_required_params_missing_param(self):
        """Test validation with missing required param"""
        params = {"name": "test"}
        required = ["name", "value"]

        result = self.client._validate_required_params(params, required)

        self.assertFalse(result)

    def test_validate_required_params_empty_value(self):
        """Test validation with empty param value"""
        params = {"name": "test", "value": ""}
        required = ["name", "value"]

        result = self.client._validate_required_params(params, required)

        self.assertFalse(result)

    def test_validate_required_params_none_value(self):
        """Test validation with None param value"""
        params = {"name": "test", "value": None}
        required = ["name", "value"]

        result = self.client._validate_required_params(params, required)

        self.assertFalse(result)

    def test_validate_required_params_empty_list(self):
        """Test validation with no required params"""
        params = {"name": "test", "value": "123"}
        required = []

        result = self.client._validate_required_params(params, required)

        self.assertTrue(result)

    @patch("os.path.exists")
    def test_upload_file_not_found(self, mock_exists):
        """Test file upload when file doesn't exist"""
        mock_exists.return_value = False

        result = self.client._upload_file("/nonexistent/file.txt")

        self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    @patch("requests.Session.post")
    def test_upload_file_success(self, mock_post, mock_file, mock_exists):
        """Test successful file upload"""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "file123",
            "filename": "test.txt",
            "size": 100,
        }
        mock_post.return_value = mock_response

        result = self.client._upload_file("/path/to/test.txt")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "file123")
        mock_post.assert_called_once()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    @patch("requests.Session.post")
    def test_upload_file_http_error(self, mock_post, mock_file, mock_exists):
        """Test file upload with HTTP error"""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error"
        )
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = self.client._upload_file("/path/to/test.txt")

        self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", side_effect=IOError("Cannot read file"))
    def test_upload_file_read_error(self, mock_file, mock_exists):
        """Test file upload when file cannot be read"""
        mock_exists.return_value = True

        result = self.client._upload_file("/path/to/test.txt")

        self.assertIsNone(result)

    @patch("requests.Session.get")
    def test_get_task_model_from_config(self, mock_get):
        """Test getting task model from server config"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"TASK_MODEL": "task-model-id"}
        mock_get.return_value = mock_response

        result = self.client._get_task_model()

        self.assertEqual(result, "task-model-id")
        self.assertEqual(self.client.task_model, "task-model-id")

    @patch("requests.Session.get")
    def test_get_task_model_cached(self, mock_get):
        """Test task model is cached after first fetch"""
        self.client.task_model = "cached-model"

        result = self.client._get_task_model()

        self.assertEqual(result, "cached-model")
        mock_get.assert_not_called()

    @patch("requests.Session.get")
    def test_get_task_model_missing_in_config(self, mock_get):
        """Test task model when TASK_MODEL is missing from config"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # No TASK_MODEL in config
        mock_get.return_value = mock_response

        result = self.client._get_task_model()

        self.assertIsNone(result)

    @patch("requests.Session.get")
    def test_get_task_model_request_error(self, mock_get):
        """Test task model fetch with request error"""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = self.client._get_task_model()

        self.assertIsNone(result)

    def test_url_construction_with_trailing_slash(self):
        """Test URL construction handles trailing slashes correctly"""
        client = BaseClient("http://test.com/", self.token, self.model)

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            client._make_request("GET", "/api/test")

            # Verify URL doesn't have double slashes
            call_args = mock_get.call_args[0]
            self.assertEqual(call_args[0], "http://test.com/api/test")

    def test_url_construction_without_leading_slash(self):
        """Test URL construction handles missing leading slash"""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            self.client._make_request("GET", "api/test")

            call_args = mock_get.call_args[0]
            self.assertEqual(call_args[0], "http://test-server.com/api/test")

    def test_custom_headers_merge(self):
        """Test custom headers are merged with default headers"""
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            custom_headers = {"X-Custom-Header": "custom-value"}
            self.client._make_request(
                "POST", "/api/test", json_data={"data": "test"}, headers=custom_headers
            )

            call_kwargs = mock_post.call_args[1]
            headers = call_kwargs["headers"]
            self.assertIn("X-Custom-Header", headers)
            self.assertIn("Authorization", headers)
            self.assertIn("Content-Type", headers)


if __name__ == "__main__":
    unittest.main()
