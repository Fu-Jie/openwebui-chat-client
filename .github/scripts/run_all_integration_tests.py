#!/usr/bin/env python3
"""
Comprehensive Integration Test Runner

This script runs all integration tests for manual execution by users.
It provides the same comprehensive testing that was previously done automatically
in GitHub Actions, but can be run locally or manually triggered.

Usage:
    python .github/scripts/run_all_integration_tests.py [--verbose] [--category CATEGORY]
    
Options:
    --verbose: Enable verbose output with detailed logging
    --category: Run only a specific test category (optional)
    --list-categories: List all available test categories
    
Environment Variables:
    All the standard OpenWebUI environment variables are required:
    - OUI_BASE_URL: Your OpenWebUI instance URL
    - OUI_AUTH_TOKEN: Your authentication token
    - OUI_DEFAULT_MODEL: Default model ID
    - OUI_PARALLEL_MODELS: Comma-separated model list (optional)
    - OUI_MULTIMODAL_MODEL: Multimodal model ID (optional)
    - OUI_RAG_MODEL: RAG-optimized model ID (optional)
"""

import os
import sys
import json
import subprocess
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_test_mapping(config_file: str) -> Dict[str, Any]:
    """Load test mapping configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error: Failed to load test mapping from {config_file}: {e}")
        sys.exit(1)


def check_environment_variables() -> bool:
    """Check if required environment variables are set."""
    required_vars = ['OUI_BASE_URL', 'OUI_AUTH_TOKEN', 'OUI_DEFAULT_MODEL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please set these environment variables before running integration tests:")
        print("export OUI_BASE_URL='https://your-openwebui-instance.com'")
        print("export OUI_AUTH_TOKEN='your-auth-token'")
        print("export OUI_DEFAULT_MODEL='your-model-id'")
        print()
        print("Optional variables:")
        print("export OUI_PARALLEL_MODELS='model1,model2'")
        print("export OUI_MULTIMODAL_MODEL='multimodal-model-id'")
        print("export OUI_RAG_MODEL='rag-optimized-model-id'")
        return False
    
    print("✅ Environment variables detected:")
    print(f"   Base URL: {os.getenv('OUI_BASE_URL')}")
    print(f"   Auth Token: {'***' + os.getenv('OUI_AUTH_TOKEN', '')[-4:] if os.getenv('OUI_AUTH_TOKEN') else 'not set'}")
    print(f"   Default Model: {os.getenv('OUI_DEFAULT_MODEL')}")
    
    optional_vars = ['OUI_PARALLEL_MODELS', 'OUI_MULTIMODAL_MODEL', 'OUI_RAG_MODEL']
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   {var}: {value}")
    
    return True


def run_integration_test(category: str, test_config: Dict[str, Any], verbose: bool = False) -> bool:
    """Run a single integration test category."""
    name = test_config['name']
    command = test_config['command']
    description = test_config['description']
    
    print(f"\n🧪 Running {name}...")
    if verbose:
        print(f"   Description: {description}")
        print(f"   Command: {command}")
    
    try:
        # Change to repository root directory
        repo_root = Path(__file__).parent.parent.parent
        
        # Run the test command
        env = os.environ.copy()
        # Set additional environment variables for comprehensive testing
        env.update({
            'OUI_MULTIMODAL_MODEL': env.get('OUI_MULTIMODAL_MODEL', env.get('OUI_DEFAULT_MODEL', '')),
            'OUI_RAG_MODEL': env.get('OUI_RAG_MODEL', env.get('OUI_DEFAULT_MODEL', ''))
        })
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=repo_root,
            env=env,
            capture_output=not verbose,
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        
        if result.returncode == 0:
            print(f"   ✅ {name} passed")
            if verbose and result.stdout:
                print("   Output:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        print(f"      {line}")
            return True
        else:
            print(f"   ❌ {name} failed (exit code: {result.returncode})")
            if result.stderr:
                print("   Error output:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"      {line}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ {name} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"   ❌ {name} failed with exception: {e}")
        return False


def list_categories(config: Dict[str, Any]) -> None:
    """List all available test categories."""
    print("📋 Available integration test categories:")
    print()
    
    test_categories = config.get('test_categories', {})
    for category, details in test_categories.items():
        print(f"  {category}:")
        print(f"    Name: {details['name']}")
        print(f"    Description: {details['description']}")
        print(f"    Command: {details['command']}")
        print()


def main():
    """Main function to run integration tests."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive integration tests for OpenWebUI Chat Client"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--category', '-c',
        type=str,
        help='Run only a specific test category'
    )
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List all available test categories'
    )
    
    args = parser.parse_args()
    
    # Load test configuration
    script_dir = Path(__file__).parent
    config_file = script_dir.parent / 'test-mapping.yml'
    config = load_test_mapping(str(config_file))
    
    # Handle list categories request
    if args.list_categories:
        list_categories(config)
        return
    
    # Check environment variables
    if not check_environment_variables():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🚀 OpenWebUI Chat Client - Comprehensive Integration Tests")
    print("=" * 60)
    
    test_categories = config.get('test_categories', {})
    
    # Determine which tests to run
    if args.category:
        if args.category not in test_categories:
            print(f"❌ Error: Unknown test category '{args.category}'")
            print(f"Available categories: {list(test_categories.keys())}")
            sys.exit(1)
        categories_to_run = {args.category: test_categories[args.category]}
    else:
        categories_to_run = test_categories
    
    # Run tests
    passed_tests = []
    failed_tests = []
    
    for category, test_config in categories_to_run.items():
        success = run_integration_test(category, test_config, args.verbose)
        if success:
            passed_tests.append(category)
        else:
            failed_tests.append(category)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Summary")
    print("=" * 60)
    
    if passed_tests:
        print(f"✅ Passed tests ({len(passed_tests)}):")
        for test in passed_tests:
            print(f"   - {test}")
    
    if failed_tests:
        print(f"\n❌ Failed tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   - {test}")
    
    total_tests = len(passed_tests) + len(failed_tests)
    success_rate = (len(passed_tests) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📈 Success rate: {success_rate:.1f}% ({len(passed_tests)}/{total_tests})")
    
    if failed_tests:
        print("\n💡 To run a specific failed test:")
        print(f"   python {sys.argv[0]} --category <category_name> --verbose")
        sys.exit(1)
    else:
        print("\n🎉 All integration tests passed successfully!")


if __name__ == '__main__':
    main()