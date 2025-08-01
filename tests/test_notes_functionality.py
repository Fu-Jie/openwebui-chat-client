import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from openwebui_chat_client import OpenWebUIClient


class TestNotesFunctionality(unittest.TestCase):
    def setUp(self):
        """Set up test client with mocked session."""
        self.client = OpenWebUIClient(
            base_url="https://test.example.com",
            token="test_token",
            default_model_id="test_model",
            skip_model_refresh=True
        )
        # Mock the session to avoid actual HTTP calls
        self.client.session = Mock()

    def test_get_notes_success(self):
        """Test successful notes retrieval."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {
                "id": "note1",
                "user_id": "user1",
                "title": "Test Note 1",
                "data": None,
                "meta": None,
                "access_control": None,
                "created_at": 1234567890,
                "updated_at": 1234567890,
                "user": {"id": "user1", "name": "Test User", "email": "test@example.com", "role": "user", "profile_image_url": "/default.png"}
            }
        ]
        self.client.session.get.return_value = mock_response

        result = self.client.get_notes()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "note1")
        self.client.session.get.assert_called_once_with(
            "https://test.example.com/api/v1/notes/",
            headers=self.client.json_headers
        )

    def test_get_notes_list_success(self):
        """Test successful notes list retrieval."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {
                "id": "note1",
                "title": "Test Note 1",
                "updated_at": 1234567890,
                "created_at": 1234567890
            }
        ]
        self.client.session.get.return_value = mock_response

        result = self.client.get_notes_list()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "note1")
        self.client.session.get.assert_called_once_with(
            "https://test.example.com/api/v1/notes/list",
            headers=self.client.json_headers
        )

    def test_create_note_success(self):
        """Test successful note creation."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "new_note_id",
            "user_id": "user1",
            "title": "New Test Note",
            "data": {"content": "test content"},
            "meta": {"tags": ["test"]},
            "access_control": None,
            "created_at": 1234567890,
            "updated_at": 1234567890
        }
        self.client.session.post.return_value = mock_response

        result = self.client.create_note(
            title="New Test Note",
            data={"content": "test content"},
            meta={"tags": ["test"]}
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "new_note_id")
        self.assertEqual(result["title"], "New Test Note")
        
        expected_payload = {
            "title": "New Test Note",
            "data": {"content": "test content"},
            "meta": {"tags": ["test"]}
        }
        self.client.session.post.assert_called_once_with(
            "https://test.example.com/api/v1/notes/create",
            json=expected_payload,
            headers=self.client.json_headers
        )

    def test_create_note_minimal(self):
        """Test note creation with only required fields."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "new_note_id",
            "user_id": "user1",
            "title": "Minimal Note",
            "data": None,
            "meta": None,
            "access_control": None,
            "created_at": 1234567890,
            "updated_at": 1234567890
        }
        self.client.session.post.return_value = mock_response

        result = self.client.create_note(title="Minimal Note")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Minimal Note")
        
        expected_payload = {"title": "Minimal Note"}
        self.client.session.post.assert_called_once_with(
            "https://test.example.com/api/v1/notes/create",
            json=expected_payload,
            headers=self.client.json_headers
        )

    def test_get_note_by_id_success(self):
        """Test successful note retrieval by ID."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "note123",
            "user_id": "user1",
            "title": "Test Note",
            "data": {"content": "note content"},
            "meta": None,
            "access_control": None,
            "created_at": 1234567890,
            "updated_at": 1234567890
        }
        self.client.session.get.return_value = mock_response

        result = self.client.get_note_by_id("note123")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "note123")
        self.assertEqual(result["title"], "Test Note")
        self.client.session.get.assert_called_once_with(
            "https://test.example.com/api/v1/notes/note123",
            headers=self.client.json_headers
        )

    def test_update_note_by_id_success(self):
        """Test successful note update."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "note123",
            "user_id": "user1",
            "title": "Updated Note Title",
            "data": {"content": "updated content"},
            "meta": {"tags": ["updated"]},
            "access_control": None,
            "created_at": 1234567890,
            "updated_at": 1234567900
        }
        self.client.session.post.return_value = mock_response

        result = self.client.update_note_by_id(
            note_id="note123",
            title="Updated Note Title",
            data={"content": "updated content"},
            meta={"tags": ["updated"]}
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Updated Note Title")
        
        expected_payload = {
            "title": "Updated Note Title",
            "data": {"content": "updated content"},
            "meta": {"tags": ["updated"]}
        }
        self.client.session.post.assert_called_once_with(
            "https://test.example.com/api/v1/notes/note123/update",
            json=expected_payload,
            headers=self.client.json_headers
        )

    def test_delete_note_by_id_success(self):
        """Test successful note deletion."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = True
        self.client.session.delete.return_value = mock_response

        result = self.client.delete_note_by_id("note123")

        self.assertTrue(result)
        self.client.session.delete.assert_called_once_with(
            "https://test.example.com/api/v1/notes/note123/delete",
            headers=self.client.json_headers
        )

    def test_delete_note_by_id_failure(self):
        """Test note deletion failure."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = False
        self.client.session.delete.return_value = mock_response

        result = self.client.delete_note_by_id("note123")

        self.assertFalse(result)

    def test_get_notes_http_error(self):
        """Test handling of HTTP errors during notes retrieval."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        self.client.session.get.return_value = mock_response

        result = self.client.get_notes()

        self.assertIsNone(result)

    def test_create_note_http_error(self):
        """Test handling of HTTP errors during note creation."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 422")
        self.client.session.post.return_value = mock_response

        result = self.client.create_note(title="Test Note")

        self.assertIsNone(result)


if __name__ == '__main__':
    # Override HTTP requests to avoid connection errors during initialization
    with patch('openwebui_chat_client.modules.model_manager.requests.Session.get') as mock_get:
        # Mock the models list response during initialization
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"id": "test_model", "name": "Test Model"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        unittest.main()