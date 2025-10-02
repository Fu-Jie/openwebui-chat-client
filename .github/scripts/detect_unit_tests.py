#!/usr/bin/env python3
"""
Unit Test Scope Detector

This script analyzes changed files and determines which unit tests should be run.
It creates a mapping between source code files and their corresponding test files.

Usage:
    python .github/scripts/detect_unit_tests.py [base_ref] [head_ref]
    
Output:
    JSON file at /tmp/test-detection.json with structure:
    {
        "should_run": true/false,
        "patterns": "test_*.py" or specific pattern
    }
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Set, Dict

# Mapping of source files to their test files
# Format: source_pattern -> test_file_name (without test_ prefix and .py suffix)
SOURCE_TO_TEST_MAPPING = {
    # Core client files
    "openwebui_chat_client/openwebui_chat_client.py": ["openwebui_chat_client"],
    "openwebui_chat_client/core/base_client.py": ["openwebui_chat_client", "core/base_client_retry"],
    
    # Module-specific mappings
    "openwebui_chat_client/modules/chat_manager.py": ["chat_functionality", "continuous_conversation"],
    "openwebui_chat_client/modules/model_manager.py": ["openwebui_chat_client", "model_permissions"],
    "openwebui_chat_client/modules/notes_manager.py": ["notes_functionality"],
    "openwebui_chat_client/modules/prompts_manager.py": ["prompts_functionality"],
    "openwebui_chat_client/modules/knowledge_base_manager.py": ["knowledge_base"],
    "openwebui_chat_client/modules/file_manager.py": ["openwebui_chat_client"],
    
    # Feature-specific test mappings
    "**/archive*.py": ["archive_functionality"],
    "**/continuous*.py": ["continuous_conversation"],
    "**/deep_research*.py": ["deep_research"],
    "**/follow_up*.py": ["follow_up_feature"],
    "**/metadata*.py": ["metadata_features"],
}

# Files that should trigger all tests
TRIGGER_ALL_TESTS = [
    "setup.py",
    "pyproject.toml",
    "openwebui_chat_client/__init__.py",
    ".github/workflows/test.yml",
]

# Files that don't require any tests
SKIP_TEST_PATTERNS = [
    "*.md",
    "*.txt",
    "*.rst",
    "docs/**",
    "examples/**",
    ".github/**/*.md",
    "CHANGELOG*",
    "LICENSE",
    ".gitignore",
]


def get_changed_files(base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> List[str]:
    """Get list of changed files between two Git references."""
    try:
        cmd = ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        
        if not files:
            cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            
        return files
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to get changed files: {e}", file=sys.stderr)
        return []


def should_skip_tests(filepath: str) -> bool:
    """Check if a file should skip tests entirely."""
    from fnmatch import fnmatch
    
    for pattern in SKIP_TEST_PATTERNS:
        if fnmatch(filepath, pattern):
            return True
    return False


def should_run_all_tests(filepath: str) -> bool:
    """Check if a file change should trigger all tests."""
    return filepath in TRIGGER_ALL_TESTS


def map_source_to_tests(filepath: str) -> Set[str]:
    """Map a source file to its corresponding test files."""
    from fnmatch import fnmatch
    
    test_files = set()
    
    # Check direct mappings
    for pattern, tests in SOURCE_TO_TEST_MAPPING.items():
        if fnmatch(filepath, pattern) or filepath == pattern:
            test_files.update(tests)
    
    # If it's already a test file, include it
    if filepath.startswith("tests/") and filepath.endswith(".py"):
        # Extract test name without test_ prefix and .py suffix
        test_name = Path(filepath).stem
        if test_name.startswith("test_"):
            test_name = test_name[5:]
        test_files.add(test_name)
    
    return test_files


def determine_test_scope(changed_files: List[str]) -> Dict[str, any]:
    """Determine which tests should be run based on changed files."""
    if not changed_files:
        return {"should_run": False, "patterns": "test_*.py"}
    
    print(f"Analyzing {len(changed_files)} changed files...", file=sys.stderr)
    
    # Check if any file triggers all tests
    for filepath in changed_files:
        if should_run_all_tests(filepath):
            print(f"  {filepath} -> triggers ALL tests", file=sys.stderr)
            return {"should_run": True, "patterns": "test_*.py"}
    
    # Collect required test files
    required_tests = set()
    has_non_skippable_changes = False
    
    for filepath in changed_files:
        if should_skip_tests(filepath):
            print(f"  {filepath} -> skip (documentation/config only)", file=sys.stderr)
            continue
        
        has_non_skippable_changes = True
        tests = map_source_to_tests(filepath)
        
        if tests:
            print(f"  {filepath} -> tests: {', '.join(tests)}", file=sys.stderr)
            required_tests.update(tests)
        else:
            print(f"  {filepath} -> no specific test mapping (will run connectivity test)", file=sys.stderr)
            required_tests.add("openwebui_chat_client")  # Default fallback
    
    # If no code changes, don't run tests
    if not has_non_skippable_changes:
        print("No code changes detected, skipping tests", file=sys.stderr)
        return {"should_run": False, "patterns": "test_*.py"}
    
    # If no specific tests identified, run core tests
    if not required_tests:
        print("No specific tests identified, running core tests", file=sys.stderr)
        return {"should_run": True, "patterns": "test_openwebui_chat_client.py"}
    
    # Build pattern for unittest discover
    # Convert test names to patterns: ["notes", "prompts"] -> "test_{notes,prompts}*.py"
    if len(required_tests) == 1:
        pattern = f"test_{list(required_tests)[0]}*.py"
    else:
        test_list = ",".join(sorted(required_tests))
        pattern = f"test_{{{test_list}}}*.py"
    
    print(f"Final test pattern: {pattern}", file=sys.stderr)
    print(f"Required tests: {sorted(required_tests)}", file=sys.stderr)
    
    return {"should_run": True, "patterns": pattern}


def main():
    """Main function to detect and output required unit tests."""
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1"
    head_ref = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    
    print(f"Detecting unit test scope for {base_ref}...{head_ref}", file=sys.stderr)
    
    changed_files = get_changed_files(base_ref, head_ref)
    print(f"Changed files: {changed_files}", file=sys.stderr)
    
    result = determine_test_scope(changed_files)
    
    # Write output to file for GitHub Actions to consume
    output_file = "/tmp/test-detection.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nTest detection result:", file=sys.stderr)
    print(f"  Should run: {result['should_run']}", file=sys.stderr)
    print(f"  Patterns: {result['patterns']}", file=sys.stderr)


if __name__ == '__main__':
    main()
