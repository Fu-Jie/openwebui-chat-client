# OpenWebUI Chat Client Examples

This directory contains comprehensive examples demonstrating all features of the OpenWebUI Chat Client library.

## 📁 Directory Structure

```
examples/
├── README.md                     # This file
├── config/                       # Configuration and setup examples
│   ├── basic_config.py          # Basic client configuration
│   └── environment_setup.py     # Environment variables setup guide
├── getting_started/              # Basic usage examples
│   ├── hello_world.py           # Simplest possible example
│   ├── basic_chat.py            # Basic chat functionality
│   └── quick_start.py           # Quick start guide with multiple features
├── chat_features/                # Chat-related functionality
│   ├── streaming_chat.py        # Streaming chat examples
│   ├── parallel_chat.py         # Multi-model parallel chat
│   ├── follow_up_suggestions.py # Chat with follow-up suggestions
│   ├── chat_with_images.py      # Multimodal chat with images
│   └── chat_management.py       # Chat management (rename, metadata, etc.)
├── rag_knowledge/                # RAG and Knowledge Base examples
│   ├── file_rag.py              # RAG with uploaded files
│   ├── knowledge_base.py        # Knowledge base management
│   ├── batch_knowledge_ops.py   # Batch knowledge base operations
│   └── advanced_rag.py          # Advanced RAG features
├── model_management/             # Model management examples
│   ├── list_models.py           # Listing available models
│   ├── model_operations.py      # Create, update, delete models
│   └── model_switching.py       # Switching models in chats
├── notes_api/                    # Notes API examples
│   ├── basic_notes.py           # Basic notes operations
│   └── advanced_notes.py        # Advanced notes management
├── advanced_features/            # Advanced functionality
│   ├── real_time_streaming.py   # Real-time streaming with updates
│   ├── concurrent_operations.py # Concurrent/parallel operations
│   ├── error_handling.py        # Error handling patterns
│   └── custom_tools.py          # Using custom tools
├── comprehensive/                # Complete feature demonstrations
│   ├── full_demo.py             # Comprehensive demo of all features
│   └── use_case_scenarios.py    # Real-world use case examples
└── utils/                        # Utility functions and helpers
    ├── file_helpers.py          # File creation and cleanup utilities
    ├── test_data.py             # Test data generation
    └── example_base.py          # Base class for examples
```

## 🚀 Getting Started

1. **Set up environment variables** (see `config/environment_setup.py`):
   ```bash
   export OUI_BASE_URL="http://localhost:3000"
   export OUI_AUTH_TOKEN="your_api_token_here"
   export OUI_DEFAULT_MODEL="gpt-4.1"
   ```

2. **Start with the basics**:
   ```bash
   python examples/getting_started/hello_world.py
   python examples/getting_started/basic_chat.py
   ```

3. **Explore specific features**:
   ```bash
   python examples/chat_features/streaming_chat.py
   python examples/rag_knowledge/file_rag.py
   python examples/model_management/list_models.py
   ```

## 📋 Example Standards

All examples in this directory follow these standards:

### 🏗️ Structure Standards
- **Consistent imports**: Import order and style
- **Environment handling**: Standardized environment variable usage
- **Error handling**: Proper exception handling and logging
- **Documentation**: Clear docstrings and comments
- **Type hints**: Full type annotations

### 📝 Naming Conventions
- **File names**: `snake_case.py` with descriptive names
- **Function names**: `snake_case` following PEP 8
- **Class names**: `PascalCase` for classes
- **Constants**: `UPPER_SNAKE_CASE` for constants

### 🎯 Code Standards
- **Logging**: Consistent logging setup and usage
- **Configuration**: Environment-based configuration
- **Cleanup**: Proper resource cleanup (files, etc.)
- **Comments**: Meaningful comments explaining complex logic
- **Error messages**: User-friendly error messages

### 📚 Documentation Standards
- **File header**: Purpose, features demonstrated, requirements
- **Function docs**: Clear parameter and return descriptions
- **Usage examples**: How to run and expected output
- **Prerequisites**: Required environment variables and setup

## 🔧 Example Template

Each example follows this template structure:

```python
#!/usr/bin/env python3
"""
Brief description of what this example demonstrates.

Features demonstrated:
- Feature 1
- Feature 2
- Feature 3

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Model availability: specific models if required

Usage:
    python examples/category/example_name.py
"""

import logging
import os
from typing import Optional, Dict, Any

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main function demonstrating the example."""
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        return
    
    # Client initialization
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        return
    
    # Example implementation
    # ... your example code here ...
    
    logger.info("🎉 Example completed successfully")


if __name__ == "__main__":
    main()
```

## 🧪 Running Examples

### Prerequisites
1. Install the package: `pip install openwebui-chat-client`
2. Set environment variables (see `config/environment_setup.py`)
3. Ensure OpenWebUI server is running and accessible

### Environment Variables
- `OUI_BASE_URL`: OpenWebUI server URL (default: http://localhost:3000)
- `OUI_AUTH_TOKEN`: Your OpenWebUI API token
- `OUI_DEFAULT_MODEL`: Default model ID (default: gpt-4.1)
- `OUI_PARALLEL_MODELS`: Comma-separated model IDs for parallel examples
- `OUI_RAG_MODEL`: Model ID for RAG examples

### Common Issues
- **Connection errors**: Ensure OpenWebUI server is running
- **Authentication errors**: Verify your API token is correct
- **Model errors**: Ensure specified models exist in your OpenWebUI instance

## 🆘 Support

For more information and support:
- [Main README](../README.md)
- [API Documentation](../README.md#api-reference)
- [GitHub Issues](https://github.com/Fu-Jie/openwebui-chat-client/issues)