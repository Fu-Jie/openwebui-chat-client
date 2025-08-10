"""
Unit tests for prompts functionality in OpenWebUI Chat Client.
Tests the PromptsManager class and related functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
import json

# Import the classes to test
from openwebui_chat_client import OpenWebUIClient
from openwebui_chat_client.modules.prompts_manager import PromptsManager


class TestPromptsManager(unittest.TestCase):
    """Test cases for PromptsManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = Mock()
        self.base_client.base_url = "http://localhost:3000"
        self.base_client.session = Mock()
        self.base_client.json_headers = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }
        self.prompts_manager = PromptsManager(self.base_client)

    def test_initialization(self):
        """Test prompts manager initialization."""
        self.assertEqual(self.prompts_manager.base_client, self.base_client)

    def test_get_prompts_success(self):
        """Test successful retrieval of prompts."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "command": "/title",
                "user_id": "user123",
                "title": "Title Generator",
                "content": "Generate a title for: {{content}}",
                "timestamp": 1754809938,
                "access_control": {}
            }
        ]
        mock_response.raise_for_status.return_value = None
        self.base_client.session.get.return_value = mock_response

        result = self.prompts_manager.get_prompts()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["command"], "/title")
        self.base_client.session.get.assert_called_once_with(
            "http://localhost:3000/api/v1/prompts/",
            headers=self.base_client.json_headers
        )

    def test_get_prompts_failure(self):
        """Test prompts retrieval failure."""
        self.base_client.session.get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.prompts_manager.get_prompts()

        self.assertIsNone(result)

    def test_create_prompt_success(self):
        """Test successful prompt creation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "command": "/test",
            "user_id": "user123",
            "title": "Test Prompt",
            "content": "This is a test prompt with {{variable}}",
            "timestamp": 1754809938,
            "access_control": {}
        }
        mock_response.raise_for_status.return_value = None
        self.base_client.session.post.return_value = mock_response

        result = self.prompts_manager.create_prompt(
            command="test",
            title="Test Prompt",
            content="This is a test prompt with {{variable}}"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["command"], "/test")
        self.assertEqual(result["title"], "Test Prompt")
        
        # Verify the API call
        self.base_client.session.post.assert_called_once()
        call_args = self.base_client.session.post.call_args
        self.assertEqual(call_args[1]["json"]["command"], "/test")

    def test_create_prompt_auto_slash(self):
        """Test that command automatically gets slash prefix."""
        mock_response = Mock()
        mock_response.json.return_value = {"command": "/test"}
        mock_response.raise_for_status.return_value = None
        self.base_client.session.post.return_value = mock_response

        self.prompts_manager.create_prompt("test", "Title", "Content")

        call_args = self.base_client.session.post.call_args
        self.assertEqual(call_args[1]["json"]["command"], "/test")

    def test_get_prompt_by_command_success(self):
        """Test successful retrieval of prompt by command."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "command": "/summarize",
            "title": "Summarizer",
            "content": "Summarize: {{text}}"
        }
        mock_response.raise_for_status.return_value = None
        self.base_client.session.get.return_value = mock_response

        result = self.prompts_manager.get_prompt_by_command("/summarize")

        self.assertIsNotNone(result)
        self.assertEqual(result["command"], "/summarize")

    def test_get_prompt_by_command_not_found(self):
        """Test prompt not found scenario."""
        mock_response = Mock()
        mock_response.status_code = 404
        error = requests.exceptions.HTTPError()
        error.response = mock_response
        self.base_client.session.get.side_effect = error

        result = self.prompts_manager.get_prompt_by_command("/nonexistent")

        self.assertIsNone(result)

    def test_update_prompt_by_command_success(self):
        """Test successful prompt update."""
        # Mock get_prompt_by_command to return existing prompt
        existing_prompt = {
            "command": "/test",
            "title": "Old Title",
            "content": "Old content",
            "access_control": {}
        }
        
        with patch.object(self.prompts_manager, 'get_prompt_by_command', return_value=existing_prompt):
            mock_response = Mock()
            mock_response.json.return_value = {
                "command": "/test",
                "title": "New Title",
                "content": "Old content"
            }
            mock_response.raise_for_status.return_value = None
            self.base_client.session.post.return_value = mock_response

            result = self.prompts_manager.update_prompt_by_command(
                "/test", 
                title="New Title"
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["title"], "New Title")

    def test_delete_prompt_by_command_success(self):
        """Test successful prompt deletion."""
        mock_response = Mock()
        mock_response.json.return_value = True
        mock_response.raise_for_status.return_value = None
        self.base_client.session.delete.return_value = mock_response

        result = self.prompts_manager.delete_prompt_by_command("/test")

        self.assertTrue(result)

    def test_delete_prompt_by_command_not_found(self):
        """Test deletion of non-existent prompt."""
        mock_response = Mock()
        mock_response.status_code = 404
        error = requests.exceptions.HTTPError()
        error.response = mock_response
        self.base_client.session.delete.side_effect = error

        result = self.prompts_manager.delete_prompt_by_command("/nonexistent")

        self.assertFalse(result)

    def test_extract_variables(self):
        """Test variable extraction from prompt content."""
        content = "Hello {{name}}, please {{action | select:options=[\"review\", \"approve\"]}} this {{document}}."
        
        variables = self.prompts_manager.extract_variables(content)
        
        expected_variables = ["name", "action", "document"]
        self.assertEqual(set(variables), set(expected_variables))

    def test_substitute_variables(self):
        """Test variable substitution in prompt content."""
        content = "Hello {{name}}, your score is {{score}}."
        variables = {"name": "John", "score": 95}
        
        result = self.prompts_manager.substitute_variables(content, variables)
        
        self.assertEqual(result, "Hello John, your score is 95.")

    def test_substitute_variables_with_system_vars(self):
        """Test variable substitution with system variables."""
        content = "Today is {{CURRENT_DATE}} and user {{name}} has {{points}} points."
        variables = {"name": "Alice", "points": 100}
        system_variables = {"CURRENT_DATE": "2024-01-15"}
        
        result = self.prompts_manager.substitute_variables(
            content, variables, system_variables
        )
        
        self.assertEqual(result, "Today is 2024-01-15 and user Alice has 100 points.")

    def test_get_system_variables(self):
        """Test system variables generation."""
        variables = self.prompts_manager.get_system_variables()
        
        self.assertIn("CURRENT_DATE", variables)
        self.assertIn("CURRENT_TIME", variables)
        self.assertIn("CURRENT_DATETIME", variables)
        self.assertIn("CURRENT_WEEKDAY", variables)

    def test_search_prompts(self):
        """Test prompt searching functionality."""
        mock_prompts = [
            {"command": "/summarize", "title": "Text Summarizer", "content": "Summarize text"},
            {"command": "/translate", "title": "Language Translator", "content": "Translate content"},
            {"command": "/review", "title": "Code Reviewer", "content": "Review code"}
        ]
        
        with patch.object(self.prompts_manager, 'get_prompts', return_value=mock_prompts):
            # Search by title
            results = self.prompts_manager.search_prompts("Summarizer", by_title=True)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["command"], "/summarize")
            
            # Search by command
            results = self.prompts_manager.search_prompts("translate", by_command=True)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["command"], "/translate")

    def test_batch_create_prompts_success(self):
        """Test successful batch prompt creation."""
        prompts_data = [
            {"command": "/test1", "title": "Test 1", "content": "Content 1"},
            {"command": "/test2", "title": "Test 2", "content": "Content 2"}
        ]
        
        with patch.object(self.prompts_manager, 'create_prompt', return_value={"success": True}) as mock_create:
            result = self.prompts_manager.batch_create_prompts(prompts_data)
            
            self.assertEqual(result["total"], 2)
            self.assertEqual(len(result["success"]), 2)
            self.assertEqual(len(result["failed"]), 0)
            self.assertEqual(mock_create.call_count, 2)

    def test_batch_delete_prompts_success(self):
        """Test successful batch prompt deletion."""
        commands = ["/test1", "/test2"]
        
        with patch.object(self.prompts_manager, 'delete_prompt_by_command', return_value=True) as mock_delete:
            result = self.prompts_manager.batch_delete_prompts(commands)
            
            self.assertEqual(result["total"], 2)
            self.assertEqual(len(result["success"]), 2)
            self.assertEqual(len(result["failed"]), 0)
            self.assertEqual(mock_delete.call_count, 2)

    def test_replace_prompt_by_command_success(self):
        """Test successful prompt replacement (delete + recreate)."""
        old_prompt = {
            "command": "/old_test",
            "title": "Old Title",
            "content": "Old content",
            "access_control": {}
        }
        
        new_prompt = {
            "command": "/new_test",
            "title": "New Title",
            "content": "New content"
        }
        
        with patch.object(self.prompts_manager, 'get_prompt_by_command') as mock_get:
            with patch.object(self.prompts_manager, 'delete_prompt_by_command', return_value=True) as mock_delete:
                with patch.object(self.prompts_manager, 'create_prompt', return_value=new_prompt) as mock_create:
                    # First call returns old prompt, second call returns None (checking if new command exists)
                    mock_get.side_effect = [old_prompt, None]
                    
                    result = self.prompts_manager.replace_prompt_by_command(
                        "/old_test", "/new_test", "New Title", "New content"
                    )
                    
                    self.assertIsNotNone(result)
                    self.assertEqual(result["command"], "/new_test")
                    self.assertEqual(result["title"], "New Title")
                    mock_delete.assert_called_once_with("/old_test")
                    mock_create.assert_called_once_with("/new_test", "New Title", "New content", None)

    def test_replace_prompt_by_command_old_not_found(self):
        """Test replacement when old prompt doesn't exist."""
        with patch.object(self.prompts_manager, 'get_prompt_by_command', return_value=None):
            result = self.prompts_manager.replace_prompt_by_command(
                "/nonexistent", "/new_test", "New Title", "New content"
            )
            
            self.assertIsNone(result)

    def test_replace_prompt_by_command_new_exists(self):
        """Test replacement when new command already exists."""
        old_prompt = {"command": "/old_test", "title": "Old Title", "content": "Old content"}
        new_prompt = {"command": "/new_test", "title": "Existing Title", "content": "Existing content"}
        
        with patch.object(self.prompts_manager, 'get_prompt_by_command') as mock_get:
            # First call returns old prompt, second call returns existing new prompt
            mock_get.side_effect = [old_prompt, new_prompt]
            
            result = self.prompts_manager.replace_prompt_by_command(
                "/old_test", "/new_test", "New Title", "New content"
            )
            
            self.assertIsNone(result)

    def test_replace_prompt_by_command_delete_failed(self):
        """Test replacement when deletion fails."""
        old_prompt = {"command": "/old_test", "title": "Old Title", "content": "Old content"}
        
        with patch.object(self.prompts_manager, 'get_prompt_by_command') as mock_get:
            with patch.object(self.prompts_manager, 'delete_prompt_by_command', return_value=False):
                # First call returns old prompt, second call returns None (new command doesn't exist)
                mock_get.side_effect = [old_prompt, None]
                
                result = self.prompts_manager.replace_prompt_by_command(
                    "/old_test", "/new_test", "New Title", "New content"
                )
                
                self.assertIsNone(result)

    def test_replace_prompt_by_command_create_failed_with_restore(self):
        """Test replacement when creation fails and restoration succeeds."""
        old_prompt = {
            "command": "/old_test",
            "title": "Old Title", 
            "content": "Old content",
            "access_control": {}
        }
        
        restored_prompt = {
            "command": "/old_test",
            "title": "Old Title",
            "content": "Old content"
        }
        
        with patch.object(self.prompts_manager, 'get_prompt_by_command') as mock_get:
            with patch.object(self.prompts_manager, 'delete_prompt_by_command', return_value=True):
                with patch.object(self.prompts_manager, 'create_prompt') as mock_create:
                    # First call returns old prompt, second call returns None (new command doesn't exist)
                    mock_get.side_effect = [old_prompt, None]
                    # First create call fails, second succeeds (restoration)
                    mock_create.side_effect = [None, restored_prompt]
                    
                    result = self.prompts_manager.replace_prompt_by_command(
                        "/old_test", "/new_test", "New Title", "New content"
                    )
                    
                    self.assertIsNone(result)
                    # Should have tried to create new prompt and then restore
                    self.assertEqual(mock_create.call_count, 2)


