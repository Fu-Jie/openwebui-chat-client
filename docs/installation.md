# Installation Guide

This guide covers the installation of `openwebui-chat-client` and its dependencies.

---

## Requirements

- **Python**: 3.8 or higher
- **Open WebUI**: A running Open WebUI instance with API access

---

## Installation

### From PyPI (Recommended)

The easiest way to install `openwebui-chat-client` is via pip:

```bash
pip install openwebui-chat-client
```

### From Source

If you want to install the latest development version:

```bash
git clone https://github.com/Fu-Jie/openwebui-chat-client.git
cd openwebui-chat-client
pip install -e .
```

### With Test Dependencies

If you plan to run tests:

```bash
pip install openwebui-chat-client[test]
```

---

## Dependencies

The package has the following core dependencies (automatically installed):

| Package | Purpose |
|---------|---------|
| `requests` | HTTP client for synchronous API calls |
| `httpx` | HTTP client for asynchronous API calls |
| `python-dotenv` | Environment variable management |

### Optional Dependencies

| Package | Purpose | Install With |
|---------|---------|--------------|
| `responses` | HTTP mocking for tests | `pip install openwebui-chat-client[test]` |

---

## Configuration

### Environment Variables

You can configure the client using environment variables:

```bash
# Required
export OUI_BASE_URL="http://localhost:3000"
export OUI_AUTH_TOKEN="your-bearer-token"

# Optional
export OUI_DEFAULT_MODEL="gpt-4.1"
```

### Using a `.env` File

Create a `.env` file in your project root:

```ini
OUI_BASE_URL=http://localhost:3000
OUI_AUTH_TOKEN=your-bearer-token
OUI_DEFAULT_MODEL=gpt-4.1
```

The client will automatically load these variables using `python-dotenv`.

---

## Verification

After installation, verify that the package is installed correctly:

```python
from openwebui_chat_client import OpenWebUIClient

# Check the version
import openwebui_chat_client
print(f"Version: {openwebui_chat_client.__version__}")

# Test connection
client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

# List available models to verify connectivity
models = client.list_models()
if models:
    print(f"Connected! Found {len(models)} models.")
else:
    print("Connection failed or no models available.")
```

---

## Troubleshooting

### Common Issues

#### `ModuleNotFoundError: No module named 'openwebui_chat_client'`

Ensure the package is installed in your current Python environment:

```bash
pip list | grep openwebui-chat-client
```

#### Connection Errors

1. Verify your Open WebUI instance is running
2. Check that the `base_url` is correct
3. Ensure your API token is valid

#### SSL Certificate Errors

If you're connecting to a server with a self-signed certificate:

```python
client = AsyncOpenWebUIClient(
    base_url="https://your-server:3000",
    token="your-token",
    default_model_id="gpt-4.1",
    verify=False  # Disable SSL verification (not recommended for production)
)
```

---

## Next Steps

- [User Guide](usage.md) - Learn how to use the client
- [API Reference](api.md) - Explore the complete API
