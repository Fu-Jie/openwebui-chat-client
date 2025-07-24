# GitHub Actions CI/CD Setup

This repository uses GitHub Actions for Continuous Integration and Continuous Deployment.

## Workflows

### 1. Test Workflow (`test.yml`)
- **Triggers**: On push to main/master branch and on pull requests
- **Purpose**: Runs tests across multiple Python versions (3.8-3.13)
- **Actions**:
  - Sets up Python environment
  - Installs package dependencies
  - Runs all unit tests using Python's unittest framework

### 2. Publish Workflow (`publish.yml`)
- **Triggers**: On GitHub releases and version tags (v*)
- **Purpose**: Builds and publishes the package to PyPI
- **Actions**:
  - Runs tests first to ensure quality
  - Builds Python package (wheel and source distribution)
  - Validates the built package
  - Publishes to PyPI using API token

## Setup Requirements

### For PyPI Publishing
1. Create a PyPI API token at https://pypi.org/manage/account/token/
2. Add the token as a repository secret named `PYPI_API_TOKEN`:
   - Go to repository Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (starts with `pypi-`)

### Creating a Release
1. Update the version in `pyproject.toml`
2. Create a git tag: `git tag v0.1.11` (or your version)
3. Push the tag: `git push origin v0.1.11`
4. Create a GitHub release from the tag
5. The publish workflow will automatically trigger

## Workflow Features
- **No code quality checks**: As requested, these workflows focus only on testing and publishing
- **Multi-version testing**: Ensures compatibility across Python 3.8-3.13
- **Safe publishing**: Tests must pass before publishing
- **Automated**: No manual intervention required after setup