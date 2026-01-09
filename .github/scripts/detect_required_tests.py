#!/usr/bin/env python3
"""
Selective Integration Test Detector (Enhanced Version)

This script analyzes changed files in a Git repository and determines which
integration tests should be run based on the file mappings defined in test-mapping.yml.

Features:
- Precise file-to-test mapping with priority-based matching
- Exact path matching before wildcard patterns
- Detailed logging for debugging
- Support for multiple Git event types

Usage:
    python .github/scripts/detect_required_tests.py [base_ref] [head_ref]
    
    base_ref: Base Git reference to compare against (default: origin/main)
    head_ref: Head Git reference to compare (default: HEAD)

Output:
    JSON array of test categories that should be executed, written to stdout.
    
Environment Variables:
    GITHUB_BASE_REF: Base reference for comparison (used in GitHub Actions)
    GITHUB_HEAD_REF: Head reference for comparison (used in GitHub Actions)
    VERBOSE: Set to '1' or 'true' for detailed logging
"""

import os
import sys
import json
import subprocess
import fnmatch
import yaml
from pathlib import Path
from typing import List, Dict, Set, Any, Tuple

# File patterns that are considered documentation-only and should skip tests
DOCUMENTATION_PATTERNS = [
    'docs/**',
    '*.md',
    'mkdocs.yml',
    '.github/workflows/deploy.yml',
    'LICENSE',
    '.gitignore',
    '**/__pycache__/**',
    '**/*.pyc',
    '**/.env',
    '**/.vscode/**',
]

# Enable verbose logging
VERBOSE = os.getenv('VERBOSE', '').lower() in ('1', 'true', 'yes')


def log_verbose(message: str) -> None:
    """Log verbose messages to stderr if VERBOSE is enabled."""
    if VERBOSE:
        print(f"[VERBOSE] {message}", file=sys.stderr)


def is_documentation_file(filepath: str) -> bool:
    """Check if a file is a documentation file that should skip tests."""
    for pattern in DOCUMENTATION_PATTERNS:
        if fnmatch.fnmatch(filepath, pattern):
            return True
    return False


def get_changed_files(base_ref: str = "origin/main", head_ref: str = "HEAD") -> List[str]:
    """Get list of changed files between two Git references."""
    try:
        # First, try to get changed files from git diff
        cmd = ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        
        if not files:
            # If no diff, try comparing with HEAD~1 for single commits
            cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            
        return files
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to get changed files: {e}", file=sys.stderr)
        print(f"Command: {' '.join(cmd)}", file=sys.stderr)
        return []


def load_test_mapping(config_file: str) -> Dict[str, Any]:
    """Load test mapping configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error: Failed to load test mapping from {config_file}: {e}", file=sys.stderr)
        sys.exit(1)


def match_file_patterns(filepath: str, patterns: List[Dict[str, Any]]) -> Tuple[Set[str], List[str]]:
    """
    Match a file path against patterns and return associated test categories.
    
    Returns:
        Tuple of (categories, matched_patterns) where:
        - categories: Set of test category names
        - matched_patterns: List of pattern strings that matched
    
    Matching Strategy:
    1. Try exact path match first (no wildcards)
    2. Then try patterns with wildcards
    3. Collect all matching categories (not just first match)
    """
    categories = set()
    matched_patterns = []
    
    # Separate exact patterns from wildcard patterns
    exact_patterns = []
    wildcard_patterns = []
    
    for mapping in patterns:
        pattern = mapping['pattern']
        if '*' in pattern or '?' in pattern:
            wildcard_patterns.append(mapping)
        else:
            exact_patterns.append(mapping)
    
    # First, try exact matches (highest priority)
    for mapping in exact_patterns:
        pattern = mapping['pattern']
        if filepath == pattern:
            log_verbose(f"  ✓ Exact match: {pattern}")
            categories.update(mapping['categories'])
            matched_patterns.append(pattern)
            description = mapping.get('description', '')
            if description:
                log_verbose(f"    → {description}")
    
    # If exact match found, return immediately (exact matches are definitive)
    if matched_patterns:
        return categories, matched_patterns
    
    # Then try wildcard patterns
    for mapping in wildcard_patterns:
        pattern = mapping['pattern']
        if fnmatch.fnmatch(filepath, pattern):
            log_verbose(f"  ✓ Pattern match: {pattern}")
            categories.update(mapping['categories'])
            matched_patterns.append(pattern)
            description = mapping.get('description', '')
            if description:
                log_verbose(f"    → {description}")
    
    return categories, matched_patterns


def determine_required_tests(changed_files: List[str], config: Dict[str, Any]) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Determine which integration tests are required based on changed files.
    
    Returns:
        Tuple of (test_categories, file_to_tests_map) where:
        - test_categories: Sorted list of unique test category names
        - file_to_tests_map: Dict mapping each file to its triggered tests
    """
    required_categories = set()
    file_to_tests_map = {}
    
    file_mappings = config.get('file_mappings', [])
    default_categories = config.get('default_categories', [])
    
    # If no files changed, run default tests
    if not changed_files:
        print("No changed files detected, using default test categories", file=sys.stderr)
        return default_categories, {}
    
    # Filter out documentation files
    non_doc_files = [f for f in changed_files if not is_documentation_file(f)]
    
    # Check if all changed files are documentation-only
    if not non_doc_files:
        print("All changed files are documentation-only, skipping integration tests", file=sys.stderr)
        return [], {}
    
    print(f"\n📋 Analyzing {len(non_doc_files)} non-documentation files:", file=sys.stderr)
    
    # Check each non-documentation file against patterns
    files_with_no_match = []
    
    for filepath in non_doc_files:
        print(f"\n🔍 Checking: {filepath}", file=sys.stderr)
        
        matched_categories, matched_patterns = match_file_patterns(filepath, file_mappings)
        
        if matched_categories:
            print(f"  ✅ Triggered {len(matched_categories)} test(s): {sorted(matched_categories)}", file=sys.stderr)
            required_categories.update(matched_categories)
            file_to_tests_map[filepath] = sorted(list(matched_categories))
        else:
            print(f"  ⚠️  No specific patterns matched", file=sys.stderr)
            files_with_no_match.append(filepath)
    
    # If some files had no specific patterns, use default categories
    if files_with_no_match:
        print(f"\n⚠️  {len(files_with_no_match)} file(s) had no specific test mapping:", file=sys.stderr)
        for f in files_with_no_match:
            print(f"  - {f}", file=sys.stderr)
        print(f"\n→ Adding default test categories: {default_categories}", file=sys.stderr)
        required_categories.update(default_categories)
        for f in files_with_no_match:
            file_to_tests_map[f] = default_categories
    
    # Summary
    print(f"\n" + "="*80, file=sys.stderr)
    print(f"📊 SUMMARY", file=sys.stderr)
    print(f"="*80, file=sys.stderr)
    print(f"Changed files analyzed: {len(non_doc_files)}", file=sys.stderr)
    print(f"Files with specific mappings: {len(non_doc_files) - len(files_with_no_match)}", file=sys.stderr)
    print(f"Files using default mappings: {len(files_with_no_match)}", file=sys.stderr)
    print(f"Total unique test categories: {len(required_categories)}", file=sys.stderr)
    print(f"\n🎯 Tests to run: {sorted(required_categories)}", file=sys.stderr)
    print("="*80 + "\n", file=sys.stderr)
    
    return sorted(list(required_categories)), file_to_tests_map


