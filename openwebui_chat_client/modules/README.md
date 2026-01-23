# OpenWebUI Chat Client - Modules Architecture

## 📁 Directory Structure

```
modules/
├── 💬 Chat Module (Modular Architecture)
│   ├── chat_manager.py       # 🎯 Facade: Coordinates all chat operations
│   ├── chat_api.py           # 🌐 HTTP: Raw API communication
│   ├── chat_workflow.py      # 🔄 Workflow: 3-step chat orchestration
│   ├── chat_tasks.py         # 🤖 Tasks: ReAct loop & deep research
│   ├── chat_actions.py       # ⚡ Actions: Trigger chat message actions
│   ├── chat_rag.py           # 📚 RAG: File handling & context injection
│   ├── chat_parallel.py      # 🔀 Parallel: Multi-model chat
│   └── chat_payloads.py      # 📦 Payloads: OpenWebUI schema builders
│
├── 🔧 Feature Managers (Sync)
│   ├── file_manager.py           # 📎 File uploads
│   ├── knowledge_base_manager.py # 🗃️ Knowledge base CRUD
│   ├── model_manager.py          # 🤖 Model management
│   ├── notes_manager.py          # 📝 Notes API
│   ├── prompts_manager.py        # 💭 Prompts management
│   └── user_manager.py           # 👤 User management (admin)
│
└── ⚡ Feature Managers (Async)
    ├── async_chat_manager.py           # Async chat operations
    ├── async_file_manager.py           # Async file operations
    ├── async_knowledge_base_manager.py # Async KB operations
    ├── async_model_manager.py          # Async model management
    ├── async_notes_manager.py          # Async notes operations
    ├── async_prompts_manager.py        # Async prompts management
    └── async_user_manager.py           # Async user management
```

## 🏗️ Architecture Principles

### 1. **Facade Pattern** (ChatManager)

- **Purpose**: Single entry point for all chat operations
- **Benefits**: Simplified API, loose coupling, easy to extend
- **Example**:

  ```python
  client = OpenWebUIClient(base_url, token, model)
  # ChatManager coordinates:
  result = client.chat("Hello")  
  # → ChatWorkflow.execute_full_turn()
  # → ChatAPI.completion()
  # → ChatAPI.update_chat()
  ```

### 2. **Single Responsibility**

- **ChatAPI**: Only HTTP communication
- **ChatWorkflow**: Only business logic orchestration
- **ChatTasks**: Only task processing & research
- **ChatActions**: Only action triggering

### 3. **Dependency Injection**

```python
class ChatManager(BaseManager):
    def __init__(self, base_client: BaseClient):
        self._api = ChatAPI(base_client)          # Injected
        self._workflow = ChatWorkflow(self._api)  # Injected
        self._tasks = ChatTasks(self)             # Injected
```

### 4. **API Isolation**

- All HTTP calls go through `*_api.py` modules
- Business logic never directly calls `requests`
- Easy to mock for testing

### 5. **Workflow Separation**

- HTTP layer (ChatAPI) separate from business logic (ChatWorkflow)
- Easy to swap implementations
- Clear error boundaries

## 📋 Module Responsibilities

### Chat Module Components

| Module | Responsibility | Key Methods |
|--------|---------------|-------------|
| `chat_manager.py` | 🎯 Facade & coordination | `chat()`, `stream_chat()`, `process_task()` |
| `chat_api.py` | 🌐 HTTP communication | `completion()`, `completed()`, `update_chat()` |
| `chat_workflow.py` | 🔄 3-step orchestration | `execute_full_turn()` |
| `chat_tasks.py` | 🤖 Advanced AI tasks | `process_task()`, `_perform_research_step()` |
| `chat_actions.py` | ⚡ Action execution | `trigger_action()` |
| `chat_rag.py` | 📚 RAG utilities | `encode_image()`, `build_rag_payload()` |
| `chat_parallel.py` | 🔀 Multi-model chat | `parallel_chat()` |
| `chat_payloads.py` | 📦 Payload builders | `build_user_message()`, `build_chat_payload()` |

### Feature Managers

| Manager | Purpose | Async Version |
|---------|---------|---------------|
| `file_manager.py` | File upload & management | `async_file_manager.py` |
| `knowledge_base_manager.py` | KB CRUD operations | `async_knowledge_base_manager.py` |
| `model_manager.py` | Model management | `async_model_manager.py` |
| `notes_manager.py` | Notes API | `async_notes_manager.py` |
| `prompts_manager.py` | Prompts management | `async_prompts_manager.py` |
| `user_manager.py` | User admin operations | `async_user_manager.py` |

