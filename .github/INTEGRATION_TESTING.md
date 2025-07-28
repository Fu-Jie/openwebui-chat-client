# Integration Testing

This repository includes an integration testing workflow that runs against a real OpenWebUI instance to verify that the API functionality works correctly.

## How It Works

The integration testing workflow (`.github/workflows/integration-test.yml`) automatically runs after the main test suite passes. It performs the following:

1. **Automatic Trigger**: Runs when the main test workflow completes successfully
2. **Environment Setup**: Configures a real OpenWebUI environment using secrets or manual inputs
3. **Notes API Testing**: Executes the Notes API example to verify all functionality works
4. **Connectivity Testing**: Performs basic connectivity tests to ensure the client can communicate with OpenWebUI

## Configuration

### Repository Secrets (Recommended)

For automatic integration testing on every successful test run, configure these repository secrets:

- `OUI_BASE_URL`: Your OpenWebUI instance URL (e.g., `https://your-openwebui-instance.com`)
- `OUI_AUTH_TOKEN`: Your OpenWebUI authentication token
- `OUI_DEFAULT_MODEL`: A valid model ID available in your OpenWebUI instance

### Manual Workflow Dispatch

You can also trigger the integration tests manually with custom parameters:

1. Go to the Actions tab in your repository
2. Select "Integration Test" workflow
3. Click "Run workflow" 
4. Enter your OpenWebUI configuration:
   - Base URL
   - Auth Token  
   - Default Model ID

## What Gets Tested

### Notes API Functionality
- ✅ Create notes with title, data, and metadata
- ✅ Retrieve all notes with full user information
- ✅ Get simplified notes list
- ✅ Fetch specific notes by ID
- ✅ Update existing notes
- ✅ Delete notes

### Basic Connectivity
- ✅ Client initialization with real credentials
- ✅ Model listing and discovery
- ✅ Authentication verification

## Example Output

When integration tests run successfully, you'll see output like:

```
✅ Environment variables detected. Running integration test...
   Base URL: https://your-openwebui-instance.com
   Model: gpt-3.5-turbo

Connecting to: https://your-openwebui-instance.com
Using model: gpt-3.5-turbo

✅ Client initialized successfully
=== Notes API Example ===

1. Creating a new note...
   ✅ Created note with ID: note_abc123
   Title: My Example Note

2. Getting all notes...
   ✅ Retrieved 15 notes
   - My Example Note (ID: note_abc...)
   - Previous Note (ID: note_def...)

...

✅ All Notes API operations completed successfully!
🎉 Integration test passed!
```

## Local Testing

You can also run integration tests locally by setting environment variables:

```bash
# Set environment variables
export OUI_BASE_URL="https://your-openwebui-instance.com"
export OUI_AUTH_TOKEN="your-access-token"
export OUI_DEFAULT_MODEL="gpt-3.5-turbo"

# Run the Notes API example
python examples/notes_api_example.py
```

## Security Notes

- Never commit authentication tokens to the repository
- Use GitHub Secrets for automatic testing
- Tokens should have minimal required permissions
- Consider using a dedicated test account for integration testing

## Troubleshooting

### Missing Environment Variables
If you see missing environment variable warnings, ensure all three required variables are set:
- `OUI_BASE_URL`
- `OUI_AUTH_TOKEN` 
- `OUI_DEFAULT_MODEL`

### Connection Errors
- Verify your OpenWebUI instance is accessible
- Check that your authentication token is valid
- Ensure the specified model ID exists in your instance

### API Errors
- Confirm your token has sufficient permissions for Notes API operations
- Check that your OpenWebUI instance supports the Notes API endpoints
- Verify the API version compatibility