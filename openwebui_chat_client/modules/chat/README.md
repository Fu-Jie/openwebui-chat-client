# Chat Module - Complete Documentation

## 📚 Overview

The **Chat Module** is the core component of openwebui-chat-client that provides complete, production-ready chat functionality following the official Open WebUI backend implementation. It handles everything from message construction to API communication and workflow orchestration.

### Module Architecture

```
chat/
├── api.py          # HTTP API Layer (48 methods) - Direct backend endpoints
├── payloads.py     # Payload Builders (11 methods) - Data structure construction  
├── workflow.py     # Workflow Orchestrator (3-step flow) - High-level operations
├── tasks.py        # Background Tasks (7 methods) - Post-completion processing
├── types.py        # Type Definitions - TypedDict structures
├── manager.py      # Chat Manager - User-facing interface
├── actions.py      # Chat Actions - Convenience methods
├── rag.py          # RAG Integration - Knowledge retrieval
└── parallel.py     # Parallel Chat - Multi-model conversations
```

### Design Philosophy

1. **Official Compatibility**: Every API call, payload structure, and workflow step matches the official Open WebUI backend exactly
2. **Type Safety**: Comprehensive TypedDict definitions prevent runtime errors
3. **Error Resilience**: Detailed error handling with automatic retries and graceful degradation
4. **Layered Architecture**: Clear separation between API, payloads, workflows, and user-facing interfaces
5. **Documentation First**: Every method includes usage examples, parameter explanations, and official backend references

---

## 🏗️ Architecture Layers

### Layer 1: Type Definitions (types.py)

Defines all data structures using TypedDict for type safety:

```python
from .types import (
    MessageDict,      # Single message structure
    ChatDict,         # Complete chat object
    ChatHistoryDict,  # Message tree structure
    CompletionPayloadDict,  # API request format
    ResponseDict,     # API response format
)
```

**Key Types:**

- **MessageDict**: Message with role, content, parentId, childrenIds (forms tree)
- **ChatHistoryDict**: `{currentId, messages}` - graph-based history
- **ChatBodyDict**: Inner chat object (title, history, models, params)
- **ChatFormDict**: Full chat creation/update payload

### Layer 2: Payload Builders (payloads.py)

Constructs official Open WebUI data structures:

```python
from openwebui_chat_client.modules.chat.payloads import ChatPayloads

# Build user message
user_msg = ChatPayloads.build_user_message(
    content="What is Python?",
    model="gpt-4.1"
)

# Build assistant response
assistant_msg = ChatPayloads.build_assistant_message(
    content="Python is a programming language...",
    model="gpt-4.1",
    parent_id=user_msg["id"],
    done=True
)

# Build complete chat payload
payload = ChatPayloads.build_chat_payload(
    title="Python Discussion",
    messages=[user_msg, assistant_msg],
    current_id=assistant_msg["id"],
    models=["gpt-4.1"]
)
```

**11 Builder Methods:**

1. `build_message()` - Generic message builder
2. `build_user_message()` - User message shortcut
3. `build_assistant_message()` - Assistant message shortcut
4. `build_system_message()` - System message shortcut
5. `build_chat_history()` - Message tree structure
6. `build_chat_object()` - Inner chat object
7. `build_chat_payload()` - Complete chat form
8. `build_completion_payload()` - Completion request
9. `build_completed_payload()` - Completion finalization
10. `convert_to_openai_format()` - OpenAI API format conversion
11. `add_child_to_parent()` - Tree structure maintenance

### Layer 3: API Layer (api.py)

Direct HTTP interface to Open WebUI backend:

```python
from openwebui_chat_client.modules.chat.api import ChatAPI

# Initialize
chat_api = ChatAPI(base_client)

# Core operations
response = chat_api.completion(payload)         # Generate response
stream = chat_api.stream_completion(payload)    # Streaming response
result = chat_api.completed(payload)            # Finalize completion

# CRUD operations
chat = chat_api.create_chat(payload)            # Create new chat
chat = chat_api.get_chat(chat_id)               # Retrieve chat
chat = chat_api.update_chat(chat_id, payload)   # Update chat
success = chat_api.delete_chat(chat_id)         # Delete chat

# List operations
chats = chat_api.list_chats(page=1)             # List chats
chats = chat_api.search_chats("python")         # Search chats
chats = chat_api.get_archived_chats()           # Archived chats

# State management
chat_api.pin_chat(chat_id)                      # Toggle pin
chat_api.archive_chat(chat_id)                  # Toggle archive
chat_api.clone_chat(chat_id, title)             # Clone chat
chat_api.share_chat(chat_id)                    # Create share link
```

