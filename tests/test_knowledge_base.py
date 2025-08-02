import unittest
from unittest.mock import Mock, patch, MagicMock, call
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient


class TestOpenWebUIClientKnowledgeBase(unittest.TestCase):
    """Unit tests for OpenWebUIClient knowledge base functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "http://localhost:3000"
        self.token = "test-token"
        self.default_model = "test-model:latest"
        
        # Create client with skip_model_refresh to prevent HTTP requests during initialization
        self.client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        self.client._auto_cleanup_enabled = False

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    @patch.object(OpenWebUIClient, "get_knowledge_base_by_name")
    def test_add_file_to_knowledge_base_create_new_kb(self, mock_get_kb, mock_post):
        """Test adding file to a knowledge base that doesn't exist (creates new one)."""
        kb_name = "new-kb"
        file_path = "/tmp/test.pdf"

        # Mock knowledge base doesn't exist initially
        mock_get_kb.return_value = None

        # Mock create_knowledge_base
        with patch.object(self.client, "create_knowledge_base") as mock_create:
            mock_create.return_value = {"id": "new-kb-id", "name": kb_name}

            # Mock _upload_file
            with patch.object(self.client, "_upload_file") as mock_upload:
                mock_upload.return_value = {"id": "file123", "name": "test.pdf"}

                # Mock the add file request
                mock_response = Mock()
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                result = self.client.add_file_to_knowledge_base(file_path, kb_name)

                self.assertTrue(result)
                mock_create.assert_called_once_with(kb_name)
                mock_upload.assert_called_once_with(file_path)
                mock_post.assert_called_once_with(
                    f"{self.base_url}/api/v1/knowledge/new-kb-id/file/add",
                    json={"file_id": "file123"},
                    headers=self.client.json_headers,
                )

    @patch.object(OpenWebUIClient, "get_knowledge_base_by_name")
    @patch.object(OpenWebUIClient, "_upload_file")
    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_add_file_to_existing_knowledge_base(
        self, mock_post, mock_upload, mock_get_kb
    ):
        """Test adding file to an existing knowledge base."""
        kb_name = "existing-kb"
        file_path = "/tmp/test.pdf"

        # Mock existing knowledge base
        mock_get_kb.return_value = {"id": "existing-kb-id", "name": kb_name}

        # Mock file upload
        mock_upload.return_value = {"id": "file123", "name": "test.pdf"}

        # Mock the add file request
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.add_file_to_knowledge_base(file_path, kb_name)

        self.assertTrue(result)
        mock_upload.assert_called_once_with(file_path)
        mock_post.assert_called_once_with(
            f"{self.base_url}/api/v1/knowledge/existing-kb-id/file/add",
            json={"file_id": "file123"},
            headers=self.client.json_headers,
        )

    @patch.object(OpenWebUIClient, "get_knowledge_base_by_name")
    def test_add_file_to_knowledge_base_kb_creation_fails(self, mock_get_kb):
        """Test adding file when knowledge base creation fails."""
        kb_name = "failing-kb"
        file_path = "/tmp/test.pdf"

        # Mock knowledge base doesn't exist
        mock_get_kb.return_value = None

        # Mock create_knowledge_base to fail
        with patch.object(self.client, "create_knowledge_base", return_value=None):
            result = self.client.add_file_to_knowledge_base(file_path, kb_name)

            self.assertFalse(result)

    @patch.object(OpenWebUIClient, "get_knowledge_base_by_name")
    @patch.object(OpenWebUIClient, "_upload_file")
    def test_add_file_to_knowledge_base_upload_fails(self, mock_upload, mock_get_kb):
        """Test adding file when file upload fails."""
        kb_name = "test-kb"
        file_path = "/tmp/test.pdf"

        # Mock existing knowledge base
        mock_get_kb.return_value = {"id": "kb-id", "name": kb_name}

        # Mock file upload failure
        mock_upload.return_value = None

        result = self.client.add_file_to_knowledge_base(file_path, kb_name)

        self.assertFalse(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_delete_all_knowledge_bases_success(
        self, mock_as_completed, mock_executor, mock_get
    ):
        """Test successful deletion of all knowledge bases."""
        # Mock list of knowledge bases
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "kb1", "name": "KB 1"},
            {"id": "kb2", "name": "KB 2"},
            {"id": "kb3", "name": "KB 3"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock executor and futures
        mock_future1 = Mock()
        mock_future1.result.return_value = True
        mock_future2 = Mock()
        mock_future2.result.return_value = True
        mock_future3 = Mock()
        mock_future3.result.return_value = False  # One failure

        mock_executor_instance = Mock()
        mock_executor_instance.submit.side_effect = [
            mock_future1,
            mock_future2,
            mock_future3,
        ]
        mock_executor_instance.__enter__ = Mock(return_value=mock_executor_instance)
        mock_executor_instance.__exit__ = Mock(return_value=None)
        mock_executor.return_value = mock_executor_instance

        # Mock as_completed
        mock_as_completed.return_value = [mock_future1, mock_future2, mock_future3]

        successful, failed = self.client.delete_all_knowledge_bases()

        self.assertEqual(successful, 2)
        self.assertEqual(failed, 1)
        self.assertEqual(mock_executor_instance.submit.call_count, 3)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_delete_all_knowledge_bases_empty_list(self, mock_get):
        """Test deleting all knowledge bases when none exist."""
        # Mock empty list
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        successful, failed = self.client.delete_all_knowledge_bases()

        self.assertEqual(successful, 0)
        self.assertEqual(failed, 0)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_delete_knowledge_bases_by_keyword_success(
        self, mock_as_completed, mock_executor, mock_get
    ):
        """Test successful deletion of knowledge bases by keyword."""
        keyword = "test"

        # Mock list of knowledge bases
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "kb1", "name": "Test KB 1"},
            {"id": "kb2", "name": "Other KB"},
            {"id": "kb3", "name": "Another Test KB"},
            {"id": "kb4", "name": "Production KB"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock executor and futures (only for matching KBs)
        mock_future1 = Mock()
        mock_future1.result.return_value = True
        mock_future2 = Mock()
        mock_future2.result.return_value = True

        mock_executor_instance = Mock()
        mock_executor_instance.submit.side_effect = [mock_future1, mock_future2]
        mock_executor_instance.__enter__ = Mock(return_value=mock_executor_instance)
        mock_executor_instance.__exit__ = Mock(return_value=None)
        mock_executor.return_value = mock_executor_instance

        # Mock as_completed
        mock_as_completed.return_value = [mock_future1, mock_future2]

        successful, failed, names = self.client.delete_knowledge_bases_by_keyword(
            keyword
        )

        self.assertEqual(successful, 2)
        self.assertEqual(failed, 0)
        self.assertEqual(len(names), 2)
        self.assertIn("Test KB 1", names)
        self.assertIn("Another Test KB", names)
        self.assertEqual(mock_executor_instance.submit.call_count, 2)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_delete_knowledge_bases_by_keyword_no_matches(self, mock_get):
        """Test deleting knowledge bases by keyword when no matches exist."""
        keyword = "nonexistent"

        # Mock list of knowledge bases
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "kb1", "name": "Test KB 1"},
            {"id": "kb2", "name": "Other KB"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        successful, failed, names = self.client.delete_knowledge_bases_by_keyword(
            keyword
        )

        self.assertEqual(successful, 0)
        self.assertEqual(failed, 0)
        self.assertEqual(len(names), 0)

    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_create_knowledge_bases_with_files_success(
        self, mock_as_completed, mock_executor
    ):
        """Test successful batch creation of knowledge bases with files."""
        kb_files = {
            "KB 1": ["/tmp/file1.pdf", "/tmp/file2.pdf"],
            "KB 2": ["/tmp/file3.pdf"],
        }

        # Mock the _process_single_kb function results
        mock_future1 = Mock()
        mock_future1.result.return_value = ("KB 1", True, None)
        mock_future2 = Mock()
        mock_future2.result.return_value = ("KB 2", True, None)

        mock_executor_instance = Mock()
        mock_executor_instance.submit.side_effect = [mock_future1, mock_future2]
        mock_executor_instance.__enter__ = Mock(return_value=mock_executor_instance)
        mock_executor_instance.__exit__ = Mock(return_value=None)
        mock_executor.return_value = mock_executor_instance

        # Mock as_completed
        mock_as_completed.return_value = [mock_future1, mock_future2]

        # Mock the individual operations
        with patch.object(self.client, "create_knowledge_base") as mock_create:
            with patch.object(
                self.client, "add_file_to_knowledge_base"
            ) as mock_add_file:
                mock_create.side_effect = [
                    {"id": "kb1-id", "name": "KB 1"},
                    {"id": "kb2-id", "name": "KB 2"},
                ]
                mock_add_file.return_value = True

                result = self.client.create_knowledge_bases_with_files(kb_files)

        self.assertIn("success", result)
        self.assertIn("failed", result)
        self.assertEqual(len(result["success"]), 2)
        self.assertEqual(len(result["failed"]), 0)
        self.assertIn("KB 1", result["success"])
        self.assertIn("KB 2", result["success"])

    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_create_knowledge_bases_with_files_partial_failure(
        self, mock_as_completed, mock_executor
    ):
        """Test batch creation with some failures."""
        kb_files = {"Success KB": ["/tmp/file1.pdf"], "Fail KB": ["/tmp/file2.pdf"]}

        # Mock the _process_single_kb function results
        mock_future1 = Mock()
        mock_future1.result.return_value = ("Success KB", True, None)
        mock_future2 = Mock()
        mock_future2.result.return_value = ("Fail KB", False, "Creation failed")

        mock_executor_instance = Mock()
        mock_executor_instance.submit.side_effect = [mock_future1, mock_future2]
        mock_executor_instance.__enter__ = Mock(return_value=mock_executor_instance)
        mock_executor_instance.__exit__ = Mock(return_value=None)
        mock_executor.return_value = mock_executor_instance

        # Mock as_completed
        mock_as_completed.return_value = [mock_future1, mock_future2]

        result = self.client.create_knowledge_bases_with_files(kb_files)

        self.assertEqual(len(result["success"]), 1)
        self.assertEqual(len(result["failed"]), 1)
        self.assertIn("Success KB", result["success"])
        self.assertIn("Fail KB", result["failed"])
        self.assertEqual(result["failed"]["Fail KB"], "Creation failed")

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_knowledge_base_details_success(self, mock_get):
        """Test successful knowledge base details retrieval."""
        kb_id = "test-kb-id"

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": kb_id,
            "name": "Test KB",
            "description": "A test knowledge base",
            "files": [
                {"id": "file1", "name": "doc1.pdf"},
                {"id": "file2", "name": "doc2.pdf"},
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client._get_knowledge_base_details(kb_id)

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], kb_id)
        self.assertEqual(result["name"], "Test KB")
        self.assertEqual(len(result["files"]), 2)
        mock_get.assert_called_once_with(
            f"{self.base_url}/api/v1/knowledge/{kb_id}",
            headers=self.client.json_headers,
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_knowledge_base_details_failure(self, mock_get):
        """Test knowledge base details retrieval failure."""
        from requests.exceptions import RequestException

        mock_get.side_effect = RequestException("Network error")

        result = self.client._get_knowledge_base_details("kb_id")

        self.assertIsNone(result)

    @patch.object(OpenWebUIClient, "get_knowledge_base_by_name")
    @patch.object(OpenWebUIClient, "create_knowledge_base")
    @patch.object(OpenWebUIClient, "_upload_file")
    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_add_file_to_knowledge_base_comprehensive_flow(
        self, mock_post, mock_upload, mock_create, mock_get_kb
    ):
        """Test the complete flow of adding a file to a knowledge base."""
        kb_name = "comprehensive-test-kb"
        file_path = "/tmp/comprehensive-test.pdf"

        # Scenario: KB doesn't exist, needs to be created
        mock_get_kb.side_effect = [None, {"id": "new-kb-id", "name": kb_name}]

        # Mock KB creation
        mock_create.return_value = {"id": "new-kb-id", "name": kb_name}

        # Mock file upload
        mock_upload.return_value = {
            "id": "uploaded-file-id",
            "name": "comprehensive-test.pdf",
            "type": "application/pdf",
        }

        # Mock add file to KB request
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.add_file_to_knowledge_base(file_path, kb_name)

        # Verify the complete flow
        self.assertTrue(result)

        # Check that get_knowledge_base_by_name was called (first time returns None, second time after creation)
        self.assertEqual(mock_get_kb.call_count, 1)

        # Check that create_knowledge_base was called
        mock_create.assert_called_once_with(kb_name)

        # Check that file was uploaded
        mock_upload.assert_called_once_with(file_path)

        # Check that file was added to KB
        mock_post.assert_called_once_with(
            f"{self.base_url}/api/v1/knowledge/new-kb-id/file/add",
            json={"file_id": "uploaded-file-id"},
            headers=self.client.json_headers,
        )

    def test_handle_rag_references_mixed_scenario(self):
        """Test RAG reference handling with both files and collections."""
        rag_files = ["/tmp/file1.pdf", "/tmp/file2.pdf"]
        rag_collections = ["kb1", "kb2"]

        # Mock file uploads
        with patch.object(self.client, "_upload_file") as mock_upload:
            mock_upload.side_effect = [
                {"id": "file1-id", "name": "file1.pdf", "type": "application/pdf"},
                {"id": "file2-id", "name": "file2.pdf", "type": "application/pdf"},
            ]

            # Mock knowledge base operations
            with patch.object(self.client, "get_knowledge_base_by_name") as mock_get_kb:
                with patch.object(
                    self.client, "_get_knowledge_base_details"
                ) as mock_get_kb_details:
                    mock_get_kb.side_effect = [
                        {"id": "kb1-id", "name": "kb1"},
                        {"id": "kb2-id", "name": "kb2"},
                    ]
                    mock_get_kb_details.side_effect = [
                        {
                            "id": "kb1-id",
                            "name": "kb1",
                            "files": [{"id": "kb1-file1"}, {"id": "kb1-file2"}],
                        },
                        {"id": "kb2-id", "name": "kb2", "files": [{"id": "kb2-file1"}]},
                    ]

                    api_payload, storage_payload = self.client._handle_rag_references(
                        rag_files, rag_collections
                    )

        # Verify results
        self.assertEqual(len(api_payload), 4)  # 2 files + 2 collections
        self.assertEqual(len(storage_payload), 4)

        # Check file payloads
        file_payloads = [p for p in api_payload if p["type"] == "file"]
        self.assertEqual(len(file_payloads), 2)

        # Check collection payloads
        collection_payloads = [p for p in api_payload if p["type"] == "collection"]
        self.assertEqual(len(collection_payloads), 2)

        # Verify collection data structure
        kb1_payload = next(p for p in collection_payloads if p["id"] == "kb1-id")
        self.assertEqual(len(kb1_payload["data"]["file_ids"]), 2)

        kb2_payload = next(p for p in collection_payloads if p["id"] == "kb2-id")
        self.assertEqual(len(kb2_payload["data"]["file_ids"]), 1)

    def test_handle_rag_references_missing_knowledge_base(self):
        """Test RAG reference handling when a knowledge base doesn't exist."""
        rag_collections = ["existing-kb", "missing-kb"]

        with patch.object(self.client, "get_knowledge_base_by_name") as mock_get_kb:
            mock_get_kb.side_effect = [
                {"id": "existing-kb-id", "name": "existing-kb"},
                None,  # missing-kb doesn't exist
            ]

            with patch.object(
                self.client, "_get_knowledge_base_details"
            ) as mock_get_kb_details:
                mock_get_kb_details.return_value = {
                    "id": "existing-kb-id",
                    "name": "existing-kb",
                    "files": [{"id": "file1"}],
                }

                api_payload, storage_payload = self.client._handle_rag_references(
                    None, rag_collections
                )

        # Should only have one collection (the existing one)
        self.assertEqual(len(api_payload), 1)
        self.assertEqual(len(storage_payload), 1)
        self.assertEqual(api_payload[0]["id"], "existing-kb-id")

    def test_handle_rag_references_kb_details_failure(self):
        """Test RAG reference handling when getting KB details fails."""
        rag_collections = ["test-kb"]

        with patch.object(self.client, "get_knowledge_base_by_name") as mock_get_kb:
            mock_get_kb.return_value = {"id": "test-kb-id", "name": "test-kb"}

            with patch.object(
                self.client, "_get_knowledge_base_details"
            ) as mock_get_kb_details:
                mock_get_kb_details.return_value = None  # Details retrieval fails

                api_payload, storage_payload = self.client._handle_rag_references(
                    None, rag_collections
                )

        # Should have no payloads due to details failure
        self.assertEqual(len(api_payload), 0)
        self.assertEqual(len(storage_payload), 0)


if __name__ == "__main__":
    unittest.main()
