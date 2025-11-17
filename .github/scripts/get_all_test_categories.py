#!/usr/bin/env python3
"""
Get all test categories from test-mapping.yml

This script reads the test-mapping.yml configuration and outputs all available
test categories as a JSON array, suitable for GitHub Actions matrix strategy.

Usage:
    python .github/scripts/get_all_test_categories.py

Output:
    JSON array of test categories, e.g.: ["notes_api", "prompts_api", "basic_chat", ...]
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML is required. Install with: pip install PyYAML", file=sys.stderr
    )
    sys.exit(1)


def get_test_categories():
    """Load test categories from test-mapping.yml"""
    config_path = Path(__file__).parent.parent.parent / ".github" / "test-mapping.yml"

    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Extract test categories
        test_categories = config.get("test_categories", {})
        categories = list(test_categories.keys())

        if not categories:
            print(
                "Error: No test categories found in test-mapping.yml", file=sys.stderr
            )
            sys.exit(1)

        # Sort for consistency
        categories.sort()

        return categories

    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading configuration: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    categories = get_test_categories()
    # Output as JSON array for GitHub Actions
    print(json.dumps(categories))
