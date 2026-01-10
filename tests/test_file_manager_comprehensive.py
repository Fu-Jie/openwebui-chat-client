"""
Comprehensive tests for FileManager - covering remaining untested methods.
"""

import unittest
from unittest.mock import Mock, mock_open, patch

from openwebui_chat_client.modules.file_manager import FileManager


class TestFileManagerComprehensive(unittest.TestCase):
    """Comprehensive test cases for FileManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client.base_url = "http://test-server.com"
        self.base_client.session = Mock()
        self.base_client.session.headers = {"Authorization": "Bearer test_token"}
        self.file_manager = FileManager(self.base_client)

    # ========== validate_file_exists tests ==========

    @patch("os.path.exists")
    def test_validate_file_exists_true(self, mock_exists):
        """Test validate_file_exists returns True when file exists."""
        mock_exists.return_value = True

        result = self.file_manager.validate_file_exists("/path/to/file.txt")

        self.assertTrue(result)
        mock_exists.assert_called_once_with("/path/to/file.txt")

    @patch("os.path.exists")
    def test_validate_file_exists_false(self, mock_exists):
        """Test validate_file_exists returns False when file doesn't exist."""
        mock_exists.return_value = False

        result = self.file_manager.validate_file_exists("/path/to/nonexistent.txt")

        self.assertFalse(result)
        mock_exists.assert_called_once_with("/path/to/nonexistent.txt")

    # ========== get_file_info tests ==========

    @patch("os.path.exists")
    def test_get_file_info_file_not_exists(self, mock_exists):
        """Test get_file_info returns None when file doesn't exist."""
        mock_exists.return_value = False

        result = self.file_manager.get_file_info("/path/to/nonexistent.txt")

        self.assertIsNone(result)

    @patch("os.stat")
    @patch("os.path.exists")
    def test_get_file_info_success(self, mock_exists, mock_stat):
        """Test get_file_info returns file information successfully."""
        mock_exists.return_value = True
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024
        mock_stat.return_value = mock_stat_result

        result = self.file_manager.get_file_info("/path/to/test.txt")

        self.assertIsNotNone(result)
        self.assertEqual(result["path"], "/path/to/test.txt")
        self.assertEqual(result["name"], "test.txt")
        self.assertEqual(result["size"], 1024)
        self.assertEqual(result["extension"], ".txt")
        self.assertTrue(result["exists"])

    @patch("os.stat")
    @patch("os.path.exists")
    def test_get_file_info_with_different_extensions(self, mock_exists, mock_stat):
        """Test get_file_info with various file extensions."""
        mock_exists.return_value = True
        mock_stat_result = Mock()
        mock_stat_result.st_size = 2048
        mock_stat.return_value = mock_stat_result

        # Test .pdf extension
        result = self.file_manager.get_file_info("/docs/document.pdf")
        self.assertEqual(result["extension"], ".pdf")
        self.assertEqual(result["name"], "document.pdf")

        # Test .png extension
        result = self.file_manager.get_file_info("/images/photo.png")
        self.assertEqual(result["extension"], ".png")
        self.assertEqual(result["name"], "photo.png")

        # Test no extension
        result = self.file_manager.get_file_info("/path/to/README")
        self.assertEqual(result["extension"], "")
        self.assertEqual(result["name"], "README")

    @patch("os.stat", side_effect=OSError("Permission denied"))
    @patch("os.path.exists")
    def test_get_file_info_stat_error(self, mock_exists, mock_stat):
        """Test get_file_info handles os.stat errors."""
        mock_exists.return_value = True

        result = self.file_manager.get_file_info("/path/to/protected.txt")

        self.assertIsNone(result)

    @patch("os.stat", side_effect=Exception("Unexpected error"))
    @patch("os.path.exists")
    def test_get_file_info_unexpected_error(self, mock_exists, mock_stat):
        """Test get_file_info handles unexpected errors."""
        mock_exists.return_value = True

        result = self.file_manager.get_file_info("/path/to/file.txt")

        self.assertIsNone(result)

    # ========== prepare_image_messages tests ==========

    def test_prepare_image_messages_empty_list(self):
        """Test prepare_image_messages with empty list."""
        result = self.file_manager.prepare_image_messages([])

        self.assertEqual(result, [])

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"image_data")
    def test_prepare_image_messages_single_image(self, mock_file, mock_exists):
        """Test prepare_image_messages with single image."""
        mock_exists.return_value = True

        result = self.file_manager.prepare_image_messages(["/path/to/image.png"])

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("data:image/png;base64,"))

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"image_data")
    def test_prepare_image_messages_multiple_images(self, mock_file, mock_exists):
        """Test prepare_image_messages with multiple images."""
        mock_exists.return_value = True

        image_paths = [
            "/path/to/image1.png",
            "/path/to/image2.jpg",
            "/path/to/image3.gif",
        ]
        result = self.file_manager.prepare_image_messages(image_paths)

        self.assertEqual(len(result), 3)
        self.assertTrue(result[0].startswith("data:image/png;base64,"))
        self.assertTrue(result[1].startswith("data:image/jpeg;base64,"))
        self.assertTrue(result[2].startswith("data:image/gif;base64,"))

    @patch("os.path.exists")
    def test_prepare_image_messages_with_invalid_images(self, mock_exists):
        """Test prepare_image_messages skips invalid images."""
        # First image exists, second doesn't, third exists
        mock_exists.side_effect = [True, False, True]

        with patch("builtins.open", new_callable=mock_open, read_data=b"image_data"):
            image_paths = [
                "/path/to/valid1.png",
                "/path/to/invalid.png",
                "/path/to/valid2.jpg",
            ]
            result = self.file_manager.prepare_image_messages(image_paths)

        # Should only have 2 valid images
        self.assertEqual(len(result), 2)

    @patch("os.path.exists")
    @patch("builtins.open", side_effect=OSError("Cannot read"))
    def test_prepare_image_messages_with_read_errors(self, mock_file, mock_exists):
        """Test prepare_image_messages handles read errors."""
        mock_exists.return_value = True

        result = self.file_manager.prepare_image_messages(["/path/to/image.png"])

        # Should return empty list when encoding fails
        self.assertEqual(result, [])

    # ========== batch_upload_files tests ==========

    def test_batch_upload_files_empty_list(self):
        """Test batch_upload_files with empty list."""
        result = self.file_manager.batch_upload_files([])

        self.assertEqual(result, {})

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"file_content")
    def test_batch_upload_files_single_file_success(self, mock_file, mock_exists):
        """Test batch_upload_files with single successful upload."""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "file123", "filename": "test.txt"}
        self.base_client.session.post.return_value = mock_response

        result = self.file_manager.batch_upload_files(["/path/to/test.txt"])

        self.assertEqual(len(result), 1)
        self.assertIn("/path/to/test.txt", result)
        self.assertIsNotNone(result["/path/to/test.txt"])
        self.assertEqual(result["/path/to/test.txt"]["id"], "file123")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"file_content")
    def test_batch_upload_files_multiple_files_all_success(
        self, mock_file, mock_exists
    ):
        """Test batch_upload_files with multiple successful uploads."""
        mock_exists.return_value = True

        # Mock different responses for each file
        responses = [
            Mock(
                status_code=200,
                json=lambda: {"id": "file1", "filename": "test1.txt"},
            ),
            Mock(
                status_code=200,
                json=lambda: {"id": "file2", "filename": "test2.txt"},
            ),
            Mock(
                status_code=200,
                json=lambda: {"id": "file3", "filename": "test3.txt"},
            ),
        ]
        self.base_client.session.post.side_effect = responses

        file_paths = [
            "/path/to/test1.txt",
            "/path/to/test2.txt",
            "/path/to/test3.txt",
        ]
        result = self.file_manager.batch_upload_files(file_paths)

        self.assertEqual(len(result), 3)
        self.assertIsNotNone(result["/path/to/test1.txt"])
        self.assertIsNotNone(result["/path/to/test2.txt"])
        self.assertIsNotNone(result["/path/to/test3.txt"])

    @patch("os.path.exists")
    def test_batch_upload_files_mixed_success_and_failure(self, mock_exists):
        """Test batch_upload_files with some successes and some failures."""
        # First file exists, second doesn't, third exists
        mock_exists.side_effect = [True, False, True]

        # Mock responses for existing files
        responses = [
            Mock(
                status_code=200,
                json=lambda: {"id": "file1", "filename": "test1.txt"},
            ),
            Mock(
                status_code=200,
                json=lambda: {"id": "file3", "filename": "test3.txt"},
            ),
        ]

        with patch("builtins.open", new_callable=mock_open, read_data=b"content"):
            self.base_client.session.post.side_effect = responses

            file_paths = [
                "/path/to/test1.txt",
                "/path/to/nonexistent.txt",
                "/path/to/test3.txt",
            ]
            result = self.file_manager.batch_upload_files(file_paths)

        self.assertEqual(len(result), 3)
        self.assertIsNotNone(result["/path/to/test1.txt"])
        self.assertIsNone(result["/path/to/nonexistent.txt"])
        self.assertIsNotNone(result["/path/to/test3.txt"])

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"file_content")
    def test_batch_upload_files_all_failures(self, mock_file, mock_exists):
        """Test batch_upload_files when all uploads fail."""
        mock_exists.return_value = True

        # Mock failed responses
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Upload failed")
        self.base_client.session.post.return_value = mock_response

        file_paths = ["/path/to/test1.txt", "/path/to/test2.txt"]
        result = self.file_manager.batch_upload_files(file_paths)

        self.assertEqual(len(result), 2)
        self.assertIsNone(result["/path/to/test1.txt"])
        self.assertIsNone(result["/path/to/test2.txt"])

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"file_content")
    def test_batch_upload_files_response_without_id(self, mock_file, mock_exists):
        """Test batch_upload_files when response doesn't contain ID."""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"filename": "test.txt"}  # No 'id' field
        self.base_client.session.post.return_value = mock_response

        result = self.file_manager.batch_upload_files(["/path/to/test.txt"])

        self.assertEqual(len(result), 1)
        self.assertIsNone(result["/path/to/test.txt"])


if __name__ == "__main__":
    unittest.main()
