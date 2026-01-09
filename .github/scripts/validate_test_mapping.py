#!/usr/bin/env python3
"""
Test Mapping Validator

This script validates the test-mapping.yml configuration file and helps
developers understand which tests will be triggered by specific file changes.

Usage:
    # Validate the configuration file
    python .github/scripts/validate_test_mapping.py
    
    # Test specific file patterns
    python .github/scripts/validate_test_mapping.py --test-file "openwebui_chat_client/modules/chat_manager.py"
    
    # Test multiple files
    python .github/scripts/validate_test_mapping.py --test-files "file1.py,file2.py,file3.py"
    
    # Show all mappings
    python .github/scripts/validate_test_mapping.py --show-all
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any
import fnmatch


def load_test_mapping(config_file: str) -> Dict[str, Any]:
    """Load test mapping configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error: Failed to load test mapping from {config_file}: {e}")
        sys.exit(1)


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate the configuration structure and content."""
    errors = []
    warnings = []
    
    # Check required sections
    if 'test_categories' not in config:
        errors.append("Missing 'test_categories' section")
    if 'file_mappings' not in config:
        errors.append("Missing 'file_mappings' section")
    
    if errors:
        for error in errors:
            print(f"❌ {error}")
        return False
    
    # Validate test categories
    test_categories = config.get('test_categories', {})
    print(f"\n✅ Found {len(test_categories)} test categories:")
    for name, details in test_categories.items():
        if 'command' not in details:
            errors.append(f"Test category '{name}' missing 'command'")
        print(f"   - {name}: {details.get('description', 'No description')}")
    
    # Validate file mappings
    file_mappings = config.get('file_mappings', [])
    print(f"\n✅ Found {len(file_mappings)} file mapping rules")
    
    # Check for undefined test categories in mappings
    defined_categories = set(test_categories.keys())
    
    for i, mapping in enumerate(file_mappings):
        if 'pattern' not in mapping:
            errors.append(f"Mapping #{i+1} missing 'pattern'")
            continue
        if 'categories' not in mapping:
            errors.append(f"Mapping #{i+1} (pattern: {mapping['pattern']}) missing 'categories'")
            continue
        
        # Check if all referenced categories are defined
        for category in mapping['categories']:
            if category not in defined_categories:
                errors.append(f"Mapping '{mapping['pattern']}' references undefined category '{category}'")
    
    # Check for duplicate patterns
    patterns = [m['pattern'] for m in file_mappings if 'pattern' in m]
    duplicate_patterns = [p for p in patterns if patterns.count(p) > 1]
    if duplicate_patterns:
        for pattern in set(duplicate_patterns):
            warnings.append(f"Duplicate pattern: '{pattern}' (appears {patterns.count(pattern)} times)")
    
    # Print warnings
    if warnings:
        print(f"\n⚠️  Warnings:")
        for warning in warnings:
            print(f"   {warning}")
    
    # Print errors
    if errors:
        print(f"\n❌ Errors:")
        for error in errors:
            print(f"   {error}")
        return False
    
    print(f"\n✅ Configuration is valid!")
    return True


def match_file_to_tests(filepath: str, config: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Match a file to test categories and return detailed results.
    
    Returns:
        Dict with 'exact_matches', 'wildcard_matches', and 'all_categories'
    """
    file_mappings = config.get('file_mappings', [])
    
    exact_matches = []
    wildcard_matches = []
    all_categories = set()
    
    for mapping in file_mappings:
        pattern = mapping['pattern']
        categories = mapping['categories']
        
        # Check for exact match
        if filepath == pattern:
            exact_matches.append({
                'pattern': pattern,
                'categories': categories,
                'description': mapping.get('description', '')
            })
            all_categories.update(categories)
        # Check for wildcard match
        elif ('*' in pattern or '?' in pattern) and fnmatch.fnmatch(filepath, pattern):
            wildcard_matches.append({
                'pattern': pattern,
                'categories': categories,
                'description': mapping.get('description', '')
            })
            all_categories.update(categories)
    
    return {
        'exact_matches': exact_matches,
        'wildcard_matches': wildcard_matches,
        'all_categories': sorted(list(all_categories))
    }


