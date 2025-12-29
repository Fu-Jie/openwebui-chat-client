# User Guide

This guide covers the main features and usage patterns of the `openwebui-chat-client` library.

---

## Basic Usage

### Initializing the Client

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)
```

### Simple Chat

```python
result = client.chat(
    question="What is the capital of France?",
    chat_title="Geography Questions"
)

if result:
    print(f"Response: {result['response']}")
    print(f"Chat ID: {result['chat_id']}")
    print(f"Message ID: {result['message_id']}")
```

---

## Chat Features

### Parallel Model Chat

Query multiple models simultaneously and compare their responses:

```python
result = client.parallel_chat(
    question="Explain quantum computing in simple terms.",
    chat_title="AI Model Comparison",
    model_ids=["gpt-4.1", "gemini-2.5-flash"],
    folder_name="Technical Comparisons"
)

if result and result.get("responses"):
    for model, response in result["responses"].items():
        print(f"--- {model} ---")
        print(response)
        print()
```

### Streaming Chat

Get real-time responses with a typewriter effect:

```python
stream = client.stream_chat(
    question="Tell me a short story about a robot.",
    chat_title="Creative Writing"
)

for chunk in stream:
    print(chunk, end="", flush=True)
print()  # New line at the end
```

### Chat with Images (Multimodal)

Send images along with your text prompt:

```python
result = client.chat(
    question="What do you see in this image?",
    chat_title="Image Analysis",
    model_id="gpt-4.1",
    image_paths=["./my_image.png"]
)

if result:
    print(result['response'])
```

### Chat with Tools

Use server-side tools (functions) configured in Open WebUI:

```python
result = client.chat(
    question="What's the weather like in Tokyo?",
    chat_title="Weather Check",
    model_id="gpt-4.1",
    tool_ids=["weather-tool"]
)

if result:
    print(result['response'])
```

### Chat with RAG (Retrieval-Augmented Generation)

Use files or knowledge bases for context:

```python
# Using file RAG
result = client.chat(
    question="Summarize the key points from this document.",
    chat_title="Document Summary",
    rag_files=["./document.pdf"]
)

# Using knowledge base RAG
result = client.chat(
    question="What does the documentation say about authentication?",
    chat_title="Documentation Query",
    rag_collections=["my-knowledge-base"]
)
```

---

## Chat Management

### Renaming Chats

```python
success = client.rename_chat(
    chat_id="your-chat-id",
    new_title="New Chat Title"
)
```

### Setting Tags

```python
client.set_chat_tags(
    chat_id="your-chat-id",
    tags=["important", "project-x"]
)
```

### Auto-generating Metadata

```python
# Enable automatic tagging and titling
result = client.chat(
    question="What are the benefits of machine learning?",
    chat_title="ML Discussion",
    enable_auto_tagging=True,
    enable_auto_titling=True
)
```

### Organizing Chats with Folders

```python
# Create a folder
folder_id = client.create_folder("Work Projects")

# Move a chat to the folder
client.move_chat_to_folder("your-chat-id", folder_id)
```

### Archiving Chats

```python
# Archive a single chat
client.archive_chat("your-chat-id")

# Bulk archive old chats
results = client.archive_chats_by_age(
    days_since_update=30,
    folder_name="Old Projects"  # Optional: filter by folder
)

print(f"Archived {results['total_archived']} chats")
```

---

## Model Management

### Listing Models

```python
# List all available models
models = client.list_models()
for model in models:
    print(f"{model['id']}: {model['name']}")

# List base models only
base_models = client.list_base_models()

# List custom models only
custom_models = client.list_custom_models()
```

### Creating a Custom Model

```python
new_model = client.create_model(
    model_id="my-custom-gpt",
    name="My Custom GPT",
    base_model_id="gpt-4.1",
    description="A customized GPT model for my project",
    params={"temperature": 0.7},
    permission_type="private",  # "public", "private", or "group"
    tags=["custom", "project-x"]
)

if new_model:
    print(f"Created model: {new_model['id']}")
```

### Updating Model Permissions

```python
# Update a single model
client.update_model(
    model_id="my-model",
    permission_type="group",
    group_identifiers=["developers", "admins"]
)

# Batch update multiple models
result = client.batch_update_model_permissions(
    model_keyword="gpt",  # Update all models containing "gpt"
    permission_type="private",
    user_ids=["user-1", "user-2"]
)