**48 API Methods by Category:**

#### Core Chat Completion (3 methods)

- `completion()` - Main completion endpoint
- `stream_completion()` - Streaming variant
- `completed()` - Post-completion finalization

#### Chat CRUD (4 methods)

- `create_chat()` - Create new chat
- `get_chat()` - Retrieve single chat
- `update_chat()` - Update existing chat
- `delete_chat()` - Delete chat

#### Chat List & Query (6 methods)

- `list_chats()` - Paginated list
- `get_all_chats()` - All user chats
- `search_chats()` - Text search
- `get_archived_chats()` - Archived only
- `get_pinned_chats()` - Pinned only
- `delete_all_chats()` - Bulk delete

#### Chat State Management (8 methods)

- `pin_chat()` / `get_pinned_status()`
- `archive_chat()` / `archive_all_chats()` / `unarchive_all_chats()`
- `clone_chat()` / `clone_shared_chat()`
- `share_chat()` / `unshare_chat()` / `get_shared_chat()`

#### Chat Metadata (10 methods)

- `get_chat_tags()` / `add_chat_tag()` / `delete_chat_tag()` / `delete_all_chat_tags()`
- `get_all_user_tags()` / `get_chats_by_tag()`
- `set_chat_folder()` / `get_chats_by_folder()` / `get_chat_list_by_folder()`

#### Import/Export & Folders (4 methods)

- `import_chats()` - Bulk import
- `create_folder()` / `list_folders()`
- `upload_file()` - File attachment

### Layer 4: Workflow Orchestrator (workflow.py)

High-level multi-step operations following official Open WebUI flow:

```python
from openwebui_chat_client.modules.chat.workflow import ChatWorkflow

# Initialize
workflow = ChatWorkflow(chat_api)

# Execute complete chat turn
result = workflow.execute_full_turn(
    question="What is machine learning?",
    model="gpt-4.1",
    chat_id=None,  # Creates new chat if None
    stream=False,
    tool_ids=["web_search"],
    files=[{"id": "file-123", "name": "doc.pdf"}]
)

if result and result["success"]:
    print(f"Chat ID: {result['chat_id']}")
    print(f"Response: {result['assistant_message']['content']}")
    print(f"Title: {result.get('chat_state', {}).get('title')}")
```

**3-Step Official Workflow:**

