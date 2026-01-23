"""
OpenWebUI Chat Client - Modular Architecture

Directory Structure:
====================

modules/
├── chat/                    # Chat core functionality
│   ├── manager.py          : High-level facade coordinating all chat operations
│   ├── api.py              : Raw HTTP communication with OpenWebUI API
│   ├── workflow.py         : 3-step chat flow orchestration (Prepare→Complete→Persist)
│   ├── tasks.py            : Task processing (ReAct loop) & deep research
│   ├── actions.py          : Action triggering for chat messages
│   ├── rag.py              : RAG & file handling utilities
│   ├── parallel.py         : Parallel multi-model chat
│   └── payloads.py         : Payload builders for OpenWebUI schema
│
├── sync/                    # Synchronous managers
│   ├── file_manager.py     : File upload/management
│   ├── knowledge_base_manager.py : Knowledge base CRUD operations
│   ├── model_manager.py    : Model management
│   ├── notes_manager.py    : Notes API operations
│   ├── prompts_manager.py  : Prompts management
│   └── user_manager.py     : User management (admin)
│
└── async_/                  # Asynchronous managers
    ├── async_chat_manager.py           : Async chat operations
    ├── async_file_manager.py           : Async file operations
    ├── async_knowledge_base_manager.py : Async knowledge base operations
    ├── async_model_manager.py          : Async model management
    ├── async_notes_manager.py          : Async notes operations
    ├── async_prompts_manager.py        : Async prompts management
    └── async_user_manager.py           : Async user management

Architecture Principles:
-----------------------
1. Facade Pattern: ChatManager coordinates specialized modules
2. Single Responsibility: Each module has one clear purpose
3. Dependency Injection: Modules receive dependencies via constructors
4. API Isolation: All HTTP calls go through api.py modules
5. Workflow Separation: Business logic separated from HTTP layer
6. Clear Organization: Related modules grouped in subdirectories
"""

# Chat module
from .chat import ChatManager

# Sync managers
from .sync import (
    FileManager,
    KnowledgeBaseManager,
    ModelManager,
    NotesManager,
    PromptsManager,
    UserManager,
)

# Async managers
from .async_ import (
    AsyncChatManager,
    AsyncFileManager,
    AsyncKnowledgeBaseManager,
    AsyncModelManager,
    AsyncNotesManager,
    AsyncPromptsManager,
    AsyncUserManager,
)

__all__ = [
    # Sync Managers
    "ChatManager",
    "FileManager",
    "KnowledgeBaseManager",
    "ModelManager",
    "NotesManager",
    "PromptsManager",
    "UserManager",
    # Async Managers
    "AsyncChatManager",
    "AsyncFileManager",
    "AsyncKnowledgeBaseManager",
    "AsyncModelManager",
    "AsyncNotesManager",
    "AsyncPromptsManager",
    "AsyncUserManager",
]
