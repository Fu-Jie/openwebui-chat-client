"""
Extended tests for KnowledgeBaseManager module.

This module tests batch operations and keyword-based deletion functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from openwebui_chat_client.modules.knowledge_base_manager import KnowledgeBaseManager


class TestKnowledgeBaseManagerExtended(unittest.TestCase):
    """Extended test cases for KnowledgeBaseManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = Mock()
        self.base_client.base_url = "http://test.local"
        self.base_client.json_headers = {"Authorization": "Bearer test_token"}
        self.base_client.session = Mock()
        self.manager = KnowledgeBaseManager(self.base_client)

    # =============================================================================
    # Delete by Keyword Tests
    # =============================================================================

    def test_delete_by_keyword_empty_keyword(self):
        """Test deleting knowledge bases with empty keyword."""
        result = self.manager.delete_knowledge_bases_by_keyword("")

        self.assertEqual(result, (0, 0, []))

    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_delete_by_keyword_case_insensitive(self, mock_as_completed, mock_executor):
        """Test deleting knowledge bases with case-insensitive keyword search."""
        mock_kbs = [
            {"id": "kb1", "name": "Test KB 1"},
            {"id": "kb2", "name": "Production KB"},
            {"id": "kb3", "name": "test kb 2"},
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_kbs
        self.base_client.session.get.return_value = mock_response

        # Mock ThreadPoolExecutor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock futures
        future1 = Mock()
        future1.result.return_value = True
        future2 = Mock()
        future2.result.return_value = True

        mock_executor_instance.submit.side_effect = [future1, future2]
        mock_as_completed.return_value = [future1, future2]

        # Mock delete_knowledge_base
        self.manager.delete_knowledge_base = Mock(return_value=True)

        result = self.manager.delete_knowledge_bases_by_keyword(
            "test", case_sensitive=False
        )

        self.assertEqual(result[0], 2)  # successful
        self.assertEqual(result[1], 0)  # failed
        self.assertEqual(len(result[2]), 2)  # processed names
        self.assertIn("Test KB 1", result[2])
        self.assertIn("test kb 2", result[2])

    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_delete_by_keyword_case_sensitive(self, mock_as_completed, mock_executor):
        """Test deleting knowledge bases with case-sensitive keyword search."""
        mock_kbs = [
            {"id": "kb1", "name": "Test KB 1"},
            {"id": "kb2", "name": "test kb 2"},
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_kbs
        self.base_client.session.get.return_value = mock_response

        # Mock ThreadPoolExecutor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock future
        future1 = Mock()
        future1.result.return_value = True

        mock_executor_instance.submit.return_value = future1
        mock_as_completed.return_value = [future1]

        self.manager.delete_knowledge_base = Mock(return_value=True)

        result = self.manager.delete_knowledge_bases_by_keyword(
            "Test", case_sensitive=True
        )

        self.assertEqual(result[0], 1)  # successful
        self.assertEqual(result[1], 0)  # failed
        self.assertEqual(len(result[2]), 1)  # processed names
        self.assertIn("Test KB 1", result[2])

    def test_delete_by_keyword_no_matches(self):
        """Test deleting knowledge bases when no matches found."""
        mock_kbs = [
            {"id": "kb1", "name": "Production KB"},
            {"id": "kb2", "name": "Staging KB"},
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_kbs
        self.base_client.session.get.return_value = mock_response

        result = self.manager.delete_knowledge_bases_by_keyword("nonexistent")

        self.assertEqual(result, (0, 0, []))

    def test_delete_by_keyword_list_fails(self):
        """Test deleting knowledge bases when listing fails."""
        import requests

        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Connection error"
        )

        result = self.manager.delete_knowledge_bases_by_keyword("test")

        self.assertEqual(result, (0, 0, []))

    def test_delete_by_keyword_empty_list(self):
        """Test deleting knowledge bases when list is empty."""
        mock_response = Mock()
        mock_response.json.return_value = []
        self.base_client.session.get.return_value = mock_response

        result = self.manager.delete_knowledge_bases_by_keyword("test")

        self.assertEqual(result, (0, 0, []))

    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_delete_by_keyword_partial_failure(self, mock_as_completed, mock_executor):
        """Test deleting knowledge bases with some failures."""
        mock_kbs = [
            {"id": "kb1", "name": "Test KB 1"},
            {"id": "kb2", "name": "Test KB 2"},
            {"id": "kb3", "name": "Test KB 3"},
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_kbs
        self.base_client.session.get.return_value = mock_response

        # Mock ThreadPoolExecutor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock futures with mixed results
        future1 = Mock()
        future1.result.return_value = True
        future2 = Mock()
        future2.result.return_value = False
        future3 = Mock()
        future3.result.return_value = True

        mock_executor_instance.submit.side_effect = [future1, future2, future3]
        mock_as_completed.return_value = [future1, future2, future3]

        self.manager.delete_knowledge_base = Mock(side_effect=[True, False, True])

        result = self.manager.delete_knowledge_bases_by_keyword("Test")

        self.assertEqual(result[0], 2)  # successful
        self.assertEqual(result[1], 1)  # failed
        self.assertEqual(len(result[2]), 3)  # processed names

    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_delete_by_keyword_missing_id(self, mock_as_completed, mock_executor):
        """Test deleting knowledge bases when some have missing IDs."""
        mock_kbs = [
            {"id": "kb1", "name": "Test KB 1"},
            {"name": "Test KB 2"},  # Missing ID
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_kbs
        self.base_client.session.get.return_value = mock_response

        # Mock ThreadPoolExecutor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock future for the one with ID
        future1 = Mock()
        future1.result.return_value = True

        mock_executor_instance.submit.return_value = future1
        mock_as_completed.return_value = [future1]

        self.manager.delete_knowledge_base = Mock(return_value=True)

        result = self.manager.delete_knowledge_bases_by_keyword("Test")

        self.assertEqual(result[0], 1)  # successful
        self.assertEqual(result[1], 1)  # failed (missing ID)
        self.assertEqual(len(result[2]), 2)  # processed names

    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_delete_by_keyword_exception_during_deletion(
        self, mock_as_completed, mock_executor
    ):
        """Test deleting knowledge bases when exception occurs during deletion."""
        mock_kbs = [
            {"id": "kb1", "name": "Test KB 1"},
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_kbs
        self.base_client.session.get.return_value = mock_response

        # Mock ThreadPoolExecutor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock future that raises exception
        future1 = Mock()
        future1.result.side_effect = Exception("Deletion failed")

        mock_executor_instance.submit.return_value = future1
        mock_as_completed.return_value = [future1]

        result = self.manager.delete_knowledge_bases_by_keyword("Test")

        self.assertEqual(result[0], 0)  # successful
        self.assertEqual(result[1], 1)  # failed
        self.assertEqual(len(result[2]), 1)  # processed names

    # =============================================================================
    # Create Knowledge Bases with Files Tests
    # =============================================================================

    def test_create_with_files_list_format(self):
        """Test creating knowledge bases with files using list format."""
        kb_configs = [
            {"name": "KB1", "description": "First KB", "files": ["file1.txt"]},
            {"name": "KB2", "description": "Second KB", "files": ["file2.txt"]},
        ]

        with patch(
            "openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor"
        ) as mock_executor:
            mock_executor_instance = MagicMock()
            mock_executor.return_value.__enter__.return_value = mock_executor_instance

            # Mock futures
            future1 = Mock()
            future1.result.return_value = ("KB1", True, "")
            future2 = Mock()
            future2.result.return_value = ("KB2", True, "")

            mock_executor_instance.submit.side_effect = [future1, future2]

            with patch(
                "openwebui_chat_client.openwebui_chat_client.as_completed"
            ) as mock_as_completed:
                mock_as_completed.return_value = [future1, future2]

                result = self.manager.create_knowledge_bases_with_files(kb_configs)

                self.assertEqual(len(result["success"]), 2)
                self.assertEqual(len(result["failed"]), 0)
                self.assertIn("KB1", result["success"])
                self.assertIn("KB2", result["success"])

    def test_create_with_files_dict_format(self):
        """Test creating knowledge bases with files using dict format (backward compatibility)."""
        kb_configs = {
            "KB1": ["file1.txt", "file2.txt"],
            "KB2": ["file3.txt"],
        }

        with patch(
            "openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor"
        ) as mock_executor:
            mock_executor_instance = MagicMock()
            mock_executor.return_value.__enter__.return_value = mock_executor_instance

            # Mock futures
            future1 = Mock()
            future1.result.return_value = ("KB1", True, "")
            future2 = Mock()
            future2.result.return_value = ("KB2", True, "")

            mock_executor_instance.submit.side_effect = [future1, future2]

            with patch(
                "openwebui_chat_client.openwebui_chat_client.as_completed"
            ) as mock_as_completed:
                mock_as_completed.return_value = [future1, future2]

                result = self.manager.create_knowledge_bases_with_files(kb_configs)

                self.assertEqual(len(result["success"]), 2)
                self.assertEqual(len(result["failed"]), 0)

    def test_create_with_files_empty_configs(self):
        """Test creating knowledge bases with empty configurations."""
        result = self.manager.create_knowledge_bases_with_files([])

        self.assertEqual(result, {"success": [], "failed": []})

    def test_create_with_files_partial_failure(self):
        """Test creating knowledge bases with some failures."""
        kb_configs = [
            {"name": "KB1", "description": "First KB", "files": ["file1.txt"]},
            {"name": "KB2", "description": "Second KB", "files": ["file2.txt"]},
        ]

        with patch(
            "openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor"
        ) as mock_executor:
            mock_executor_instance = MagicMock()
            mock_executor.return_value.__enter__.return_value = mock_executor_instance

            # Mock futures with mixed results
            future1 = Mock()
            future1.result.return_value = ("KB1", True, "")
            future2 = Mock()
            future2.result.return_value = ("KB2", False, "Creation failed")

            mock_executor_instance.submit.side_effect = [future1, future2]

            with patch(
                "openwebui_chat_client.openwebui_chat_client.as_completed"
            ) as mock_as_completed:
                mock_as_completed.return_value = [future1, future2]

                result = self.manager.create_knowledge_bases_with_files(kb_configs)

                self.assertEqual(len(result["success"]), 1)
                self.assertEqual(len(result["failed"]), 1)
                self.assertIn("KB1", result["success"])
                self.assertIn("KB2", result["failed"])

    def test_create_with_files_exception(self):
        """Test creating knowledge bases when exception occurs."""
        kb_configs = [
            {"name": "KB1", "description": "First KB", "files": ["file1.txt"]},
        ]

        with patch(
            "openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor"
        ) as mock_executor:
            mock_executor_instance = MagicMock()
            mock_executor.return_value.__enter__.return_value = mock_executor_instance

            # Mock future that raises exception
            future1 = Mock()
            future1.result.side_effect = Exception("Processing failed")

            mock_executor_instance.submit.return_value = future1

            with patch(
                "openwebui_chat_client.openwebui_chat_client.as_completed"
            ) as mock_as_completed:
                mock_as_completed.return_value = [future1]

                result = self.manager.create_knowledge_bases_with_files(kb_configs)

                # When exception occurs, it's logged but not added to failed list
                # This is the actual behavior of the code
                self.assertEqual(len(result["success"]), 0)
                self.assertEqual(len(result["failed"]), 0)

    # =============================================================================
    # Get Knowledge Base Details Tests
    # =============================================================================

    def test_get_kb_details_success(self):
        """Test getting knowledge base details successfully."""
        mock_details = {
            "id": "kb123",
            "name": "Test KB",
            "description": "Test description",
            "files": ["file1.txt", "file2.txt"],
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_details
        self.base_client.session.get.return_value = mock_response

        result = self.manager.get_knowledge_base_details("kb123")

        self.assertEqual(result, mock_details)
        self.base_client.session.get.assert_called_once()

    def test_get_kb_details_http_error(self):
        """Test getting knowledge base details with HTTP error."""
        import requests

        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "HTTP 404"
        )

        result = self.manager.get_knowledge_base_details("kb123")

        self.assertIsNone(result)

    # =============================================================================
    # List Knowledge Bases Tests
    # =============================================================================

    def test_list_knowledge_bases_success(self):
        """Test listing knowledge bases successfully."""
        mock_kbs = [
            {"id": "kb1", "name": "KB 1"},
            {"id": "kb2", "name": "KB 2"},
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_kbs
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_knowledge_bases()

        self.assertEqual(result, mock_kbs)
        self.assertEqual(len(result), 2)

    def test_list_knowledge_bases_empty(self):
        """Test listing knowledge bases when none exist."""
        mock_response = Mock()
        mock_response.json.return_value = []
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_knowledge_bases()

        self.assertEqual(result, [])

    def test_list_knowledge_bases_error(self):
        """Test listing knowledge bases with error."""
        import requests

        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Connection error"
        )

        result = self.manager.list_knowledge_bases()

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
