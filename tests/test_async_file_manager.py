"""
Tests for AsyncFileManager module.
"""

import base64
import unittest
from unittest.mock import AsyncMock, Mock, mock_open, patch

import pytest

from openwebui_chat_client.modules.async_file_manager import AsyncFileManager


class TestAsyncFileManager(unittest.TestCase):
    """Test cases for AsyncFileManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client.base_url = "http://localhost:3000"
        self.base_client._upload_file = AsyncMock()
        self.file_manager = AsyncFileManager(self.base_client)

    def test_initialization(self):
        """Test AsyncFileManager initialization"""
        self.assertIsNotNone(self.file_manager)
        self.assertEqual(self.file_manager.base_client, self.base_client)

    @pytest.mark.asyncio
    async def test_upload_file_success(self):
        """Test successful async file upload"""
        self.base_client._upload_file.return_value = {
            "id": "file123",
            "filename": "test.txt",
            "size": 100,
        }

        result = await self.file_manager.upload_file("/path/to/test.txt")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "file123")
        self.base_client._upload_file.assert_called_once_with("/path/to/test.txt")

    @pytest.mark.asyncio
    async def test_upload_file_failure(self):
        """Test async file upload failure"""
        self.base_client._upload_file.return_value = None

        result = await self.file_manager.upload_file("/path/to/test.txt")

        self.assertIsNone(result)
        self.base_client._upload_file.assert_called_once()

    @patch("os.path.exists")
    def test_encode_image_to_base64_file_not_found(self, mock_exists):
        """Test encode_image_to_base64 when image doesn't exist"""
        mock_exists.return_value = False

        result = self.file_manager.encode_image_to_base64("/nonexistent/image.png")

        self.assertIsNone(result)
        mock_exists.assert_called_once_with("/nonexistent/image.png")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
    def test_encode_image_to_base64_png_success(self, mock_file, mock_exists):
        """Test successful PNG image encoding"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/image.png")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/png;base64,"))
        base64_part = result.split(",")[1]
        decoded = base64.b64decode(base64_part)
        self.assertEqual(decoded, b"fake_image_data")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
    def test_encode_image_to_base64_jpeg_success(self, mock_file, mock_exists):
        """Test successful JPEG image encoding (default)"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/image.jpg")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/jpeg;base64,"))

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
    def test_encode_image_to_base64_gif_success(self, mock_file, mock_exists):
        """Test successful GIF image encoding"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/image.gif")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/gif;base64,"))

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
    def test_encode_image_to_base64_webp_success(self, mock_file, mock_exists):
        """Test successful WebP image encoding"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/image.webp")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/webp;base64,"))

    @patch("os.path.exists")
    @patch("builtins.open", side_effect=OSError("Cannot read file"))
    def test_encode_image_to_base64_read_error(self, mock_file, mock_exists):
        """Test encode_image_to_base64 when file cannot be read"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/image.png")

        self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"")
    def test_encode_image_to_base64_empty_file(self, mock_file, mock_exists):
        """Test encoding an empty image file"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/empty.png")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/png;base64,"))

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"large" * 1000)
    def test_encode_image_to_base64_large_file(self, mock_file, mock_exists):
        """Test encoding a large image file"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/large.png")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/png;base64,"))
        base64_part = result.split(",")[1]
        decoded = base64.b64decode(base64_part)
        self.assertEqual(decoded, b"large" * 1000)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test")
    def test_encode_image_to_base64_case_insensitive_extension(
        self, mock_file, mock_exists
    ):
        """Test that file extension matching is case-insensitive"""
        mock_exists.return_value = True

        # Test uppercase extensions
        result_png = self.file_manager.encode_image_to_base64("/path/to/image.PNG")
        self.assertTrue(result_png.startswith("data:image/png;base64,"))

        result_gif = self.file_manager.encode_image_to_base64("/path/to/image.GIF")
        self.assertTrue(result_gif.startswith("data:image/gif;base64,"))

        result_webp = self.file_manager.encode_image_to_base64("/path/to/image.WEBP")
        self.assertTrue(result_webp.startswith("data:image/webp;base64,"))


if __name__ == "__main__":
    unittest.main()