print(f"Updated {len(result['success'])} models")
```

---

## Knowledge Base Operations

### Creating a Knowledge Base

```python
kb = client.create_knowledge_base(
    name="Project Documentation",
    description="All project-related documents"
)

if kb:
    print(f"Created KB: {kb['id']}")
```

### Adding Files to a Knowledge Base

```python
success = client.add_file_to_knowledge_base(
    file_path="./docs/guide.pdf",
    knowledge_base_name="Project Documentation"
)
```

### Batch Creating Knowledge Bases with Files

```python
kb_configs = [
    {
        "name": "Technical Docs",
        "description": "Technical documentation",
        "files": ["./tech1.pdf", "./tech2.pdf"]
    },
    {
        "name": "User Guides",
        "description": "User guides and manuals",
        "files": ["./user_guide.pdf"]
    }
]

results = client.create_knowledge_bases_with_files(kb_configs, max_workers=3)
```

### Deleting Knowledge Bases

```python
# Delete by ID
client.delete_knowledge_base("kb-id")

# Delete all
deleted, failed = client.delete_all_knowledge_bases()

# Delete by keyword
deleted, failed, names = client.delete_knowledge_bases_by_keyword("test")
```

---

## Notes Management

### Creating Notes

```python
note = client.create_note(
    title="Meeting Notes",
    data={"content": "Discussion points from today's meeting..."},
    meta={"category": "meetings", "priority": "high"}
)

if note:
    print(f"Created note: {note['id']}")
```

### CRUD Operations

```python
# Get all notes
notes = client.get_notes()

# Get a specific note
note = client.get_note_by_id("note-id")

# Update a note
updated = client.update_note_by_id(
    note_id="note-id",
    title="Updated Title",
    data={"content": "Updated content..."}
)

# Delete a note
client.delete_note_by_id("note-id")
```

---

## Prompts Management

### Creating Prompts with Variables

```python
prompt = client.create_prompt(
    command="/summarize",
    title="Document Summarizer",
    content="""Summarize the following {{document_type}} for a {{audience}} audience:

Title: {{title}}
Content: {{content}}

Provide a {{length}} summary focusing on {{key_points}}."""
)
```

### Using Prompts

```python
# Extract variables from a prompt
variables = client.extract_variables(prompt['content'])
print(f"Variables: {variables}")  # ['document_type', 'audience', 'title', 'content', 'length', 'key_points']

# Substitute variables
final_prompt = client.substitute_variables(
    prompt['content'],
    {
        "document_type": "research paper",
        "audience": "general",
        "title": "AI in Healthcare",
        "content": "...",
        "length": "concise",
        "key_points": "main findings"
    }
)

# Use in chat
result = client.chat(question=final_prompt, chat_title="Summary")
```

---

## Advanced Features

### Autonomous Task Processing

Use the agent to solve multi-step problems:

```python
result = client.process_task(
    question="Research quantum computing trends and create a summary report",
    model_id="gpt-4.1",
    tool_server_ids="web-search-tool",
    max_iterations=10,
    summarize_history=True
)

if result:
    print("--- Solution ---")
    print(result['solution'])
    print("\n--- To-Do List ---")
    for item in result['todo_list']:
        status = "✅" if item['status'] == 'completed' else "⏳"
        print(f"{status} {item['task']}")
```

### Deep Research Agent

Perform autonomous multi-step research:

```python
result = client.deep_research(
    topic="Impact of AI on software development",
    num_steps=3,
    general_models=["gpt-4.1"],
    search_models=["duckduckgo-search"]
)

if result:
    print("--- Final Report ---")
    print(result['final_report'])
```

### User Management (Admin Only)

```python
# List users
users = client.get_users(limit=50)

# Update user role
client.update_user_role("user-id", "admin")

# Delete user
client.delete_user("user-id")
```

---

## Async Client

For high-performance async applications:

```python
import asyncio
from openwebui_chat_client import AsyncOpenWebUIClient

async def main():
    async with AsyncOpenWebUIClient(
        base_url="http://localhost:3000",
        token="your-token",
        default_model_id="gpt-4.1"
    ) as client:
        # All methods support async/await
        result = await client.chat(
            question="Hello!",
            chat_title="Async Demo"
        )
        print(result['response'])
        
        # Streaming
        async for chunk in client.stream_chat(
            question="Tell me a joke",
            chat_title="Jokes"
        ):
            print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Next Steps

- [API Reference](api.md) - Explore the complete API documentation
- [GitHub Examples](https://github.com/Fu-Jie/openwebui-chat-client/tree/main/examples) - More code examples
