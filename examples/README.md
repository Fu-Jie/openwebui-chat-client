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
│   ├── async_basic_chat.py      # Async client basic functionality
│   └── quick_start.py           # Quick start guide with multiple features
├── chat_features/                # Chat-related functionality
│   ├── streaming_chat.py        # Streaming chat examples
│   ├── async_streaming_chat.py  # Async streaming chat examples
│   ├── model_switching.py       # Switching models in chats
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
│   ├── async_model_operations.py # Async model management
│   └── model_switching.py       # Legacy: Use chat_features/model_switching.py instead
├── notes_api/                    # Notes API examples
│   ├── basic_notes.py           # Basic notes operations
│   └── advanced_notes.py        # Advanced notes management
├── prompts_api/                  # Prompts API examples
│   ├── basic_prompts.py         # Basic prompts CRUD operations
│   ├── advanced_prompts.py      # Advanced prompts with variables
│   └── README.md                # Detailed prompts usage guide
├── advanced_features/            # Advanced functionality
│   ├── continuous_conversation.py # Multi-turn conversations with follow-ups
│   ├── deep_research_example.py # Autonomous research agent
│   ├── process_task_example.py  # Multi-step task processing agent
│   ├── stream_process_task_example.py # Streaming task processing
│   ├── archive_chats.py         # Chat archiving functionality
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
   
   # Optional: Clean up all chats before running examples (default: false)
   export OUI_CLEANUP_BEFORE_TEST="true"
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
   python examples/prompts_api/basic_prompts.py
   ```

## 📂 Example Categories

### 🗨️ Prompts API (`prompts_api/`)

Create and manage custom prompt templates with variable substitution:

- **`basic_prompts.py`**: CRUD operations, variable extraction/substitution, search functionality
- **`advanced_prompts.py`**: Interactive forms, dynamic prompt creation, chat integration
- **Key Features**: Variable types (text, select, date, etc.), system variables, batch operations

### 💬 Chat Features (`chat_features/`)

Core conversation functionality:

- **`basic_chat.py`**: Simple single-model conversations
- **`streaming_chat.py`**: Real-time streaming responses
- **`async_streaming_chat.py`**: Async streaming with timing analysis and concurrency
- **`parallel_chat.py`**: Multi-model parallel conversations
- **`model_switching.py`**: Switching models within existing chats

### 📚 RAG & Knowledge (`rag_knowledge/`)

Retrieval-Augmented Generation and knowledge management:

- **`file_rag.py`**: RAG with uploaded files
- **`knowledge_base.py`**: Knowledge base CRUD operations
- **`batch_knowledge_ops.py`**: Bulk knowledge base management

### 🤖 Model Management (`model_management/`)

Model configuration and management:

- **`list_models.py`**: Enumerate available models
- **`model_operations.py`**: Create, update, delete custom models
- **`async_model_operations.py`**: Async model listing, categorization, and statistics
- **`batch_permissions.py`**: Bulk permission management

### 📝 Notes API (`notes_api/`)

Structured note management:

- **`basic_notes.py`**: Note CRUD operations with metadata
- **`advanced_notes.py`**: Advanced note management patterns

### 🔬 Advanced Features (`advanced_features/`)

Advanced autonomous agents and multi-step processing:

- **`continuous_conversation.py`**: Multi-turn conversations with automatic follow-up suggestions
- **`deep_research_example.py`**: Autonomous research agent with intelligent model routing
- **`process_task_example.py`**: Multi-step task processing with agentic loop (tool use)
- **`stream_process_task_example.py`**: Streaming version of task processing with real-time updates
- **`archive_chats.py`**: Automated chat archiving by age and folder
- **Key Features**: Autonomous reasoning, tool integration, iterative problem-solving, streaming updates

### 🚀 Getting Started (`getting_started/`)

Entry-level examples for new users:

- **`hello_world.py`**: Minimal example
- **`basic_chat.py`**: Core chat functionality (sync client)
- **`async_basic_chat.py`**: Async client with asyncio support, concurrent operations, streaming
- **`quick_start.py`**: Multi-feature demonstration

### 🌐 Integration Smoke Tests (`integration/`)

Env-gated live smoke tests (require `OUI_BASE_URL` and `OUI_AUTH_TOKEN`):

- **`test_integration_async_client_live.py`**: Async client live basics (list_models + chat)
- **`test_integration_async_stream_chat.py`**: Async streaming chat live
- **`test_integration_async_model_ops.py`**: Async model list and detail fetch
- **`test_integration_sync_stream_chat.py`**: Sync streaming chat live
- **`test_integration_openwebui_chat_client.py`**: Sync client live (chat + model CRUD; may skip on restricted servers)

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

- `OUI_BASE_URL`: OpenWebUI server URL (default: <http://localhost:3000>)
- `OUI_AUTH_TOKEN`: Your OpenWebUI API token
- `OUI_DEFAULT_MODEL`: Default model ID (default: gpt-4.1)
- `OUI_TOOL_SERVER_ID`: Tool server ID for process_task examples (optional)
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