```
┌──────────────────────────────────────────────────────────────┐
│ Step 1: Completion Request                                   │
│ POST /api/chat/completions                                    │
│                                                               │
│ ┌──────────────┐                                             │
│ │ User Input   │                                             │
│ │ - Question   │                                             │
│ │ - Files      │                                             │
│ │ - Tools      │                                             │
│ └───────┬──────┘                                             │
│         │                                                     │
│         ▼                                                     │
│ ┌──────────────────────────────┐                             │
│ │ Metadata Preparation          │                             │
│ │ - Generate message IDs        │                             │
│ │ - Build message tree          │                             │
│ │ - Attach files/tools          │                             │
│ └───────┬──────────────────────┘                             │
│         │                                                     │
│         ▼                                                     │
│ ┌──────────────────────────────┐                             │
│ │ Completion Request            │                             │
│ │ - Call model provider         │                             │
│ │ - Process tools if needed     │                             │
│ │ - Apply RAG if configured     │                             │
│ └───────┬──────────────────────┘                             │
│         │                                                     │
│         ▼                                                     │
│ ┌──────────────────────────────┐                             │
│ │ Response                      │                             │
│ │ - Assistant message           │                             │
│ │ - Usage statistics            │                             │
│ │ - Sources/citations           │                             │
│ └───────┬──────────────────────┘                             │
└─────────┼──────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 2: Completed (Background Tasks)                         │
│ POST /api/chat/completed                                      │
│                                                               │
│ ┌──────────────────────────────┐                             │
│ │ Outlet Filters                │                             │
│ │ - Content filtering           │                             │
│ │ - Moderation checks           │                             │
│ └───────┬──────────────────────┘                             │
│         │                                                     │
│         ▼                                                     │
│ ┌──────────────────────────────┐                             │
│ │ Background Tasks (Parallel)   │                             │
│ │                               │                             │
│ │ ┌──────────────────────┐     │                             │
│ │ │ Title Generation     │     │                             │
│ │ │ (first turn only)    │     │                             │
│ │ └──────────────────────┘     │                             │
│ │                               │                             │
│ │ ┌──────────────────────┐     │                             │
│ │ │ Tags Extraction      │     │                             │
│ │ └──────────────────────┘     │                             │
│ │                               │                             │
│ │ ┌──────────────────────┐     │                             │
│ │ │ Follow-up Questions  │     │                             │
│ │ └──────────────────────┘     │                             │
│ └───────┬──────────────────────┘                             │
│         │                                                     │
│         ▼                                                     │
│ ┌──────────────────────────────┐                             │
│ │ Metadata Updates              │                             │
│ │ - Title, tags, follow-ups     │                             │
│ └───────┬──────────────────────┘                             │
└─────────┼──────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: Persist Chat State                                   │
│ POST /api/v1/chats/{id}                                       │
│                                                               │
│ ┌──────────────────────────────┐                             │
│ │ Build Complete Chat           │                             │
│ │ - User message                │                             │
│ │ - Assistant message           │                             │
│ │ - Update history tree         │                             │
│ │ - Update currentId            │                             │
│ └───────┬──────────────────────┘                             │
│         │                                                     │
│         ▼                                                     │
│ ┌──────────────────────────────┐                             │
│ │ Save to Database              │                             │
│ │ - Update chat object          │                             │
│ │ - Update metadata             │                             │
│ │ - Index for search            │                             │
│ └───────┬──────────────────────┘                             │
│         │                                                     │
│         ▼                                                     │
│ ┌──────────────────────────────┐                             │
│ │ Final Chat State              │                             │
│ │ - Complete chat object        │                             │
│ │ - All messages preserved      │                             │
│ │ - Metadata attached           │                             │
│ └──────────────────────────────┘                             │
└──────────────────────────────────────────────────────────────┘
```

**Workflow Methods:**

- `execute_full_turn()` - Complete 3-step workflow
- `execute_streaming_turn()` - Streaming variant (WebSocket-based)
- `_init_new_chat()` - Helper for chat creation

### Layer 5: Background Tasks (tasks.py)

Post-completion processing and tool calling:

```python
from openwebui_chat_client.modules.chat.tasks import ChatTasks

# Initialize
chat_tasks = ChatTasks(chat_manager)

# Execute background tasks
results = chat_tasks.execute_background_tasks(
    chat_id="chat-123",
    message_id="msg-456",
    messages=message_history,
    model_id="gpt-4.1",
    tasks_config={
        "TITLE_GENERATION": True,
        "TAGS_GENERATION": True,
        "FOLLOW_UP_GENERATION": True
    }
)

print(results)
# {
#     "title": "Discussion about Python",
#     "tags": ["Python", "Programming", "Tutorial"],
#     "follow_ups": [
#         "Can you explain classes in Python?",
#         "What are decorators?",
#         "How does Python compare to Java?"
#     ]
# }

# ReAct tool calling workflow
result = chat_tasks.process_task_with_tools(
    question="Calculate 15% tip on $45.50",
    model_id="gpt-4.1",
    tool_ids=["calculator"],
    max_iterations=25
)
```

**Background Task Types:**

1. **Title Generation**: Auto-generate chat title from first 2 messages
2. **Tags Extraction**: Extract relevant tags for categorization
3. **Follow-up Suggestions**: Generate contextual follow-up questions
4. **Image Generation**: Generate images if requested in chat

**Tool Calling (ReAct Pattern):**