class TestOpenWebUIClientPromptsIntegration(unittest.TestCase):
    """Test prompts integration with OpenWebUIClient."""

    def setUp(self):
        """Set up test client."""
        with patch('openwebui_chat_client.openwebui_chat_client.ModelManager'):
            self.client = OpenWebUIClient(
                base_url="http://localhost:3000",
                token="test_token", 
                default_model_id="test-model",
                skip_model_refresh=True
            )

    def test_prompts_manager_initialized(self):
        """Test that prompts manager is properly initialized."""
        self.assertIsNotNone(self.client._prompts_manager)
        self.assertEqual(
            self.client._prompts_manager.base_client, 
            self.client._base_client
        )

    def test_prompts_methods_delegated(self):
        """Test that prompts methods are properly delegated."""
        # Test that methods exist and are callable
        self.assertTrue(hasattr(self.client, 'get_prompts'))
        self.assertTrue(hasattr(self.client, 'create_prompt'))
        self.assertTrue(hasattr(self.client, 'get_prompt_by_command'))
        self.assertTrue(hasattr(self.client, 'update_prompt_by_command'))
        self.assertTrue(hasattr(self.client, 'delete_prompt_by_command'))
        self.assertTrue(hasattr(self.client, 'search_prompts'))
        self.assertTrue(hasattr(self.client, 'extract_variables'))
        self.assertTrue(hasattr(self.client, 'substitute_variables'))

    def test_get_prompts_delegation(self):
        """Test get_prompts method delegation."""
        with patch.object(self.client._prompts_manager, 'get_prompts', return_value=[]) as mock_method:
            result = self.client.get_prompts()
            mock_method.assert_called_once()

    def test_create_prompt_delegation(self):
        """Test create_prompt method delegation."""
        with patch.object(self.client._prompts_manager, 'create_prompt', return_value={}) as mock_method:
            result = self.client.create_prompt("/test", "Test", "Content")
            mock_method.assert_called_once_with("/test", "Test", "Content", None)

    def test_replace_prompt_by_command_method_exists(self):
        """Test that replace_prompt_by_command method exists and is callable."""
        self.assertTrue(hasattr(self.client, 'replace_prompt_by_command'))
        self.assertTrue(callable(getattr(self.client, 'replace_prompt_by_command')))

    def test_replace_prompt_by_command_delegation(self):
        """Test replace_prompt_by_command method delegation."""
        with patch.object(self.client._prompts_manager, 'replace_prompt_by_command', return_value={}) as mock_method:
            result = self.client.replace_prompt_by_command("/old", "/new", "Title", "Content")
            mock_method.assert_called_once_with("/old", "/new", "Title", "Content", None)


if __name__ == '__main__':
    unittest.main()