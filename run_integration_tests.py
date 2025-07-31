#!/usr/bin/env python3
"""
Quick Integration Test Runner

A simple wrapper script that makes it easy for users to run integration tests
without needing to navigate to the .github/scripts directory.

Usage:
    python run_integration_tests.py [options]
    
This script is a convenience wrapper around the main integration test runner.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run the integration test script with forwarded arguments."""
    # Get the path to the actual integration test script
    script_dir = Path(__file__).parent
    integration_script = script_dir / ".github" / "scripts" / "run_all_integration_tests.py"
    
    if not integration_script.exists():
        print(f"❌ Error: Integration test script not found at {integration_script}")
        sys.exit(1)
    
    # Forward all arguments to the real script
    cmd = [sys.executable, str(integration_script)] + sys.argv[1:]
    
    try:
        # Run the integration test script
        result = subprocess.run(cmd, cwd=script_dir)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⏹️  Integration tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()