```
┌─────────────────────────────────────────────────┐
│ ReAct Loop (Repeat until solution or max iter)  │
│                                                  │
│  ┌────────────────┐                             │
│  │ 1. THOUGHT     │  Analyze task, plan action  │
│  └───────┬────────┘                             │
│          │                                       │
│          ▼                                       │
│  ┌────────────────┐                             │
│  │ 2. ACTION      │  Call tool if needed        │
│  └───────┬────────┘                             │
│          │                                       │
│          ▼                                       │
│  ┌────────────────┐                             │
│  │ 3. OBSERVATION │  Review tool result         │
│  └───────┬────────┘                             │
│          │                                       │
│          └──────> Repeat or final answer        │
│                                                  │
│  ┌────────────────┐                             │
│  │ FINAL ANSWER   │  Solution ready             │
│  └────────────────┘                             │
└─────────────────────────────────────────────────┘
```

**7 Task Methods:**

- `execute_background_tasks()` - Run all background tasks
- `_generate_title()` - Title generation logic
- `_generate_tags()` - Tags extraction logic
- `_generate_follow_ups()` - Follow-up suggestions logic
- `process_task_with_tools()` - ReAct loop orchestrator
- `_execute_tool_calls()` - Tool execution handler
- `_get_react_system_prompt()` - ReAct system prompt

---

## 📖 Usage Patterns

### Pattern 1: Simple Chat Interaction

```python
from openwebui_chat_client import OpenWebUIClient

# Initialize client
client = OpenWebUIClient(
    base_url="http://localhost:3000",
    auth_token="your-token",
    default_model="gpt-4.1"
)

# Simple chat (automatic workflow)
result = client.chat(
    question="What is Python?",
    chat_title="Python Tutorial"
)

if result:
    print(result["response"])
```

### Pattern 2: Streaming Chat

```python
# Streaming response
for chunk in client.stream_chat(
    question="Write a long story about AI",
    chat_title="AI Story"
):
    print(chunk, end="", flush=True)
```

### Pattern 3: Multi-Model Parallel Chat

```python
# Compare responses from multiple models
results = client.parallel_chat(
    question="Explain quantum computing",
    model_ids=["gpt-4.1", "gemini-2.5-flash", "claude-3"],
    chat_title="Quantum Computing"
)

for model, response in results.items():
    print(f"\n{model}:")
    print(response)
```

### Pattern 4: Chat with Files (Multimodal)

```python
# Upload file
file_dict = client.upload_file("diagram.png")

# Chat with file reference
result = client.chat(
    question="Describe this diagram",
    files=[file_dict],
    model="gpt-4.1"
)
```

### Pattern 5: Chat with Knowledge Base (RAG)

```python
# Create knowledge base
kb = client.create_knowledge_base(
    name="Python Docs",
    files=["python_tutorial.pdf", "api_reference.pdf"]
)

# Chat with RAG
result = client.chat(
    question="How do I use asyncio?",
    knowledge_base_id=kb["id"],
    model="gpt-4.1"
)
```

### Pattern 6: Chat with Tools

```python
# Chat with tools enabled
result = client.chat(
    question="Search for latest Python news and summarize",
    tool_ids=["web_search", "summarizer"],
    model="gpt-4.1"
)

# Check if tools were used
if result.get("tool_calls"):
    print("Tools used:")
    for call in result["tool_calls"]:
        print(f"  - {call['function']['name']}")
```

### Pattern 7: Manual Workflow Control

```python
from openwebui_chat_client.modules.chat.api import ChatAPI
from openwebui_chat_client.modules.chat.payloads import ChatPayloads
from openwebui_chat_client.core.base_client import BaseClient

# Initialize layers
base_client = BaseClient(base_url, auth_token)
chat_api = ChatAPI(base_client)

# Step 1: Build payloads manually
user_msg = ChatPayloads.build_user_message(
    content="Hello",
    model="gpt-4.1"
)

completion_payload = ChatPayloads.build_completion_payload(
    model="gpt-4.1",
    messages=[user_msg],
    stream=False
)

# Step 2: Get completion
response = chat_api.completion(completion_payload)

# Step 3: Extract assistant message
assistant_content = response["choices"][0]["message"]["content"]
assistant_msg = ChatPayloads.build_assistant_message(
    content=assistant_content,
    model="gpt-4.1",
    parent_id=user_msg["id"]
)

# Step 4: Create chat with history
chat_payload = ChatPayloads.build_chat_payload(
    title="Manual Chat",
    messages=[user_msg, assistant_msg],
    current_id=assistant_msg["id"],
    models=["gpt-4.1"]
)

chat = chat_api.create_chat(chat_payload)
print(f"Created chat: {chat['id']}")
```

