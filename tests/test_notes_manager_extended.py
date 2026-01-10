"""
Extended tests for NotesManager to improve coverage.

This test file focuses on testing NotesManager CRUD operations
and error handling.
"""

import json
import unittest
from unittest.mock import Mock

import requests

from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.modules.notes_manager import NotesManager


class TestNotesManagerExtended(unittest.TestCase):
    """Extended tests for NotesManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = Mock(spec=BaseClient)
        self.base_client.base_url = "http://localhost:3000"
        self.base_client.session = Mock()
        self.base_client.json_headers = {"Authorization": "Bearer test_token"}
        self.manager = NotesManager(self.base_client)

    def test_initialization(self):
        """Test NotesManager initialization."""
        self.assertEqual(self.manager.base_client, self.base_client)

    def test_get_notes_request_exception(self):
        """Test get_notes handles request exception."""
        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Error"
        )

        result = self.manager.get_notes()

        self.assertIsNone(result)

    def test_get_notes_json_decode_error(self):
        """Test get_notes handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.get_notes()

        self.assertIsNone(result)

    def test_get_notes_list_success(self):
        """Test get_notes_list successfully retrieves notes."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "note1", "title": "Note 1", "created_at": 1000, "updated_at": 2000},
            {"id": "note2", "title": "Note 2", "created_at": 1500, "updated_at": 2500},
        ]
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.get_notes_list()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

    def test_get_notes_list_request_exception(self):
        """Test get_notes_list handles request exception."""
        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Error"
        )

        result = self.manager.get_notes_list()

        self.assertIsNone(result)

    def test_create_note_request_exception(self):
        """Test create_note handles request exception."""
        self.base_client.session.post.side_effect = (
            requests.exceptions.RequestException("Error")
        )

        result = self.manager.create_note("Test Note")

        self.assertIsNone(result)

    def test_create_note_json_decode_error(self):
        """Test create_note handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.post.return_value = mock_response

        result = self.manager.create_note("Test Note")

        self.assertIsNone(result)

    def test_create_note_with_all_params(self):
        """Test create_note with all parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "note1",
            "title": "Test Note",
            "data": {"content": "test"},
            "meta": {"tags": ["test"]},
            "access_control": {"read": {"user_ids": ["user1"]}},
        }
        mock_response.raise_for_status = Mock()
        self.base_client.session.post.return_value = mock_response

        result = self.manager.create_note(
            title="Test Note",
            data={"content": "test"},
            meta={"tags": ["test"]},
            access_control={"read": {"user_ids": ["user1"]}},
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "note1")

    def test_get_note_by_id_request_exception(self):
        """Test get_note_by_id handles request exception."""
        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Error"
        )

        result = self.manager.get_note_by_id("note1")

        self.assertIsNone(result)

    def test_get_note_by_id_json_decode_error(self):
        """Test get_note_by_id handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.get_note_by_id("note1")

        self.assertIsNone(result)

    def test_update_note_by_id_request_exception(self):
        """Test update_note_by_id handles request exception."""
        self.base_client.session.post.side_effect = (
            requests.exceptions.RequestException("Error")
        )

        result = self.manager.update_note_by_id("note1", title="Updated")

        self.assertIsNone(result)

    def test_update_note_by_id_json_decode_error(self):
        """Test update_note_by_id handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.post.return_value = mock_response

        result = self.manager.update_note_by_id("note1", title="Updated")

        self.assertIsNone(result)

    def test_update_note_by_id_with_all_params(self):
        """Test update_note_by_id with all parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "note1",
            "title": "Updated Note",
            "data": {"content": "updated"},
            "meta": {"tags": ["updated"]},
            "access_control": {"read": {"user_ids": ["user2"]}},
        }
        mock_response.raise_for_status = Mock()
        self.base_client.session.post.return_value = mock_response

        result = self.manager.update_note_by_id(
            note_id="note1",
            title="Updated Note",
            data={"content": "updated"},
            meta={"tags": ["updated"]},
            access_control={"read": {"user_ids": ["user2"]}},
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Updated Note")

    def test_delete_note_by_id_success(self):
        """Test delete_note_by_id successfully deletes note."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        self.base_client.session.delete.return_value = mock_response

        result = self.manager.delete_note_by_id("note1")

        self.assertTrue(result)

    def test_delete_note_by_id_request_exception(self):
        """Test delete_note_by_id handles request exception."""
        self.base_client.session.delete.side_effect = (
            requests.exceptions.RequestException("Error")
        )

        result = self.manager.delete_note_by_id("note1")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
