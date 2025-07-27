#!/usr/bin/env python3
"""
Tests for the changelog extraction script
"""
import unittest
import tempfile
import os
import sys

# Add the scripts directory to the path
script_dir = os.path.join(os.path.dirname(__file__), '..', '.github', 'scripts')
sys.path.insert(0, script_dir)

from extract_changelog import extract_version_changelog, get_version_from_pyproject


class TestChangelogExtraction(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_changelog = """# Changelog

All notable changes to this project will be documented in this file.

## [0.1.12] - 2025-07-27

### Added in 0.1.12
- New feature A
- New feature B

### Changed in 0.1.12
- Updated feature C

## [0.1.11] - 2025-07-26

### Added in 0.1.11
- Previous feature

---

## [0.1.10] - 2025-07-20

### Added in 0.1.10
- Older feature
"""

        self.test_pyproject = """[build-system]
requires = ["setuptools>=61.0"]

[project]
name = "test-package"
version = "0.1.12"
description = "Test package"
"""

    def test_extract_version_changelog_success(self):
        """Test successful changelog extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(self.test_changelog)
            f.flush()
            
            result = extract_version_changelog(f.name, "0.1.12")
            
            self.assertIsNotNone(result)
            self.assertIn("New feature A", result)
            self.assertIn("New feature B", result)
            self.assertIn("Updated feature C", result)
            self.assertNotIn("Previous feature", result)
            
            os.unlink(f.name)

    def test_extract_version_changelog_not_found(self):
        """Test changelog extraction for non-existent version."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(self.test_changelog)
            f.flush()
            
            result = extract_version_changelog(f.name, "0.1.999")
            
            self.assertIsNone(result)
            
            os.unlink(f.name)

    def test_get_version_from_pyproject(self):
        """Test version extraction from pyproject.toml."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(self.test_pyproject)
            f.flush()
            
            result = get_version_from_pyproject(f.name)
            
            self.assertEqual(result, "0.1.12")
            
            os.unlink(f.name)

    def test_get_version_from_pyproject_not_found(self):
        """Test version extraction from file without version."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("[build-system]\nrequires = ['setuptools']")
            f.flush()
            
            result = get_version_from_pyproject(f.name)
            
            self.assertIsNone(result)
            
            os.unlink(f.name)


if __name__ == '__main__':
    unittest.main()