---

## 🔍 Message Tree Structure Deep Dive

### Understanding the Graph-Based History

Open WebUI uses a **directed acyclic graph (DAG)** for message history, not a simple list. This enables:

- **Branching**: Edit/regenerate creates alternative responses
- **Version control**: All conversation paths preserved
- **Time travel**: Navigate different conversation branches

### Tree Structure Example

```
Initial conversation:
┌──────────┐
│  User 1  │ (id: u1, parentId: null)
└────┬─────┘
     │
     ▼
┌──────────┐
│  Asst 1  │ (id: a1, parentId: u1)
└────┬─────┘
     │
     ▼
┌──────────┐
│  User 2  │ (id: u2, parentId: a1)
└────┬─────┘
     │
     ▼
┌──────────┐
│  Asst 2  │ (id: a2, parentId: u2) ← currentId
└──────────┘

After regenerating Asst 2:
┌──────────┐
│  User 1  │
└────┬─────┘
     │
     ▼
┌──────────┐
│  Asst 1  │
└────┬─────┘
     │
     ▼
┌──────────┐
│  User 2  │
└────┬─────┘
     │
     ├──────────────────┐
     │                  │
     ▼                  ▼
┌──────────┐      ┌──────────┐
│ Asst 2A  │      │ Asst 2B  │ ← currentId (active branch)
└──────────┘      └──────────┘
(inactive)        (active)

user2.childrenIds = [a2a, a2b]
```

### Python Code for Tree Navigation

```python
def get_active_branch(history: ChatHistoryDict) -> List[MessageDict]:
    """Extract active conversation branch from history."""
    messages = history["messages"]
    current_id = history["currentId"]
    
    # Walk backwards from currentId to root
    branch = []
    msg_id = current_id
    
    while msg_id:
        msg = messages.get(msg_id)
        if not msg:
            break
        branch.append(msg)
        msg_id = msg.get("parentId")
    
    # Reverse to get chronological order
    return list(reversed(branch))

# Usage
active_messages = get_active_branch(chat["chat"]["history"])
for msg in active_messages:
    print(f"{msg['role']}: {msg['content']}")
```

---

## ⚙️ Configuration and Best Practices

### Error Handling

All methods follow consistent error handling:

```python
# All API methods return None on failure
result = chat_api.get_chat("invalid-id")
if result is None:
    # Check logs for detailed error
    logger.error("Chat retrieval failed")
else:
    # Success path
    print(result["title"])
```

### Logging Configuration

```python
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,  # INFO for operations, DEBUG for payloads
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Module-specific logging
logging.getLogger("openwebui_chat_client.modules.chat").setLevel(logging.DEBUG)
```

### Retry Logic

API layer implements automatic retries for transient errors:

```python
# Automatic retries (completion endpoint)
max_retries = 3
retry_delay = 1.0  # Exponential backoff

# Customize in your own wrapper
def completion_with_custom_retry(payload, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return chat_api.completion(payload)
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### Performance Optimization

```python
# 1. Use streaming for long responses
stream = chat_api.stream_completion(payload)

# 2. Paginate large lists
chats = chat_api.list_chats(page=1)  # 60 items per page

# 3. Cache frequently accessed chats
chat_cache = {}
def get_cached_chat(chat_id):
    if chat_id not in chat_cache:
        chat_cache[chat_id] = chat_api.get_chat(chat_id)
    return chat_cache[chat_id]

