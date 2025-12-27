#!/usr/bin/env python3
"""
Regression tests to ensure duplicate method definitions remain consolidated.
"""

import ast
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestDuplicateDefinitions(unittest.TestCase):
    """Validate key classes only define single copies of important helpers."""

    def _get_method_counts(self, file_path: Path, class_name: str) -> dict:
        """Return a mapping of method names to definition counts for a class."""
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception as exc:  # pragma: no cover - defensive error reporting
            self.fail(f"Failed to load/parse {file_path}: {exc}")
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                counts = {}
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        counts[item.name] = counts.get(item.name, 0) + 1
                return counts
        self.fail(f"Class {class_name} not found in {file_path}")

    def test_chat_manager_methods_are_unique(self):
        """ChatManager should not have duplicate helper definitions."""
        file_path = PROJECT_ROOT / "openwebui_chat_client" / "modules" / "chat_manager.py"
        counts = self._get_method_counts(file_path, "ChatManager")
        for method in ("rename_chat", "get_folder_id_by_name", "move_chat_to_folder"):
            self.assertEqual(
                counts.get(method, 0),
                1,
                f"Expected single definition for {method} in ChatManager",
            )

    def test_client_methods_are_unique(self):
        """OpenWebUIClient should keep one implementation for critical helpers."""
        file_path = PROJECT_ROOT / "openwebui_chat_client" / "openwebui_chat_client.py"
        counts = self._get_method_counts(file_path, "OpenWebUIClient")
        for method in (
            "_upload_file",
            "_cleanup_unused_placeholder_messages",
            "_handle_rag_references",
        ):
            self.assertEqual(
                counts.get(method, 0),
                1,
                f"Expected single definition for {method} in OpenWebUIClient",
            )


if __name__ == "__main__":
    unittest.main()
