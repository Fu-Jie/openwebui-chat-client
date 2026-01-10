"""
Tests for FileManager module.
"""

import base64
import unittest
from unittest.mock import Mock, mock_open, patch

from openwebui_chat_client.modules.file_manager import FileManager


class TestFileManager(unittest.TestCase):
    """Test cases for FileManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client.base_url = "http://localhost:3000"
        self.base_client.session = Mock()
        self.base_client.session.headers = {"Authorization": "Bearer test-token"}
        self.file_manager = FileManager(self.base_client)

    def test_initialization(self):
        """Test FileManager initialization"""
        self.assertIsNotNone(self.file_manager)
        self.assertEqual(self.file_manager.base_client, self.base_client)

    @patch("os.path.exists")
    def test_upload_file_not_found(self, mock_exists):
        """Test upload_file when file doesn't exist"""
        mock_exists.return_value = False

        result = self.file_manager.upload_file("/nonexistent/file.txt")

        self.assertIsNone(result)
        mock_exists.assert_called_once_with("/nonexistent/file.txt")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    def test_upload_file_success(self, mock_file, mock_exists):
        """Test successful file upload"""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "file123",
            "filename": "test.txt",
            "size": 100,
        }
        self.base_client.session.post.return_value = mock_response

        result = self.file_manager.upload_file("/path/to/test.txt")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "file123")
        self.assertEqual(result["filename"], "test.txt")
        mock_exists.assert_called_once()
        self.base_client.session.post.assert_called_once()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    def test_upload_file_no_id_in_response(self, mock_file, mock_exists):
        """Test upload_file when response doesn't contain ID"""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"filename": "test.txt"}  # No 'id' field
        self.base_client.session.post.return_value = mock_response

        result = self.file_manager.upload_file("/path/to/test.txt")

        self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    def test_upload_file_http_error(self, mock_file, mock_exists):
        """Test upload_file with HTTP error"""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        self.base_client.session.post.return_value = mock_response

        result = self.file_manager.upload_file("/path/to/test.txt")

        self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", side_effect=OSError("Cannot read file"))
    def test_upload_file_read_error(self, mock_file, mock_exists):
        """Test upload_file when file cannot be read"""
        mock_exists.return_value = True

        result = self.file_manager.upload_file("/path/to/test.txt")

        self.assertIsNone(result)

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
        # Verify base64 encoding
        base64_part = result.split(",")[1]
        decoded = base64.b64decode(base64_part)
        self.assertEqual(decoded, b"fake_image_data")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
    def test_encode_image_to_base64_jpg_success(self, mock_file, mock_exists):
        """Test successful JPG image encoding"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/image.jpg")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/jpeg;base64,"))

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
    def test_encode_image_to_base64_jpeg_success(self, mock_file, mock_exists):
        """Test successful JPEG image encoding"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/image.jpeg")

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
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_file_data")
    def test_encode_image_to_base64_unknown_extension(self, mock_file, mock_exists):
        """Test image encoding with unknown file extension"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/file.xyz")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:application/octet-stream;base64,"))

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
        # Empty file should encode to empty base64
        base64_part = result.split(",")[1]
        self.assertEqual(base64_part, "")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"large" * 1000)
    def test_encode_image_to_base64_large_file(self, mock_file, mock_exists):
        """Test encoding a large image file"""
        mock_exists.return_value = True

        result = self.file_manager.encode_image_to_base64("/path/to/large.png")

        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("data:image/png;base64,"))
        # Verify the large content is properly encoded
        base64_part = result.split(",")[1]
        decoded = base64.b64decode(base64_part)
        self.assertEqual(decoded, b"large" * 1000)


if __name__ == "__main__":
    unittest.main()
