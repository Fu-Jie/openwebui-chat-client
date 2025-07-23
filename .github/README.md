# GitHub Actions CI/CD

This repository includes comprehensive GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 🧪 CI Workflow (`.github/workflows/ci.yml`)
- **Trigger**: Push to `main`/`master`/`develop` branches and pull requests
- **Testing**: Runs tests across multiple Python versions (3.8-3.12) and OS (Ubuntu, Windows, macOS)
- **Build**: Creates distribution packages and uploads as artifacts
- **Validation**: Ensures package can be imported successfully

### 🔍 Code Quality Workflow (`.github/workflows/lint.yml`)
- **Trigger**: Push to `main`/`master`/`develop` branches and pull requests
- **Linting**: Uses flake8 to check for syntax errors and code quality issues
- **Formatting**: Reports code formatting status with black and isort (informational)

### 🚀 Release Workflow (`.github/workflows/release.yml`)
- **Trigger**: When a GitHub release is published
- **Publishing**: Automatically builds and publishes to PyPI
- **Security**: Uses PyPI API token stored in GitHub secrets (`PYPI_API_TOKEN`)

## Setup Requirements

### For PyPI Publishing
To enable automatic PyPI publishing, add your PyPI API token as a repository secret:

1. Generate an API token at https://pypi.org/manage/account/token/
2. Go to repository Settings → Secrets and variables → Actions
3. Add a new secret named `PYPI_API_TOKEN` with your token value

### Branch Protection
Consider enabling branch protection rules for `main` branch requiring:
- Status checks to pass before merging
- Up-to-date branches before merging

## Local Development

Install development dependencies:
```bash
pip install flake8 black isort
```

Run code quality checks:
```bash
# Check syntax and basic issues
flake8 openwebui_chat_client/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Format code (optional)
black openwebui_chat_client/ tests/
isort openwebui_chat_client/ tests/
```