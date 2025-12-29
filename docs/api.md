# API Reference

This page provides the complete API reference for `openwebui-chat-client`, automatically generated from the source code docstrings.

---

## OpenWebUIClient

The main client class for synchronous operations.

::: openwebui_chat_client.OpenWebUIClient
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - chat
        - stream_chat
        - parallel_chat
        - continuous_chat
        - continuous_parallel_chat
        - continuous_stream_chat
        - deep_research
        - process_task
        - stream_process_task
        - rename_chat
        - set_chat_tags
        - update_chat_metadata
        - switch_chat_model
        - list_chats
        - get_chats_by_folder
        - archive_chat
        - archive_chats_by_age
        - delete_all_chats
        - create_folder
        - get_folder_id_by_name
        - move_chat_to_folder
        - list_models
        - list_base_models
        - list_custom_models
        - list_groups
        - get_model
        - create_model
        - update_model
        - delete_model
        - batch_update_model_permissions
        - get_knowledge_base_by_name
        - create_knowledge_base
        - add_file_to_knowledge_base
        - delete_knowledge_base
        - delete_all_knowledge_bases
        - delete_knowledge_bases_by_keyword
        - create_knowledge_bases_with_files
        - get_notes
        - get_notes_list
        - create_note
        - get_note_by_id
        - update_note_by_id
        - delete_note_by_id
        - get_prompts
        - get_prompts_list
        - create_prompt
        - get_prompt_by_command
        - update_prompt_by_command
        - replace_prompt_by_command
        - delete_prompt_by_command
        - search_prompts
        - extract_variables
        - substitute_variables
        - get_system_variables
        - batch_create_prompts
        - batch_delete_prompts
        - get_users
        - get_user_by_id
        - update_user_role
        - delete_user

---

## AsyncOpenWebUIClient

The async client class for asynchronous operations.

::: openwebui_chat_client.AsyncOpenWebUIClient
    options:
      show_root_heading: true
      show_source: false

---

## Return Value Examples

### Chat Operations

```python
{
    "response": "Generated response text",
    "chat_id": "chat-uuid-string",
    "message_id": "message-uuid-string",
    "sources": [...]  # For RAG operations
}
```

### Parallel Chat

```python
{
    "responses": {
        "model-1": "Response from model 1",
        "model-2": "Response from model 2"
    },
    "chat_id": "chat-uuid-string",
    "message_ids": {
        "model-1": "message-uuid-1",
        "model-2": "message-uuid-2"
    }
}
```

### Knowledge Base / Notes

```python
{
    "id": "resource-uuid",
    "name": "Resource Name",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    ...
}
```

### Process Task

```python
{
    "solution": "Final solution text",
    "conversation_history": [...],  # or summarized string
    "todo_list": [
        {"task": "Research topic", "status": "completed"},
        {"task": "Write summary", "status": "completed"}
    ]
}
```

---

## Quick Reference Tables

### Chat Operations

| Method | Description |
|--------|-------------|
| `chat()` | Single-model conversation with optional features |
| `stream_chat()` | Streaming conversation with real-time updates |
| `parallel_chat()` | Multi-model parallel conversation |
| `continuous_chat()` | Continuous conversation with follow-ups |
| `process_task()` | Autonomous multi-step task processing |
| `deep_research()` | Multi-step research agent |

### Chat Management

| Method | Description |
|--------|-------------|
| `rename_chat()` | Rename an existing chat |
| `set_chat_tags()` | Apply tags to a chat |
| `update_chat_metadata()` | Regenerate tags and/or title |
| `switch_chat_model()` | Switch model for existing chat |
| `list_chats()` | Get list of user's chats |
| `archive_chat()` | Archive a specific chat |
| `archive_chats_by_age()` | Bulk archive old chats |
| `create_folder()` | Create a chat folder |

### Model Management

| Method | Description |
|--------|-------------|
| `list_models()` | List available models |
| `list_base_models()` | List base models |
| `list_custom_models()` | List custom models |
| `get_model()` | Get model details |
| `create_model()` | Create a custom model |
| `update_model()` | Update a model |
| `delete_model()` | Delete a model |
| `batch_update_model_permissions()` | Batch update permissions |

### Knowledge Base Operations

| Method | Description |
|--------|-------------|
| `create_knowledge_base()` | Create a knowledge base |
| `add_file_to_knowledge_base()` | Add file to KB |
| `get_knowledge_base_by_name()` | Get KB by name |
| `delete_knowledge_base()` | Delete a KB |
| `delete_all_knowledge_bases()` | Delete all KBs |
| `create_knowledge_bases_with_files()` | Batch create KBs |

### Notes API

| Method | Description |
|--------|-------------|
| `get_notes()` | Get all notes |
| `create_note()` | Create a note |
| `get_note_by_id()` | Get note by ID |
| `update_note_by_id()` | Update a note |
| `delete_note_by_id()` | Delete a note |

### Prompts API

| Method | Description |
|--------|-------------|
| `get_prompts()` | Get all prompts |
| `create_prompt()` | Create a prompt |
| `get_prompt_by_command()` | Get prompt by command |
| `update_prompt_by_command()` | Update a prompt |
| `delete_prompt_by_command()` | Delete a prompt |
| `extract_variables()` | Extract prompt variables |
| `substitute_variables()` | Replace variables |

### User Management

| Method | Description |
|--------|-------------|
| `get_users()` | List users |
| `get_user_by_id()` | Get user details |
| `update_user_role()` | Update user role |
| `delete_user()` | Delete a user |
