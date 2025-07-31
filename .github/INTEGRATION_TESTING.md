# Integration Testing

This repository includes a comprehensive integration testing workflow that runs against a real OpenWebUI instance to verify that all API functionality works correctly.

## 🎯 Selective Testing (New!)

**GitHub Actions now runs only relevant integration tests based on changed files**, significantly reducing CI time while maintaining comprehensive coverage.

### How Selective Testing Works

- **Automatic Detection**: Analyzes changed files to determine required tests
- **Intelligent Mapping**: Maps file patterns to corresponding test categories  
- **Parallel Execution**: Runs multiple test categories simultaneously
- **Manual Override**: Option to run all tests when needed

### Example: What Tests Run

| Changed Files | Tests Executed |
|---------------|----------------|
| Core client code | `connectivity`, `basic_chat`, `model_management` |
| Notes examples | `notes_api` only |
| RAG functionality | `rag_integration`, `comprehensive_demos` |
| Documentation only | No tests (unless manually triggered) |

### Manual Full Testing

Users can still run **all integration tests** manually:

```bash
# Run all integration tests locally
python .github/scripts/run_all_integration_tests.py

# Run specific test category
python .github/scripts/run_all_integration_tests.py --category notes_api

# List available test categories
python .github/scripts/run_all_integration_tests.py --list-categories
```

## How It Works

The integration testing workflow (`.github/workflows/integration-test.yml`) uses intelligent selective testing:

### Automatic Selective Testing

1. **Change Detection**: Analyzes modified files in PR/push
2. **Test Mapping**: Determines relevant test categories using pattern matching
3. **Parallel Execution**: Runs only required tests simultaneously
4. **Smart Defaults**: Falls back to core tests if no patterns match

### Manual Full Testing

1. **Local Execution**: Run comprehensive test suite locally
2. **GitHub Actions Override**: Use workflow_dispatch with "run_all_tests" = true
3. **Category-Specific**: Run individual test categories as needed

### Test Categories

- **`connectivity`**: Basic client initialization and API connection
- **`basic_chat`**: Fundamental chat functionality  
- **`notes_api`**: Notes CRUD operations and API functionality
- **`rag_integration`**: RAG and knowledge base features
- **`model_management`**: Model CRUD operations and management
- **`model_switching`**: Model switching in existing chats
- **`comprehensive_demos`**: End-to-end workflow testing

## Configuration

### Repository Secrets (Recommended)

For automatic integration testing on every successful test run, configure these repository secrets:

- `OUI_BASE_URL`: Your OpenWebUI instance URL (e.g., `https://your-openwebui-instance.com`)
- `OUI_AUTH_TOKEN`: Your OpenWebUI authentication token
- `OUI_DEFAULT_MODEL`: A valid model ID available in your OpenWebUI instance
- `OUI_PARALLEL_MODELS`: Comma-separated list of models for parallel testing (optional, defaults to `gpt-4.1,gemini-2.5-flash`)

### Additional Optional Variables

- `OUI_MULTIMODAL_MODEL`: Model ID for multimodal operations (defaults to `OUI_DEFAULT_MODEL`)
- `OUI_RAG_MODEL`: Model ID optimized for RAG operations (defaults to `gemini-2.5-flash`)

### Manual Workflow Dispatch

You can also trigger integration tests manually with custom parameters:

1. Go to the Actions tab in your repository
2. Select "Integration Test" workflow
3. Click "Run workflow" 
4. Enter your OpenWebUI configuration:
   - Base URL
   - Auth Token  
   - Default Model ID
   - Parallel Models (optional)
   - **Run All Tests**: Check this to override selective testing and run all categories

### Selective Testing Configuration

The selective testing system uses `.github/test-mapping.yml` to define:
- File patterns that trigger specific test categories
- Available test categories and their commands
- Default fallback tests for unmatched changes

See [Selective Testing Documentation](.github/scripts/README-selective-testing.md) for detailed configuration and usage.

## What Gets Tested

### Notes API Functionality
- ✅ Create notes with title, data, and metadata
- ✅ Retrieve all notes with full user information
- ✅ Get simplified notes list
- ✅ Fetch specific notes by ID
- ✅ Update existing notes
- ✅ Delete notes

### Basic Chat Operations
- ✅ Single model chat
- ✅ Parallel model chat with multiple models
- ✅ Streaming chat functionality

