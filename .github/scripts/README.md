# GitHub Actions Scripts

This directory contains utility scripts used by GitHub Actions workflows.

## extract_changelog.py

This script extracts changelog content for a specific version from `CHANGELOG.md` and formats it for GitHub releases.

### Usage

```bash
# Extract changelog content for the current version (from pyproject.toml)
python .github/scripts/extract_changelog.py

# Extract changelog content for a specific version
python .github/scripts/extract_changelog.py --version 0.1.12

# Save to file
python .github/scripts/extract_changelog.py --output release_notes.md

# Specify custom paths
python .github/scripts/extract_changelog.py --changelog CHANGELOG.md --pyproject pyproject.toml
```

### Parameters

- `--version`: Version to extract (if not provided, reads from pyproject.toml)
- `--changelog`: Path to changelog file (default: CHANGELOG.md)
- `--pyproject`: Path to pyproject.toml file (default: pyproject.toml)
- `--output`: Output file (if not provided, prints to stdout)

### How it works

1. Parses the `CHANGELOG.md` file to find the section for the specified version
2. Extracts content between the version header and the next version or separator
3. Formats the content for GitHub release notes
4. Outputs the formatted content

### Expected CHANGELOG.md format

```markdown
## [version] - date

### Added in version
- Feature A
- Feature B

### Changed in version
- Updated feature C

---

## [previous-version] - date
...
```

The script automatically handles:
- Version extraction from pyproject.toml
- Content extraction between version sections
- Proper formatting for GitHub releases
- Error handling for missing versions or files