# 4. Batch operations when possible
results = chat_tasks.execute_background_tasks(...)  # Parallel execution
```

---

## 🔗 Integration with Open WebUI Backend

### Official Backend Mappings

| Client Module | Backend File | Purpose |
|---------------|-------------|---------|
| `api.py` | `routers/chats.py` | Chat CRUD endpoints |
| `api.py:completion()` | `main.py:chat_completion()` | Completion endpoint |
| `payloads.py` | `models/chats.py` | Data structures |
| `workflow.py` | `utils/middleware.py` | Multi-step processing |
| `tasks.py` | `routers/tasks.py` | Background tasks |
| `rag.py` | `utils/rag.py` | RAG integration |

### Backend Version Compatibility

- **Tested with**: Open WebUI v0.3.x and v0.4.x
- **API Version**: v1 (stable)
- **Breaking Changes**: Check CHANGELOG for backend updates

### Custom Backend Deployments

```python
# For custom Open WebUI deployments
client = OpenWebUIClient(
    base_url="https://your-custom-domain.com",  # Your deployment
    auth_token="your-api-token",
    default_model="your-default-model"
)
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Chat not found" Error

```python
# Check chat ownership
chats = chat_api.list_chats()
chat_ids = [c["id"] for c in chats]
if chat_id not in chat_ids:
    print("Chat doesn't belong to current user")
```

#### 2. Invalid Message Structure

```python
# Validate message before using
def validate_message(msg):
    required = ["id", "role", "content", "timestamp"]
    return all(field in msg for field in required)

if not validate_message(my_message):
    raise ValueError("Invalid message structure")
```

#### 3. Completion Timeout

```python
# Increase timeout in base client
base_client = BaseClient(
    base_url=base_url,
    auth_token=token,
    timeout=300  # 5 minutes
)
```

#### 4. Streaming Connection Drops

```python
# Handle stream interruption
try:
    for chunk in chat_api.stream_completion(payload):
        process_chunk(chunk)
except requests.exceptions.ChunkedEncodingError:
    logger.error("Stream interrupted, retrying...")
    # Retry or fall back to non-streaming
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger("openwebui_chat_client").setLevel(logging.DEBUG)

# Or use environment variable
import os
os.environ["OICLIENT_DEBUG"] = "1"
```

---

## 📚 Additional Resources

### Documentation Files

- `CHATMANAGER_PHASE2_COMPLETION.md` - ChatManager refactoring details
- `CHATMANAGER_REFACTORING_PLAN.md` - Architecture decisions
- `ERROR_HANDLING_SUMMARY.md` - Error handling patterns
- `CHAT_TYPES_COMPLETION_REPORT.md` - Type system documentation

### Official Open WebUI References

- Backend Codebase: <https://github.com/open-webui/open-webui>
- API Documentation: <https://docs.openwebui.com>
- Community Discord: <https://discord.gg/openwebui>

### Related Modules

- `models/` - Model management
- `knowledge/` - Knowledge base operations
- `files/` - File handling
- `tools/` - Tool integration

---

## 🎯 Quick Reference Card

### Essential Imports

```python
from openwebui_chat_client import OpenWebUIClient
from openwebui_chat_client.modules.chat.api import ChatAPI
from openwebui_chat_client.modules.chat.payloads import ChatPayloads
from openwebui_chat_client.modules.chat.workflow import ChatWorkflow
from openwebui_chat_client.modules.chat.tasks import ChatTasks
```

### Essential Methods

```python
# High-level (via OpenWebUIClient)
client.chat(question, chat_title)
client.stream_chat(question, chat_title)
client.parallel_chat(question, model_ids)

# API Layer
chat_api.completion(payload)
chat_api.create_chat(payload)
chat_api.get_chat(chat_id)
chat_api.update_chat(chat_id, payload)

# Payload Builders
ChatPayloads.build_user_message(content, model)
ChatPayloads.build_chat_payload(title, messages, current_id)

# Workflow
workflow.execute_full_turn(question, model, chat_id)

# Tasks
tasks.execute_background_tasks(chat_id, message_id, messages, model_id)
```

---

## 📝 License and Contributing

This module is part of openwebui-chat-client licensed under MIT License.

**Contributing Guidelines:**

1. Follow existing code style (Black, Ruff, mypy)
2. Add comprehensive docstrings (Google style)
3. Include usage examples in docstrings
4. Reference official backend code
5. Write tests for new functionality
6. Update this README for major changes

**Questions or Issues?**

- GitHub Issues: <https://github.com/fu-jie/openwebui-chat-client/issues>
- Discussions: <https://github.com/fu-jie/openwebui-chat-client/discussions>

---

*Last Updated: 2026-01-23*
*Module Version: See `__init__.py` for version*
