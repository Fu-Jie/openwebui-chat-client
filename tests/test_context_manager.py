"""
Tests for context manager functionality of OpenWebUIClient.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient


class TestContextManager(unittest.TestCase):
    """Test context manager implementation for OpenWebUIClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "http://localhost:3000"
        self.token = "test-token"
        self.default_model = "test-model:latest"

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session")
    def test_context_manager_basic(self, mock_session_class):
        """Test basic context manager usage."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Use client as context manager
        with OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        ) as client:
            # Verify client is returned
            self.assertIsNotNone(client)
            self.assertEqual(client.base_url, self.base_url)
        
        # Verify session was closed
        mock_session.close.assert_called_once()

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session")
    def test_context_manager_with_exception(self, mock_session_class):
        """Test context manager cleanup when exception occurs."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Use client with exception
        with self.assertRaises(ValueError):
            with OpenWebUIClient(
                base_url=self.base_url,
                token=self.token,
                default_model_id=self.default_model,
                skip_model_refresh=True,
            ) as client:
                # Raise an exception inside the with block
                raise ValueError("Test exception")
        
        # Verify session was still closed despite exception
        mock_session.close.assert_called_once()

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session")
    def test_explicit_close(self, mock_session_class):
        """Test explicit close() method."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        
        # Explicitly close the client
        client.close()
        
        # Verify session was closed
        mock_session.close.assert_called_once()

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session")
    def test_close_with_placeholder_cleanup(self, mock_session_class):
        """Test close() method with placeholder message cleanup."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        
        # Setup conditions for placeholder cleanup
        client._base_client._auto_cleanup_enabled = True
        client.chat_id = "test-chat-id"
        client.chat_object_from_server = {"chat": {"id": "test-chat-id"}}
        
        # Mock the cleanup method
        client._cleanup_unused_placeholder_messages = Mock(return_value=2)
        
        # Close the client
        client.close()
        
        # Verify cleanup was called
        client._cleanup_unused_placeholder_messages.assert_called_once()
        
        # Verify session was closed
        mock_session.close.assert_called_once()

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session")
    def test_close_idempotent(self, mock_session_class):
        """Test that close() can be called multiple times safely."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        
        # Call close multiple times
        client.close()
        client.close()
        client.close()
        
        # Session close should be called multiple times (but session handles it gracefully)
        # We just verify no exceptions are raised
        self.assertTrue(mock_session.close.called)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session")
    def test_enter_returns_self(self, mock_session_class):
        """Test that __enter__ returns the client instance."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        
        result = client.__enter__()
        
        self.assertIs(result, client)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session")
    def test_exit_returns_false(self, mock_session_class):
        """Test that __exit__ returns False (don't suppress exceptions)."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        
        client._auto_cleanup_enabled = False  # Disable cleanup for this test
        
        result = client.__exit__(None, None, None)
        
        self.assertFalse(result)
        mock_session.close.assert_called_once()

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session")
    def test_del_calls_close(self, mock_session_class):
        """Test that __del__ calls close() for cleanup."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        
        client._auto_cleanup_enabled = False  # Disable cleanup for this test
        
        # Manually call __del__
        client.__del__()
        
        # Verify session was closed
        mock_session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
