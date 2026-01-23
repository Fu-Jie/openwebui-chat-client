#!/usr/bin/env python3
"""
Refactored Integration Test Runner v2.0

Major improvements:
1. ⚡ Parallel execution support (ThreadPoolExecutor)
2. 🎯 Smart test grouping (fast/medium/slow)
3. ⏱️ Timeout per test category with configurable limits
4. 📊 Real-time progress tracking
5. 🔄 Retry logic for flaky tests
6. 📝 Detailed JSON reports
7. 🎨 Better output formatting with rich colors

Usage:
    # Run all tests in parallel (default)
    python .github/scripts/run_integration_tests_v2.py

    # Run specific category
    python .github/scripts/run_integration_tests_v2.py --category basic_chat

    # Run fast tests only
    python .github/scripts/run_integration_tests_v2.py --group fast

    # Sequential execution (for debugging)
    python .github/scripts/run_integration_tests_v2.py --no-parallel

    # With retry for flaky tests
    python .github/scripts/run_integration_tests_v2.py --retry 2
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class TestResult:
    """Test result data class."""

    category: str
    name: str
    passed: bool
    duration: float
    output: str = ""
    error: str = ""
    attempt: int = 1
    max_attempts: int = 1


@dataclass
class TestConfig:
    """Test configuration data class."""

    category: str
    name: str
    command: str
    description: str
    timeout: int = 120  # Default 2 minutes
    group: str = "medium"  # fast, medium, slow
    retry: int = 0  # Number of retries for flaky tests


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def colorize(text: str, color: str) -> str:
    """Add color to text."""
    return f"{color}{text}{Colors.ENDC}"


def load_test_mapping(config_file: str) -> Dict[str, Any]:
    """Load test mapping configuration from YAML file."""
    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Enhance test categories with metadata
        test_categories = config.get("test_categories", {})

        # Classify tests by speed/complexity
        fast_tests = ["connectivity"]
        slow_tests = [
            "comprehensive_demos",
            "deep_research",
            "process_task",
            "stream_process_task",
        ]

        for category, details in test_categories.items():
            # Set group
            if category in fast_tests:
                details["group"] = "fast"
            elif category in slow_tests:
                details["group"] = "slow"
            else:
                details["group"] = "medium"

            # Set timeout based on group
            if details["group"] == "fast":
                details["timeout"] = 30
            elif details["group"] == "slow":
                details["timeout"] = 300
            else:
                details["timeout"] = 120

            # Set retry for known flaky tests
            if category in ["connectivity", "basic_chat"]:
                details["retry"] = 1

        return config
    except Exception as e:
        print(colorize(f"❌ Error: Failed to load test mapping: {e}", Colors.FAIL))
        sys.exit(1)


def check_environment_variables() -> bool:
    """Check if required environment variables are set."""
    required_vars = ["OUI_BASE_URL", "OUI_AUTH_TOKEN", "OUI_DEFAULT_MODEL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(colorize("❌ Missing required environment variables:", Colors.FAIL))
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables:")
        print("export OUI_BASE_URL='http://localhost:3003'")
        print("export OUI_AUTH_TOKEN='your-auth-token'")
        print("export OUI_DEFAULT_MODEL='gpt-4.1'")
        return False

    print(colorize("✅ Environment variables verified", Colors.OKGREEN))
    print(f"   Base URL: {os.getenv('OUI_BASE_URL')}")
    print(
        f"   Auth Token: ***{os.getenv('OUI_AUTH_TOKEN', '')[-4:] if os.getenv('OUI_AUTH_TOKEN') else 'not set'}"
    )
    print(f"   Default Model: {os.getenv('OUI_DEFAULT_MODEL')}")

    return True


def run_single_test(
    test_config: TestConfig, verbose: bool = False, attempt: int = 1
) -> TestResult:
    """Run a single integration test."""
    start_time = time.time()

    try:
        repo_root = Path(__file__).parent.parent.parent
        env = os.environ.copy()

        # Set fallback environment variables
        env.update(
            {
                "OUI_MULTIMODAL_MODEL": env.get(
                    "OUI_MULTIMODAL_MODEL", env.get("OUI_DEFAULT_MODEL", "")
                ),
                "OUI_RAG_MODEL": env.get(
                    "OUI_RAG_MODEL", env.get("OUI_DEFAULT_MODEL", "")
                ),
            }
        )

        result = subprocess.run(
            shlex.split(test_config.command),
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=test_config.timeout,
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            return TestResult(
                category=test_config.category,
                name=test_config.name,
                passed=True,
                duration=duration,
                output=result.stdout if verbose else "",
                attempt=attempt,
                max_attempts=test_config.retry + 1,
            )
        else:
            return TestResult(
                category=test_config.category,
                name=test_config.name,
                passed=False,
                duration=duration,
                output=result.stdout if verbose else "",
                error=result.stderr,
                attempt=attempt,
                max_attempts=test_config.retry + 1,
            )

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return TestResult(
            category=test_config.category,
            name=test_config.name,
            passed=False,
            duration=duration,
            error=f"Test timed out after {test_config.timeout}s",
            attempt=attempt,
            max_attempts=test_config.retry + 1,
        )
    except Exception as e:
        duration = time.time() - start_time
        return TestResult(
            category=test_config.category,
            name=test_config.name,
            passed=False,
            duration=duration,
            error=str(e),
            attempt=attempt,
            max_attempts=test_config.retry + 1,
        )


def run_test_with_retry(test_config: TestConfig, verbose: bool = False) -> TestResult:
    """Run a test with retry logic."""
    max_attempts = test_config.retry + 1

    for attempt in range(1, max_attempts + 1):
        result = run_single_test(test_config, verbose, attempt)

        if result.passed:
            return result

        if attempt < max_attempts:
            print(
                colorize(
                    f"   ⚠️  Attempt {attempt}/{max_attempts} failed, retrying...",
                    Colors.WARNING,
                )
            )
            time.sleep(1)  # Brief pause before retry

    return result


def print_test_progress(
    current: int, total: int, test_name: str, status: str = "running"
) -> None:
    """Print test progress."""
    percentage = (current / total * 100) if total > 0 else 0
    if status == "running":
        symbol = "🔄"
        color = Colors.OKCYAN
    elif status == "passed":
        symbol = "✅"
        color = Colors.OKGREEN
    elif status == "failed":
        symbol = "❌"
        color = Colors.FAIL
    else:
        symbol = "⏳"
        color = Colors.WARNING

    print(
        colorize(f"{symbol} [{current}/{total}] ({percentage:.0f}%) {test_name}", color)
    )


def run_tests_parallel(
    test_configs: List[TestConfig], verbose: bool = False, max_workers: int = 4
) -> List[TestResult]:
    """Run tests in parallel."""
    results = []
    total = len(test_configs)

    print(
        colorize(
            f"\n🚀 Running {total} tests in parallel (max {max_workers} workers)...\n",
            Colors.BOLD,
        )
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tests
        future_to_test = {
            executor.submit(run_test_with_retry, config, verbose): config
            for config in test_configs
        }

        # Process completed tests
        completed = 0
        for future in as_completed(future_to_test):
            test_config = future_to_test[future]
            result = future.result()
            results.append(result)
            completed += 1

            # Print progress
            status = "passed" if result.passed else "failed"
            print_test_progress(completed, total, test_config.name, status)

            if not result.passed and verbose:
                print(colorize(f"   Error: {result.error}", Colors.FAIL))

    return results


def run_tests_sequential(
    test_configs: List[TestConfig], verbose: bool = False
) -> List[TestResult]:
    """Run tests sequentially."""
    results = []
    total = len(test_configs)

    print(colorize(f"\n🐌 Running {total} tests sequentially...\n", Colors.BOLD))

    for idx, config in enumerate(test_configs, 1):
        print_test_progress(idx, total, config.name, "running")
        result = run_test_with_retry(config, verbose)
        results.append(result)

        status = "passed" if result.passed else "failed"
        print_test_progress(idx, total, config.name, status)

        if not result.passed and verbose:
            print(colorize(f"   Error: {result.error}", Colors.FAIL))

    return results


def print_summary(results: List[TestResult], verbose: bool = False) -> None:
    """Print test summary."""
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    total = len(results)

    print("\n" + "=" * 70)
    print(colorize("📊 Integration Test Summary", Colors.BOLD))
    print("=" * 70)

    # Success rate
    success_rate = (len(passed) / total * 100) if total > 0 else 0
    rate_color = Colors.OKGREEN if success_rate >= 80 else Colors.WARNING
    print(
        colorize(
            f"📈 Success Rate: {success_rate:.1f}% ({len(passed)}/{total})",
            rate_color,
        )
    )

    # Total time
    total_time = sum(r.duration for r in results)
    print(f"⏱️  Total Time: {total_time:.2f}s")

    # Passed tests
    if passed:
        print(colorize(f"\n✅ Passed Tests ({len(passed)}):", Colors.OKGREEN))
        for result in passed:
            retry_info = (
                f" (attempt {result.attempt}/{result.max_attempts})"
                if result.attempt > 1
                else ""
            )
            print(f"   • {result.category} - {result.duration:.2f}s{retry_info}")

    # Failed tests
    if failed:
        print(colorize(f"\n❌ Failed Tests ({len(failed)}):", Colors.FAIL))
        for result in failed:
            print(f"   • {result.category} - {result.duration:.2f}s")
            if verbose and result.error:
                print(colorize(f"     Error: {result.error[:200]}...", Colors.FAIL))

    # Group analysis
    if results:
        print("\n📦 Tests by Group:")
        groups = {}
        for result in results:
            group = getattr(result, "group", "unknown")
            if group not in groups:
                groups[group] = {"passed": 0, "failed": 0}
            if result.passed:
                groups[group]["passed"] += 1
            else:
                groups[group]["failed"] += 1

        for group, stats in groups.items():
            total_in_group = stats["passed"] + stats["failed"]
            rate = (stats["passed"] / total_in_group * 100) if total_in_group > 0 else 0
            print(f"   {group}: {stats['passed']}/{total_in_group} ({rate:.0f}%)")


def save_json_report(results: List[TestResult], output_file: str) -> None:
    """Save test results to JSON file."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "passed": len([r for r in results if r.passed]),
        "failed": len([r for r in results if not r.passed]),
        "total_duration": sum(r.duration for r in results),
        "tests": [
            {
                "category": r.category,
                "name": r.name,
                "passed": r.passed,
                "duration": r.duration,
                "error": r.error if not r.passed else None,
                "attempt": r.attempt,
                "max_attempts": r.max_attempts,
            }
            for r in results
        ],
    }

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(colorize(f"\n💾 Report saved to: {output_file}", Colors.OKBLUE))


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run integration tests with parallel execution support"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--category", "-c", type=str, help="Run specific category")
    parser.add_argument(
        "--group",
        "-g",
        type=str,
        choices=["fast", "medium", "slow"],
        help="Run tests by group",
    )
    parser.add_argument(
        "--no-parallel", action="store_true", help="Run tests sequentially"
    )
    parser.add_argument(
        "--max-workers", type=int, default=4, help="Max parallel workers (default: 4)"
    )
    parser.add_argument(
        "--list-categories", action="store_true", help="List all test categories"
    )
    parser.add_argument(
        "--retry", type=int, default=None, help="Override retry count for all tests"
    )
    parser.add_argument(
        "--report", type=str, help="Save JSON report to file", default=None
    )

    args = parser.parse_args()

    # Load configuration
    script_dir = Path(__file__).parent
    config_file = script_dir.parent / "test-mapping.yml"
    config = load_test_mapping(str(config_file))

    test_categories = config.get("test_categories", {})

    # List categories
    if args.list_categories:
        print(colorize("📋 Available Test Categories:\n", Colors.BOLD))
        for category, details in test_categories.items():
            group_color = (
                Colors.OKGREEN
                if details["group"] == "fast"
                else Colors.WARNING if details["group"] == "slow" else Colors.OKCYAN
            )
            print(colorize(f"  [{details['group']}] {category}", group_color))
            print(f"    Name: {details['name']}")
            print(f"    Timeout: {details['timeout']}s")
            print(f"    Retry: {details.get('retry', 0)}")
            print()
        return

    # Check environment
    if not check_environment_variables():
        sys.exit(1)

    print("\n" + "=" * 70)
    print(colorize("🚀 OpenWebUI Chat Client - Integration Tests v2.0", Colors.BOLD))
    print("=" * 70)

    # Build test configs
    test_configs = []
    for category, details in test_categories.items():
        # Filter by category
        if args.category and category != args.category:
            continue

        # Filter by group
        if args.group and details.get("group") != args.group:
            continue

        config = TestConfig(
            category=category,
            name=details["name"],
            command=details["command"],
            description=details["description"],
            timeout=details.get("timeout", 120),
            group=details.get("group", "medium"),
            retry=args.retry if args.retry is not None else details.get("retry", 0),
        )
        test_configs.append(config)

    if not test_configs:
        print(colorize("❌ No tests to run!", Colors.FAIL))
        sys.exit(1)

    print(f"📦 Test Selection: {len(test_configs)} tests")
    if args.category:
        print(f"   Category filter: {args.category}")
    if args.group:
        print(f"   Group filter: {args.group}")

    # Run tests
    if args.no_parallel:
        results = run_tests_sequential(test_configs, args.verbose)
    else:
        results = run_tests_parallel(test_configs, args.verbose, args.max_workers)

    # Print summary
    print_summary(results, args.verbose)

    # Save report
    if args.report:
        save_json_report(results, args.report)

    # Exit code
    failed_count = len([r for r in results if not r.passed])
    if failed_count > 0:
        print(colorize(f"\n💡 {failed_count} test(s) failed", Colors.WARNING))
        sys.exit(1)
    else:
        print(colorize("\n🎉 All tests passed!", Colors.OKGREEN))


if __name__ == "__main__":
    main()
