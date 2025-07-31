# Selective Integration Testing

This directory contains scripts and configuration for intelligent, selective integration testing that runs only the relevant tests for changed code.

## Overview

The selective integration testing system automatically analyzes changed files in pull requests and pushes to determine which integration tests should be executed, significantly reducing CI time while maintaining comprehensive coverage.

## Components

### 1. Configuration (`test-mapping.yml`)

Defines:
- **Test Categories**: Available integration test types with their commands and descriptions
- **File Mappings**: Pattern-based mapping from file paths to test categories
- **Default Categories**: Fallback tests when no specific patterns match

### 2. Detection Script (`detect_required_tests.py`)

Analyzes Git changes and outputs JSON array of required test categories:

```bash
# Detect tests for current changes
python .github/scripts/detect_required_tests.py

# Compare specific refs
python .github/scripts/detect_required_tests.py origin/main HEAD

# Output example: ["connectivity", "basic_chat", "model_management"]
```

### 3. Manual Test Runner (`run_all_integration_tests.py`)

Comprehensive test runner for manual execution:

```bash
# Run all integration tests
python .github/scripts/run_all_integration_tests.py

# Run specific category
python .github/scripts/run_all_integration_tests.py --category notes_api

# List available categories
python .github/scripts/run_all_integration_tests.py --list-categories

# Verbose output
python .github/scripts/run_all_integration_tests.py --verbose
```

## How It Works

### In GitHub Actions

1. **Change Detection**: `detect-changes` job analyzes modified files
2. **Selective Testing**: Matrix strategy runs only required test categories
3. **Parallel Execution**: Multiple test categories run simultaneously
4. **Summary**: Reports which tests ran and why

### File-to-Test Mapping Examples

| Changed File | Triggered Tests |
|--------------|----------------|
| `openwebui_chat_client/openwebui_chat_client.py` | `connectivity`, `basic_chat`, `model_management` |
| `examples/notes_api/basic_notes.py` | `notes_api` |
| `examples/rag_knowledge/**` | `rag_integration` |
| `tests/**` | `connectivity` |
| No specific match | `connectivity`, `basic_chat` |

## Test Categories

### Core Categories

- **`connectivity`**: Basic client initialization and API connection
- **`basic_chat`**: Fundamental chat functionality
- **`model_management`**: Model CRUD operations
- **`notes_api`**: Notes API functionality
- **`rag_integration`**: RAG and knowledge base features
- **`model_switching`**: Model switching in existing chats
- **`comprehensive_demos`**: End-to-end workflow testing

### When Tests Run

| Scenario | Tests Executed |
|----------|----------------|
| Core client changes | Multiple relevant categories |
| Example script changes | Corresponding feature category |
| Test file changes | Basic connectivity |
| Documentation changes | No tests (unless override) |
| Manual trigger with override | All categories |

## Configuration

### Environment Variables

All standard OpenWebUI environment variables are required:

```bash
export OUI_BASE_URL="https://your-openwebui-instance.com"
export OUI_AUTH_TOKEN="your-auth-token"
export OUI_DEFAULT_MODEL="gpt-3.5-turbo"
export OUI_PARALLEL_MODELS="gpt-3.5-turbo,gpt-4"  # optional
```

### GitHub Actions Workflow

The modified `integration-test.yml` supports:

- **Automatic selective testing** based on changed files
- **Manual override** to run all tests via `workflow_dispatch`
- **Parallel execution** of test categories
- **Detailed reporting** of which tests ran and why

## Benefits

### For Developers

- **Faster CI**: Only relevant tests run for each change
- **Clear feedback**: Know exactly which functionality is being tested
- **Manual control**: Can override and run all tests when needed

### For Maintainers

- **Resource efficiency**: Reduced CI time and cost
- **Comprehensive coverage**: Important tests still run for any change
- **Flexibility**: Easy to adjust mappings and add new test categories

## Adding New Tests

### 1. Add Test Category

In `test-mapping.yml`:

```yaml
test_categories:
  new_feature:
    name: "New Feature Integration Test"
    command: "python examples/new_feature/test_script.py"
    description: "Tests new feature functionality"
```

### 2. Add File Mappings

```yaml
file_mappings:
  - pattern: "**/*new_feature*"
    categories: ["new_feature"]
```

### 3. Update Default Categories (if needed)

```yaml
default_categories:
  - "connectivity"
  - "basic_chat"
  - "new_feature"  # if it should always run
```

## Troubleshooting

### No Tests Detected

If no tests are detected for your changes:
- Check file patterns in `test-mapping.yml`
- Verify the detection script can access Git history
- Review the `default_categories` fallback

### Test Failures

- Use manual runner with `--verbose` for detailed output
- Check environment variables are properly set
- Verify OpenWebUI instance accessibility

### Updating Mappings

When adding new functionality:
1. Update `test-mapping.yml` with new patterns
2. Test the detection script locally
3. Consider adding integration tests to verify the feature

## Example Workflows

### Developer Making Chat Changes

```bash
# Make changes to chat functionality
git add openwebui_chat_client/openwebui_chat_client.py

# See what tests would run
python .github/scripts/detect_required_tests.py
# Output: ["connectivity", "basic_chat", "model_management"]

# Push changes - only these 3 test categories run in CI
git commit -m "Improve chat functionality"
git push
```

### Maintainer Running Full Test Suite

```bash
# Run all tests locally before release
python .github/scripts/run_all_integration_tests.py

# Or trigger all tests in GitHub Actions
# Use workflow_dispatch with run_all_tests = true
```

This selective testing system provides an intelligent balance between comprehensive testing and efficient resource usage, ensuring that changes are properly validated without unnecessary overhead.