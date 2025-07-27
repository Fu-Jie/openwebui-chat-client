#!/usr/bin/env python3
"""
Extract changelog content for a specific version from CHANGELOG.md
"""
import sys
import re
import argparse
from pathlib import Path


def extract_version_changelog(changelog_path, version):
    """
    Extract changelog content for a specific version.
    
    Args:
        changelog_path (str): Path to CHANGELOG.md file
        version (str): Version to extract (e.g., "0.1.12")
    
    Returns:
        str: Formatted changelog content for the version
    """
    try:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: CHANGELOG.md not found at {changelog_path}")
        return None
    
    # Pattern to match version headers like "## [0.1.12] - 2025-07-27"
    version_pattern = rf'^## \[{re.escape(version)}\] - (.+)$'
    
    lines = content.split('\n')
    start_idx = None
    end_idx = None
    
    # Find the start of the target version section
    for i, line in enumerate(lines):
        if re.match(version_pattern, line):
            start_idx = i
            break
    
    if start_idx is None:
        print(f"Error: Version {version} not found in changelog")
        return None
    
    # Find the end of the target version section (next version or end of file)
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        # Check if this is another version header
        if re.match(r'^## \[.+\] - .+$', line):
            end_idx = i
            break
        # Check for horizontal rule separator
        if line.strip() == '---':
            end_idx = i
            break
    
    if end_idx is None:
        end_idx = len(lines)
    
    # Extract the content between start and end
    version_lines = lines[start_idx:end_idx]
    
    # Remove the version header line and clean up
    changelog_content = []
    for line in version_lines[1:]:  # Skip the version header
        if line.strip() == '---':  # Stop at separator
            break
        changelog_content.append(line)
    
    # Remove trailing empty lines
    while changelog_content and not changelog_content[-1].strip():
        changelog_content.pop()
    
    return '\n'.join(changelog_content).strip()


def get_version_from_pyproject(pyproject_path):
    """
    Extract version from pyproject.toml file.
    
    Args:
        pyproject_path (str): Path to pyproject.toml file
    
    Returns:
        str: Version string or None if not found
    """
    try:
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: pyproject.toml not found at {pyproject_path}")
        return None
    
    # Look for version = "x.x.x" line
    version_match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    
    print("Error: Version not found in pyproject.toml")
    return None


def main():
    parser = argparse.ArgumentParser(description='Extract changelog content for a version')
    parser.add_argument('--version', help='Version to extract (if not provided, reads from pyproject.toml)')
    parser.add_argument('--changelog', default='CHANGELOG.md', help='Path to changelog file')
    parser.add_argument('--pyproject', default='pyproject.toml', help='Path to pyproject.toml file')
    parser.add_argument('--output', help='Output file (if not provided, prints to stdout)')
    
    args = parser.parse_args()
    
    # Get version from argument or pyproject.toml
    version = args.version
    if not version:
        version = get_version_from_pyproject(args.pyproject)
        if not version:
            sys.exit(1)
    
    print(f"Extracting changelog for version {version}")
    
    # Extract changelog content
    changelog_content = extract_version_changelog(args.changelog, version)
    if not changelog_content:
        sys.exit(1)
    
    # Format the release notes
    release_notes = f"## What's New in v{version}\n\n{changelog_content}"
    
    # Output the content
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(release_notes)
        print(f"Changelog content written to {args.output}")
    else:
        print("\n" + "="*50)
        print("RELEASE NOTES:")
        print("="*50)
        print(release_notes)


if __name__ == '__main__':
    main()