## 🔗 Data Flow

### Standard Chat Flow

```
User Request
    ↓
ChatManager.chat()
    ↓
ChatWorkflow.execute_full_turn()
    ↓
    ├─→ Step 1: ChatAPI.completion() [Generate response]
    ├─→ Step 2: ChatAPI.completed() [Apply filters]
    └─→ Step 3: ChatAPI.update_chat() [Persist to DB]
    ↓
Return ChatResult
```

### Task Processing Flow (ReAct)

```
User Task
    ↓
ChatManager.process_task()
    ↓
ChatTasks.process_task()
    ↓
Loop (max_iterations):
    ├─→ Get model completion
    ├─→ Parse thought/action/observation
    ├─→ Check for final answer
    ├─→ Execute tools if needed
    └─→ Update todo list
    ↓
Return final solution
```

### Deep Research Flow

```
Research Topic
    ↓
OpenWebUIClient.deep_research()
    ↓
ChatManager._perform_research_step() (delegated to ChatTasks)
    ↓
For each step:
    ├─→ Plan: What question to ask?
    ├─→ Route: Which model type (general/search)?
    ├─→ Execute: Get answer
    └─→ Accumulate: Add to research history
    ↓
Generate final report
```

## 🧪 Testing Strategy

### Unit Tests

- Test each module independently
- Mock dependencies via dependency injection
- Focus on business logic correctness

### Integration Tests

- Test module interactions
- Use real OpenWebUI API (when available)
- Verify end-to-end workflows

### Example Test Structure

```python
# Unit test: ChatWorkflow
def test_execute_full_turn():
    mock_api = Mock(spec=ChatAPI)
    workflow = ChatWorkflow(mock_api)
    
    result = workflow.execute_full_turn("Hello", chat_id="123")
    
    mock_api.completion.assert_called_once()
    mock_api.completed.assert_called_once()
    mock_api.update_chat.assert_called_once()
```

## 📝 Migration Notes

### From Mixin Architecture to Modular

**Before** (Mixin Hell):

```python
class ChatManager(
    ModelAccessMixin,
    ChatCoreMixin,
    ChatActionsMixin,
    ChatFoldersMixin,
    ChatMetadataMixin,
    ChatOperationsMixin,
    ChatPlaceholdersMixin,
    ChatQueriesMixin,
    TaskProcessingMixin,
    BaseManager
):
    # 100+ methods mixed together
    pass
```

**After** (Clean Facade):

```python
class ChatManager(BaseManager):
    def __init__(self, base_client):
        self._api = ChatAPI(base_client)
        self._workflow = ChatWorkflow(self._api)
        self._tasks = ChatTasks(self)
        self._actions = ChatActions(self)
    
    def chat(self, question, **kwargs):
        return self._workflow.execute_full_turn(question, **kwargs)
    
    def process_task(self, question, **kwargs):
        return self._tasks.process_task(question, **kwargs)
```

### Benefits

✅ **Clarity**: Each module has a single, clear purpose  
✅ **Maintainability**: Easy to locate and modify code  
✅ **Testability**: Modules can be tested independently  
✅ **Extensibility**: New features added to dedicated modules  
✅ **Debugging**: Clear boundaries make issues easier to trace  

## 🚀 Adding New Features

### Step 1: Identify Module

- HTTP operation? → Add to `chat_api.py`
- Business logic? → Add to `chat_workflow.py`
- Advanced AI feature? → Add to `chat_tasks.py`
- New feature category? → Create new module

### Step 2: Implement

```python
# Example: Adding a new action type
# File: chat_actions.py

class ChatActions:
    def trigger_custom_action(self, action_id, chat_id, params):
        # Implementation
        pass
```

### Step 3: Expose via Facade

```python
# File: chat_manager.py

class ChatManager:
    def trigger_custom_action(self, action_id, chat_id, params):
        return self._actions.trigger_custom_action(action_id, chat_id, params)
```

### Step 4: Document & Test

- Add docstring explaining the feature
- Write unit tests for the module
- Add integration test if needed
- Update this README

## 📚 References

- **OpenWebUI API Docs**: [github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)
- **Architecture Patterns**: Facade, Dependency Injection, Separation of Concerns
- **Python Best Practices**: PEP 8, Type Hints, Logging