def main():
    """Main function to detect and output required integration tests."""
    # Parse command line arguments
    base_ref = sys.argv[1] if len(sys.argv) > 1 else os.getenv('GITHUB_BASE_REF', 'origin/main')
    head_ref = sys.argv[2] if len(sys.argv) > 2 else os.getenv('GITHUB_HEAD_REF', 'HEAD')
    
    # Handle GitHub Actions environment
    if os.getenv('GITHUB_ACTIONS') == 'true':
        event_name = os.getenv('GITHUB_EVENT_NAME')
        
        print(f"🔧 GitHub Actions Environment Detected", file=sys.stderr)
        print(f"   Event: {event_name}", file=sys.stderr)
        
        if event_name == 'workflow_run':
            # For workflow_run events, we need to use the commit SHA from the original workflow
            workflow_run_sha = os.getenv('WORKFLOW_RUN_HEAD_SHA')
            if workflow_run_sha:
                print(f"   Using workflow_run SHA: {workflow_run_sha}", file=sys.stderr)
                head_ref = workflow_run_sha
                # Compare with the parent commit of the workflow run
                base_ref = f"{workflow_run_sha}~1"
            else:
                print("   Warning: No WORKFLOW_RUN_HEAD_SHA found, falling back to HEAD~1", file=sys.stderr)
                base_ref = 'HEAD~1'
                head_ref = 'HEAD'
        elif event_name == 'pull_request':
            base_ref = f"origin/{os.getenv('GITHUB_BASE_REF', 'main')}"
            head_ref = os.getenv('GITHUB_SHA', 'HEAD')
            print(f"   PR: {base_ref}...{head_ref}", file=sys.stderr)
        else:
            # For push events, compare with previous commit
            base_ref = 'HEAD~1'
            head_ref = 'HEAD'
            print(f"   Push: {base_ref}...{head_ref}", file=sys.stderr)
    
    print(f"\n🔍 Comparing: {base_ref}...{head_ref}\n", file=sys.stderr)
    
    # Get changed files
    changed_files = get_changed_files(base_ref, head_ref)
    
    if changed_files:
        print(f"📝 Found {len(changed_files)} changed file(s):", file=sys.stderr)
        for f in changed_files:
            print(f"   - {f}", file=sys.stderr)
    else:
        print("📝 No changed files detected", file=sys.stderr)
    
    # Load test mapping configuration
    script_dir = Path(__file__).parent
    config_file = script_dir.parent / 'test-mapping.yml'
    
    print(f"\n📖 Loading test mapping from: {config_file}", file=sys.stderr)
    config = load_test_mapping(str(config_file))
    
    print(f"   Found {len(config.get('test_categories', {}))} test categories", file=sys.stderr)
    print(f"   Found {len(config.get('file_mappings', []))} file mapping rules", file=sys.stderr)
    
    # Determine required tests
    required_tests, file_to_tests_map = determine_required_tests(changed_files, config)
    
    # Output detailed mapping if verbose
    if VERBOSE and file_to_tests_map:
        print("\n📋 Detailed File-to-Test Mapping:", file=sys.stderr)
        for filepath, tests in sorted(file_to_tests_map.items()):
            print(f"   {filepath}", file=sys.stderr)
            for test in tests:
                print(f"      → {test}", file=sys.stderr)
    
    # Output as JSON for consumption by GitHub Actions
    print(json.dumps(required_tests))


if __name__ == '__main__':
    main()