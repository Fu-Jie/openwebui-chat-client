#!/usr/bin/env python3
"""
Selective Integration Test Detector

This script analyzes changed files in a Git repository and determines which
integration tests should be run based on the file mappings defined in test-mapping.yml.

Usage:
    python .github/scripts/detect_required_tests.py [base_ref] [head_ref]
    
    base_ref: Base Git reference to compare against (default: origin/main)
    head_ref: Head Git reference to compare (default: HEAD)

Output:
    JSON array of test categories that should be executed, written to stdout.
    
Environment Variables:
    GITHUB_BASE_REF: Base reference for comparison (used in GitHub Actions)
    GITHUB_HEAD_REF: Head reference for comparison (used in GitHub Actions)
"""

import os
import sys
import json
import subprocess
import fnmatch
import yaml
from pathlib import Path
from typing import List, Dict, Set, Any


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


def match_file_patterns(filepath: str, patterns: List[Dict[str, Any]]) -> Set[str]:
    """Match a file path against patterns and return associated test categories."""
    categories = set()
    
    for mapping in patterns:
        pattern = mapping['pattern']
        
        # Convert glob pattern to work with filepath
        if fnmatch.fnmatch(filepath, pattern):
            categories.update(mapping['categories'])
    
    return categories


def determine_required_tests(changed_files: List[str], config: Dict[str, Any]) -> List[str]:
    """Determine which integration tests are required based on changed files."""
    required_categories = set()
    
    file_mappings = config.get('file_mappings', [])
    default_categories = config.get('default_categories', [])
    
    # If no files changed, run default tests
    if not changed_files:
        print("No changed files detected, using default test categories", file=sys.stderr)
        return default_categories
    
    # Check each changed file against patterns
    for filepath in changed_files:
        print(f"Checking file: {filepath}", file=sys.stderr)
        matched_categories = match_file_patterns(filepath, file_mappings)
        
        if matched_categories:
            print(f"  -> Matched categories: {sorted(matched_categories)}", file=sys.stderr)
            required_categories.update(matched_categories)
        else:
            print(f"  -> No specific patterns matched", file=sys.stderr)
    
    # If no specific patterns matched, use default categories
    if not required_categories:
        print("No specific patterns matched any files, using default categories", file=sys.stderr)
        required_categories.update(default_categories)
    
    return sorted(list(required_categories))


def main():
    """Main function to detect and output required integration tests."""
    # Parse command line arguments
    base_ref = sys.argv[1] if len(sys.argv) > 1 else os.getenv('GITHUB_BASE_REF', 'origin/main')
    head_ref = sys.argv[2] if len(sys.argv) > 2 else os.getenv('GITHUB_HEAD_REF', 'HEAD')
    
    # Handle GitHub Actions environment
    if os.getenv('GITHUB_ACTIONS') == 'true':
        event_name = os.getenv('GITHUB_EVENT_NAME')
        
        if event_name == 'workflow_run':
            # For workflow_run events, we need to use the commit SHA from the original workflow
            workflow_run_sha = os.getenv('WORKFLOW_RUN_HEAD_SHA')
            if workflow_run_sha:
                print(f"Using workflow_run context: SHA {workflow_run_sha}", file=sys.stderr)
                head_ref = workflow_run_sha
                # Compare with the parent commit of the workflow run
                base_ref = f"{workflow_run_sha}~1"
            else:
                print("Warning: No WORKFLOW_RUN_HEAD_SHA found, falling back to HEAD~1", file=sys.stderr)
                base_ref = 'HEAD~1'
                head_ref = 'HEAD'
        elif event_name == 'pull_request':
            base_ref = f"origin/{os.getenv('GITHUB_BASE_REF', 'main')}"
            head_ref = os.getenv('GITHUB_SHA', 'HEAD')
        else:
            # For push events, compare with previous commit
            base_ref = 'HEAD~1'
            head_ref = 'HEAD'
    
    print(f"Comparing {base_ref}...{head_ref}", file=sys.stderr)
    
    # Get changed files
    changed_files = get_changed_files(base_ref, head_ref)
    print(f"Changed files ({len(changed_files)}): {changed_files}", file=sys.stderr)
    
    # Load test mapping configuration
    script_dir = Path(__file__).parent
    config_file = script_dir.parent / 'test-mapping.yml'
    config = load_test_mapping(str(config_file))
    
    # Determine required tests
    required_tests = determine_required_tests(changed_files, config)
    print(f"Required test categories: {required_tests}", file=sys.stderr)
    
    # Output as JSON for consumption by GitHub Actions
    print(json.dumps(required_tests))


if __name__ == '__main__':
    main()