def test_file_patterns(files: List[str], config: Dict[str, Any]) -> None:
    """Test which tests would be triggered by specific file changes."""
    print(f"\n{'='*80}")
    print(f"🧪 Testing File Patterns")
    print(f"{'='*80}\n")
    
    for filepath in files:
        print(f"📄 File: {filepath}")
        print(f"   {'-'*76}")
        
        results = match_file_to_tests(filepath, config)
        
        if results['exact_matches']:
            print(f"   ✅ Exact Matches ({len(results['exact_matches'])}):")
            for match in results['exact_matches']:
                print(f"      Pattern: {match['pattern']}")
                if match['description']:
                    print(f"      Description: {match['description']}")
                print(f"      Tests: {', '.join(match['categories'])}")
                print()
        
        if results['wildcard_matches']:
            print(f"   🔍 Wildcard Matches ({len(results['wildcard_matches'])}):")
            for match in results['wildcard_matches']:
                print(f"      Pattern: {match['pattern']}")
                if match['description']:
                    print(f"      Description: {match['description']}")
                print(f"      Tests: {', '.join(match['categories'])}")
                print()
        
        if results['all_categories']:
            print(f"   🎯 Total Tests Triggered: {len(results['all_categories'])}")
            print(f"      {', '.join(results['all_categories'])}")
        else:
            print(f"   ⚠️  No tests matched (would use default categories)")
        
        print()


def show_all_mappings(config: Dict[str, Any]) -> None:
    """Display all file mappings in a readable format."""
    file_mappings = config.get('file_mappings', [])
    
    print(f"\n{'='*80}")
    print(f"📋 All File Mappings ({len(file_mappings)} rules)")
    print(f"{'='*80}\n")
    
    # Group by pattern type
    exact_patterns = []
    wildcard_patterns = []
    
    for mapping in file_mappings:
        pattern = mapping['pattern']
        if '*' in pattern or '?' in pattern:
            wildcard_patterns.append(mapping)
        else:
            exact_patterns.append(mapping)
    
    print(f"📌 Exact Patterns ({len(exact_patterns)}):")
    print(f"   {'-'*76}")
    for mapping in exact_patterns:
        print(f"   {mapping['pattern']}")
        if mapping.get('description'):
            print(f"      → {mapping['description']}")
        print(f"      Tests: {', '.join(mapping['categories'])}")
        print()
    
    print(f"\n🔍 Wildcard Patterns ({len(wildcard_patterns)}):")
    print(f"   {'-'*76}")
    for mapping in wildcard_patterns:
        print(f"   {mapping['pattern']}")
        if mapping.get('description'):
            print(f"      → {mapping['description']}")
        print(f"      Tests: {', '.join(mapping['categories'])}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Validate and test the test-mapping.yml configuration'
    )
    parser.add_argument(
        '--test-file',
        help='Test a specific file path to see which tests it would trigger'
    )
    parser.add_argument(
        '--test-files',
        help='Test multiple file paths (comma-separated)'
    )
    parser.add_argument(
        '--show-all',
        action='store_true',
        help='Show all file mappings'
    )
    parser.add_argument(
        '--config',
        default='.github/test-mapping.yml',
        help='Path to test-mapping.yml (default: .github/test-mapping.yml)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config_file = Path(args.config)
    if not config_file.exists():
        print(f"❌ Error: Configuration file not found: {config_file}")
        sys.exit(1)
    
    print(f"📖 Loading configuration from: {config_file}")
    config = load_test_mapping(str(config_file))
    
    # Validate configuration
    if not validate_config(config):
        sys.exit(1)
    
    # Test specific files
    if args.test_file:
        test_file_patterns([args.test_file], config)
    elif args.test_files:
        files = [f.strip() for f in args.test_files.split(',')]
        test_file_patterns(files, config)
    
    # Show all mappings
    if args.show_all:
        show_all_mappings(config)
    
    # If no specific action, just validate
    if not (args.test_file or args.test_files or args.show_all):
        print("\n💡 Tip: Use --test-file to test specific file patterns")
        print("   Example: python validate_test_mapping.py --test-file 'openwebui_chat_client/modules/chat_manager.py'")


if __name__ == '__main__':
    main()
