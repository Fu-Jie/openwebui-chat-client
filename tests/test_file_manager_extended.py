"""
Extended tests for FileManager to improve coverage.

This test file focuses on testing FileManager methods including
file upload operations and error handling.
"""

import base64
import os
import unittest
from unittest.mock import MagicMock, Mock, patch, mock_open
from typing import Dict, Any
import requests

from openwebui_chat_client.modules.file_manager import FileManager
from openwebui_chat_client.core.base_client import BaseClient


class TestFileManagerExtended(unittest.TestCase):
    """Extended tests for FileManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = Mock(spec=BaseClient)
        self.base_client.base_url = "http://localhost:3000"
        self.base_client.session = Mock()
        self.base_client.json_headers = {"Authorization": "Bearer test_token"}
        self.manager = FileManager(self.base_client)

    def test_initialization(self):
        """Test FileManager initialization."""
        self.assertEqual(self.manager.base_client, self.base_client)

    @patch("os.path.exists")
    def test_upload_file_not_exists(self, mock_exists):
        """Test upload_file when file doesn't exist."""
        mock_exists.return_value = False

        result = self.manager.upload_file("nonexistent.txt")

        self.assertIsNone(result)

    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    @patch("os.path.exists")
    def test_upload_file_request_exception(self, mock_exists, mock_file):
        """Test upload_file handles request exception."""
        mock_exists.return_value = True
        self.base_client.session.post.side_effect = (
            requests.exceptions.RequestException("Error")
        )

        result = self.manager.upload_file("test.txt")

        self.assertIsNone(result)

    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    @patch("os.path.exists")
    def test_upload_file_http_error(self, mock_exists, mock_file):
        """Test upload_file handles HTTP error."""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.text = "Error message"
        error = requests.exceptions.HTTPError("API Error")
        error.response = mock_response
        self.base_client.session.post.side_effect = error

        result = self.manager.upload_file("test.txt")

        self.assertIsNone(result)

    @patch("builtins.open", side_effect=IOError("Cannot read file"))
    @patch("os.path.exists")
    def test_upload_file_io_error(self, mock_exists, mock_file):
        """Test upload_file handles IO error."""
        mock_exists.return_value = True

        result = self.manager.upload_file("test.txt")

        self.assertIsNone(result)

    @patch("os.path.exists")
    def test_encode_image_to_base64_not_exists(self, mock_exists):
        """Test encode_image_to_base64 when file doesn't exist."""
        mock_exists.return_value = False

        result = self.manager.encode_image_to_base64("nonexistent.png")

        self.assertIsNone(result)

    @patch("builtins.open", new_callable=mock_open, read_data=b"\x89PNG\r\n\x1a\n")
    @patch("os.path.exists")
    def test_encode_image_to_base64_png(self, mock_exists, mock_file):
        """Test encode_image_to_base64 with PNG file."""
        mock_exists.return_value = True

        result = self.manager.encode_image_to_base64("test.png")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/png;base64,"))

    @patch("builtins.open", new_callable=mock_open, read_data=b"\xff\xd8\xff")
    @patch("os.path.exists")
    def test_encode_image_to_base64_jpg(self, mock_exists, mock_file):
        """Test encode_image_to_base64 with JPG file."""
        mock_exists.return_value = True

        result = self.manager.encode_image_to_base64("test.jpg")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/jpeg;base64,"))

    @patch("builtins.open", new_callable=mock_open, read_data=b"GIF89a")
    @patch("os.path.exists")
    def test_encode_image_to_base64_gif(self, mock_exists, mock_file):
        """Test encode_image_to_base64 with GIF file."""
        mock_exists.return_value = True

        result = self.manager.encode_image_to_base64("test.gif")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/gif;base64,"))

    @patch("builtins.open", new_callable=mock_open, read_data=b"WEBP")
    @patch("os.path.exists")
    def test_encode_image_to_base64_webp(self, mock_exists, mock_file):
        """Test encode_image_to_base64 with WEBP file."""
        mock_exists.return_value = True

        result = self.manager.encode_image_to_base64("test.webp")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/webp;base64,"))

    @patch("builtins.open", side_effect=IOError("Cannot read file"))
    @patch("os.path.exists")
    def test_encode_image_to_base64_io_error(self, mock_exists, mock_file):
        """Test encode_image_to_base64 handles IO error."""
        mock_exists.return_value = True

        result = self.manager.encode_image_to_base64("test.png")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