### RAG (Retrieval Augmented Generation)
- ✅ File-based RAG operations
- ✅ Knowledge base creation and management
- ✅ RAG-powered chat sessions

### Model Management
- ✅ List available models and base models
- ✅ Create custom models
- ✅ Update model configurations
- ✅ Delete models

### Model Switching
- ✅ Switch chat models for existing conversations
- ✅ Support for single and multiple model configurations

### Comprehensive Demo Features
- ✅ All major client functionality in integrated workflows
- ✅ Real-world usage patterns

### Basic Connectivity
- ✅ Client initialization with real credentials
- ✅ Model listing and discovery
- ✅ Authentication verification

## Example Output

When integration tests run successfully, you'll see output like:

```
🧪 Running Notes API integration test...
✅ Environment variables detected. Running integration test...
   Base URL: https://your-openwebui-instance.com
   Model: gpt-3.5-turbo

=== Notes API Example ===

1. Creating a new note...
   ✅ Created note with ID: note_abc123
   Title: My Example Note

2. Getting all notes...
   ✅ Retrieved 15 notes

🧪 Running basic usage integration test...
--- Starting a new multi-model parallel chat ---
Chat session saved with ID: chat_123

🧪 Running RAG integration test...
✅ Created test file: apollo_brief.txt
🤖 [RAG Response]: Based on the document, Project Apollo's primary objective...

🧪 Running model management integration test...
Found 8 models:
  - ID: gpt-3.5-turbo, Name: GPT-3.5 Turbo
  - ID: gpt-4, Name: GPT-4

🧪 Running model switch integration test...
✅ Successfully switched chat to model 'gpt-4'

🧪 Running comprehensive demos integration test...
✅ Comprehensive demos integration test passed!

🎉 All integration tests completed successfully!
```

## Local Testing

You can also run integration tests locally by setting environment variables:

```bash
# Set required environment variables
export OUI_BASE_URL="https://your-openwebui-instance.com"
export OUI_AUTH_TOKEN="your-access-token"
export OUI_DEFAULT_MODEL="gpt-3.5-turbo"

# Set optional environment variables
export OUI_PARALLEL_MODELS="gpt-3.5-turbo,gpt-4,claude-3-haiku"
export OUI_MULTIMODAL_MODEL="gpt-4-vision-preview"
export OUI_RAG_MODEL="gemini-pro"

# Run individual examples
python examples/notes_api/basic_notes.py
python examples/getting_started/basic_chat.py
python examples/rag_knowledge/file_rag.py
python examples/model_management/model_operations.py
python examples/chat_features/model_switching.py

# Or run comprehensive demos
python examples/getting_started/quick_start.py
```

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OUI_BASE_URL` | ✅ Yes | None | Your OpenWebUI instance URL |
| `OUI_AUTH_TOKEN` | ✅ Yes | None | Authentication token |
| `OUI_DEFAULT_MODEL` | ✅ Yes | `gpt-4.1` | Default model for operations |
| `OUI_PARALLEL_MODELS` | ❌ No | `gpt-4.1,gemini-2.5-flash` | Comma-separated models for parallel testing |
| `OUI_MULTIMODAL_MODEL` | ❌ No | Same as default | Model for multimodal operations |
| `OUI_RAG_MODEL` | ❌ No | `gemini-2.5-flash` | Model optimized for RAG tasks |

## Security Notes

- Never commit authentication tokens to the repository
- Use GitHub Secrets for automatic testing
- Tokens should have minimal required permissions
- Consider using a dedicated test account for integration testing

## Troubleshooting

### Missing Environment Variables
If you see missing environment variable warnings, ensure all required variables are set:
- `OUI_BASE_URL`
- `OUI_AUTH_TOKEN` 
- `OUI_DEFAULT_MODEL`

### Connection Errors
- Verify your OpenWebUI instance is accessible
- Check that your authentication token is valid
- Ensure the specified model IDs exist in your instance

### Model Not Found Errors
- Verify all models in `OUI_PARALLEL_MODELS` exist in your instance
- Use the model management example to list available models:
  ```bash
  python examples/model_management/model_operations.py
  ```

### API Errors
- Confirm your token has sufficient permissions for all API operations
- Check that your OpenWebUI instance supports all API endpoints
- Verify the API version compatibility