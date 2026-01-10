"""
Extended tests for PromptsManager module.

This module tests batch operations, search functionality, and variable handling.
"""

import unittest
from unittest.mock import Mock

from openwebui_chat_client.modules.prompts_manager import PromptsManager


class TestPromptsManagerExtended(unittest.TestCase):
    """Extended test cases for PromptsManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = Mock()
        self.base_client.base_url = "http://test.local"
        self.base_client.json_headers = {"Authorization": "Bearer test_token"}
        self.base_client.session = Mock()
        self.manager = PromptsManager(self.base_client)

    # =============================================================================
    # Search Tests
    # =============================================================================

    def test_search_prompts_by_title(self):
        """Test searching prompts by title."""
        mock_prompts = [
            {
                "command": "/sum",
                "title": "Summarize Text",
                "content": "Summarize {{text}}",
            },
            {
                "command": "/trans",
                "title": "Translate",
                "content": "Translate {{text}}",
            },
            {"command": "/code", "title": "Code Review", "content": "Review {{code}}"},
        ]
        self.manager.get_prompts = Mock(return_value=mock_prompts)

        results = self.manager.search_prompts(query="Translate", by_title=True)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["command"], "/trans")

    def test_search_prompts_by_command(self):
        """Test searching prompts by command."""
        mock_prompts = [
            {"command": "/summarize", "title": "Summary", "content": "Content"},
            {"command": "/translate", "title": "Translation", "content": "Content"},
        ]
        self.manager.get_prompts = Mock(return_value=mock_prompts)

        results = self.manager.search_prompts(
            query="sum", by_command=True, by_title=False
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["command"], "/summarize")

    def test_search_prompts_by_content(self):
        """Test searching prompts by content."""
        mock_prompts = [
            {
                "command": "/test1",
                "title": "Test 1",
                "content": "This is a test prompt",
            },
            {"command": "/test2", "title": "Test 2", "content": "Another prompt"},
        ]
        self.manager.get_prompts = Mock(return_value=mock_prompts)

        results = self.manager.search_prompts(
            query="test prompt", by_content=True, by_title=False
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["command"], "/test1")

    def test_search_prompts_no_query(self):
        """Test searching prompts with no query returns all prompts."""
        mock_prompts = [
            {"command": "/test1", "title": "Test 1", "content": "Content 1"},
            {"command": "/test2", "title": "Test 2", "content": "Content 2"},
        ]
        self.manager.get_prompts = Mock(return_value=mock_prompts)

        results = self.manager.search_prompts(query=None)

        self.assertEqual(len(results), 2)

    def test_search_prompts_empty_results(self):
        """Test searching prompts with no matches."""
        mock_prompts = [
            {"command": "/test1", "title": "Test 1", "content": "Content 1"},
        ]
        self.manager.get_prompts = Mock(return_value=mock_prompts)

        results = self.manager.search_prompts(query="nonexistent")

        self.assertEqual(len(results), 0)

    def test_search_prompts_get_prompts_fails(self):
        """Test searching prompts when get_prompts fails."""
        self.manager.get_prompts = Mock(return_value=None)

        results = self.manager.search_prompts(query="test")

        self.assertEqual(results, [])

    # =============================================================================
    # Variable Extraction Tests
    # =============================================================================

    def test_extract_variables_simple(self):
        """Test extracting simple variables."""
        content = "Hello {{name}}, welcome to {{place}}!"
        variables = self.manager.extract_variables(content)

        self.assertEqual(len(variables), 2)
        self.assertIn("name", variables)
        self.assertIn("place", variables)

    def test_extract_variables_with_types(self):
        """Test extracting variables with type annotations."""
        content = "Process {{text | textarea}} and {{count | number:min=1,max=100}}"
        variables = self.manager.extract_variables(content)

        self.assertEqual(len(variables), 2)
        self.assertIn("text", variables)
        self.assertIn("count", variables)

    def test_extract_variables_duplicates(self):
        """Test extracting variables removes duplicates."""
        content = "{{name}} said hello to {{name}} again"
        variables = self.manager.extract_variables(content)

        self.assertEqual(len(variables), 1)
        self.assertIn("name", variables)

    def test_extract_variables_none(self):
        """Test extracting variables from content with no variables."""
        content = "This is plain text with no variables"
        variables = self.manager.extract_variables(content)

        self.assertEqual(len(variables), 0)

    # =============================================================================
    # Variable Substitution Tests
    # =============================================================================

    def test_substitute_variables_simple(self):
        """Test simple variable substitution."""
        content = "Hello {{name}}, you are {{age}} years old"
        variables = {"name": "Alice", "age": 30}

        result = self.manager.substitute_variables(content, variables)

        self.assertEqual(result, "Hello Alice, you are 30 years old")

    def test_substitute_variables_with_types(self):
        """Test variable substitution with type annotations."""
        content = "Text: {{text | textarea}} Count: {{count | number}}"
        variables = {"text": "Sample text", "count": 42}

        result = self.manager.substitute_variables(content, variables)

        self.assertIn("Sample text", result)
        self.assertIn("42", result)

    def test_substitute_variables_with_system_vars(self):
        """Test variable substitution with system variables."""
        content = "Today is {{CURRENT_DATE}} and user is {{name}}"
        variables = {"name": "Bob"}
        system_vars = {"CURRENT_DATE": "2025-01-10"}

        result = self.manager.substitute_variables(content, variables, system_vars)

        self.assertEqual(result, "Today is 2025-01-10 and user is Bob")

    def test_substitute_variables_missing_vars(self):
        """Test variable substitution with missing variables."""
        content = "Hello {{name}}, you are {{age}} years old"
        variables = {"name": "Alice"}  # age is missing

        result = self.manager.substitute_variables(content, variables)

        self.assertIn("Alice", result)
        self.assertIn("{{age}}", result)  # Unsubstituted variable remains

    # =============================================================================
    # System Variables Tests
    # =============================================================================

    def test_get_system_variables(self):
        """Test getting system variables."""
        system_vars = self.manager.get_system_variables()

        self.assertIn("CURRENT_DATE", system_vars)
        self.assertIn("CURRENT_DATETIME", system_vars)
        self.assertIn("CURRENT_TIME", system_vars)
        self.assertIn("CURRENT_TIMEZONE", system_vars)
        self.assertIn("CURRENT_WEEKDAY", system_vars)

    def test_get_system_variables_format(self):
        """Test system variables have correct format."""
        system_vars = self.manager.get_system_variables()

        # Check date format (YYYY-MM-DD)
        self.assertRegex(system_vars["CURRENT_DATE"], r"\d{4}-\d{2}-\d{2}")

        # Check time format (HH:MM:SS)
        self.assertRegex(system_vars["CURRENT_TIME"], r"\d{2}:\d{2}:\d{2}")

        # Check weekday is a valid day name
        valid_weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        self.assertIn(system_vars["CURRENT_WEEKDAY"], valid_weekdays)

    # =============================================================================
    # Batch Create Tests
    # =============================================================================

    def test_batch_create_prompts_success(self):
        """Test batch creating prompts successfully."""
        prompts_data = [
            {"command": "/test1", "title": "Test 1", "content": "Content 1"},
            {"command": "/test2", "title": "Test 2", "content": "Content 2"},
        ]

        self.manager.create_prompt = Mock(
            side_effect=[
                {"command": "/test1", "title": "Test 1"},
                {"command": "/test2", "title": "Test 2"},
            ]
        )

        results = self.manager.batch_create_prompts(prompts_data)

        self.assertEqual(results["total"], 2)
        self.assertEqual(len(results["success"]), 2)
        self.assertEqual(len(results["failed"]), 0)

    def test_batch_create_prompts_partial_failure(self):
        """Test batch creating prompts with some failures."""
        prompts_data = [
            {"command": "/test1", "title": "Test 1", "content": "Content 1"},
            {"command": "/test2", "title": "Test 2", "content": "Content 2"},
            {"command": "/test3", "title": "Test 3", "content": "Content 3"},
        ]

        self.manager.create_prompt = Mock(
            side_effect=[
                {"command": "/test1", "title": "Test 1"},
                None,  # Second one fails
                {"command": "/test3", "title": "Test 3"},
            ]
        )

        results = self.manager.batch_create_prompts(prompts_data)

        self.assertEqual(results["total"], 3)
        self.assertEqual(len(results["success"]), 2)
        self.assertEqual(len(results["failed"]), 1)

    def test_batch_create_prompts_missing_fields(self):
        """Test batch creating prompts with missing required fields."""
        prompts_data = [
            {"command": "/test1", "title": "Test 1"},  # Missing content
            {"command": "/test2", "title": "Test 2", "content": "Content 2"},
        ]

        self.manager.create_prompt = Mock(return_value={"command": "/test2"})

        results = self.manager.batch_create_prompts(prompts_data)

        self.assertEqual(results["total"], 2)
        self.assertEqual(len(results["success"]), 1)
        self.assertEqual(len(results["failed"]), 1)
        self.assertIn("Missing required fields", results["failed"][0]["error"])

    def test_batch_create_prompts_stop_on_error(self):
        """Test batch creating prompts stops on first error when continue_on_error=False."""
        prompts_data = [
            {"command": "/test1", "title": "Test 1", "content": "Content 1"},
            {"command": "/test2", "title": "Test 2", "content": "Content 2"},
            {"command": "/test3", "title": "Test 3", "content": "Content 3"},
        ]

        self.manager.create_prompt = Mock(
            side_effect=[
                {"command": "/test1"},
                Exception("Creation failed"),
            ]
        )

        results = self.manager.batch_create_prompts(
            prompts_data, continue_on_error=False
        )

        self.assertEqual(len(results["success"]), 1)
        self.assertEqual(len(results["failed"]), 1)
        # Third prompt should not be attempted
        self.assertEqual(self.manager.create_prompt.call_count, 2)

    def test_batch_create_prompts_with_access_control(self):
        """Test batch creating prompts with access control."""
        prompts_data = [
            {
                "command": "/test1",
                "title": "Test 1",
                "content": "Content 1",
                "access_control": {"read": ["user1"], "write": ["user1"]},
            },
        ]

        self.manager.create_prompt = Mock(return_value={"command": "/test1"})

        results = self.manager.batch_create_prompts(prompts_data)

        self.assertEqual(len(results["success"]), 1)
        # Verify access_control was passed
        call_args = self.manager.create_prompt.call_args
        self.assertIsNotNone(call_args[0][3])  # access_control argument

    # =============================================================================
    # Batch Delete Tests
    # =============================================================================

    def test_batch_delete_prompts_success(self):
        """Test batch deleting prompts successfully."""
        commands = ["/test1", "/test2", "/test3"]

        self.manager.delete_prompt_by_command = Mock(return_value=True)

        results = self.manager.batch_delete_prompts(commands)

        self.assertEqual(results["total"], 3)
        self.assertEqual(len(results["success"]), 3)
        self.assertEqual(len(results["failed"]), 0)

    def test_batch_delete_prompts_partial_failure(self):
        """Test batch deleting prompts with some failures."""
        commands = ["/test1", "/test2", "/test3"]

        self.manager.delete_prompt_by_command = Mock(side_effect=[True, False, True])

        results = self.manager.batch_delete_prompts(commands)

        self.assertEqual(results["total"], 3)
        self.assertEqual(len(results["success"]), 2)
        self.assertEqual(len(results["failed"]), 1)

    def test_batch_delete_prompts_stop_on_error(self):
        """Test batch deleting prompts stops on first error when continue_on_error=False."""
        commands = ["/test1", "/test2", "/test3"]

        self.manager.delete_prompt_by_command = Mock(
            side_effect=[
                True,
                Exception("Deletion failed"),
            ]
        )

        results = self.manager.batch_delete_prompts(commands, continue_on_error=False)

        self.assertEqual(len(results["success"]), 1)
        self.assertEqual(len(results["failed"]), 1)
        # Third prompt should not be attempted
        self.assertEqual(self.manager.delete_prompt_by_command.call_count, 2)

    def test_batch_delete_prompts_all_fail(self):
        """Test batch deleting prompts when all deletions fail."""
        commands = ["/test1", "/test2"]

        self.manager.delete_prompt_by_command = Mock(return_value=False)

        results = self.manager.batch_delete_prompts(commands)

        self.assertEqual(results["total"], 2)
        self.assertEqual(len(results["success"]), 0)
        self.assertEqual(len(results["failed"]), 2)

    # =============================================================================
    # Replace Prompt Tests
    # =============================================================================

    def test_replace_prompt_old_not_found(self):
        """Test replacing prompt when old prompt doesn't exist."""
        self.manager.get_prompt_by_command = Mock(return_value=None)

        result = self.manager.replace_prompt_by_command(
            "/old", "/new", "New Title", "New Content"
        )

        self.assertIsNone(result)

    def test_replace_prompt_new_already_exists(self):
        """Test replacing prompt when new command already exists."""
        self.manager.get_prompt_by_command = Mock(
            side_effect=[
                {"command": "/old", "title": "Old", "content": "Old content"},
                {"command": "/new", "title": "Existing", "content": "Existing content"},
            ]
        )

        result = self.manager.replace_prompt_by_command(
            "/old", "/new", "New Title", "New Content"
        )

        self.assertIsNone(result)

    def test_replace_prompt_delete_fails(self):
        """Test replacing prompt when deletion fails."""
        self.manager.get_prompt_by_command = Mock(
            return_value={"command": "/old", "title": "Old", "content": "Old content"}
        )
        self.manager.delete_prompt_by_command = Mock(return_value=False)

        result = self.manager.replace_prompt_by_command(
            "/old", "/new", "New Title", "New Content"
        )

        self.assertIsNone(result)

    def test_replace_prompt_create_fails_with_restore(self):
        """Test replacing prompt when creation fails and restoration succeeds."""
        old_prompt = {
            "command": "/old",
            "title": "Old Title",
            "content": "Old Content",
            "access_control": {"read": ["user1"]},
        }

        # First call returns old prompt, second call returns None (new doesn't exist)
        self.manager.get_prompt_by_command = Mock(side_effect=[old_prompt, None])
        self.manager.delete_prompt_by_command = Mock(return_value=True)
        self.manager.create_prompt = Mock(
            side_effect=[
                None,  # New prompt creation fails
                {"command": "/old", "title": "Old Title"},  # Restoration succeeds
            ]
        )

        result = self.manager.replace_prompt_by_command(
            "/old", "/new", "New Title", "New Content"
        )

        self.assertIsNone(result)
        # Verify restoration was attempted
        self.assertEqual(self.manager.create_prompt.call_count, 2)

    def test_replace_prompt_create_fails_restore_fails(self):
        """Test replacing prompt when both creation and restoration fail."""
        old_prompt = {"command": "/old", "title": "Old", "content": "Old content"}

        # First call returns old prompt, second call returns None (new doesn't exist)
        self.manager.get_prompt_by_command = Mock(side_effect=[old_prompt, None])
        self.manager.delete_prompt_by_command = Mock(return_value=True)
        self.manager.create_prompt = Mock(return_value=None)  # Both fail

        result = self.manager.replace_prompt_by_command(
            "/old", "/new", "New Title", "New Content"
        )

        self.assertIsNone(result)
        # Verify both creation and restoration were attempted
        self.assertEqual(self.manager.create_prompt.call_count, 2)


if __name__ == "__main__":
    unittest.main()
