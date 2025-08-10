# Prompts API Examples

This directory contains comprehensive examples demonstrating the prompts functionality in the OpenWebUI Chat Client.

## Overview

The prompts API allows you to create, manage, and use custom prompt templates with variable substitution. This is particularly useful for creating reusable AI interactions with dynamic content.

## Examples

### 1. Basic Prompts (`basic_prompts.py`)

Demonstrates fundamental prompt operations:

- **CRUD Operations**: Create, read, update, delete prompts
- **Variable Extraction**: Parse variables from prompt templates
- **Variable Substitution**: Replace variables with actual values
- **Search Functionality**: Find prompts by command, title, or content
- **Batch Operations**: Create/delete multiple prompts efficiently

```bash
python examples/prompts_api/basic_prompts.py
```

**Key Features Shown:**
- Simple prompt creation with `{{variable}}` syntax
- System variables like `{{CURRENT_DATE}}`, `{{CURRENT_TIME}}`
- Batch creation and deletion of prompts
- Search capabilities across different fields

### 2. Advanced Prompts (`advanced_prompts.py`)

Shows sophisticated prompt usage and integration:

- **Interactive Prompts**: Complex forms with typed inputs
- **Dynamic Generation**: Creating prompts programmatically
- **Chat Integration**: Using prompts in conversations
- **Template Patterns**: Reusable prompt templates
- **Variable Types**: Comprehensive input type examples

```bash
python examples/prompts_api/advanced_prompts.py
```

**Advanced Variable Types Demonstrated:**
- `{{text}}` - Basic text input
- `{{textarea}}` - Multi-line text
- `{{select:options=["A","B"]}}` - Dropdown selection
- `{{number:min=1:max=100}}` - Numeric input with constraints
- `{{date}}` - Date picker
- `{{time}}` - Time selector
- `{{email}}` - Email validation
- `{{url}}` - URL input
- `{{checkbox}}` - Boolean toggle
- `{{color}}` - Color picker
- `{{range:min=1:max=10}}` - Slider input

## Core Concepts

### Variable Syntax

The prompts API supports two variable formats:

1. **Simple Variables**: `{{variable_name}}`
2. **Typed Variables**: `{{variable_name | type:property="value"}}`

#### Variable Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | Single-line text input | `{{name \| text:placeholder="Enter name"}}` |
| `textarea` | Multi-line text area | `{{description \| textarea}}` |
| `select` | Dropdown menu | `{{priority \| select:options=["High","Low"]}}` |
| `number` | Numeric input | `{{count \| number:min=1:max=100}}` |
| `date` | Date picker | `{{due_date \| date}}` |
| `time` | Time selector | `{{meeting_time \| time}}` |
| `email` | Email input with validation | `{{contact \| email}}` |
| `url` | URL input | `{{website \| url}}` |
| `checkbox` | Boolean checkbox | `{{include_summary \| checkbox}}` |
| `color` | Color picker | `{{theme_color \| color:default="#FF0000"}}` |
| `range` | Slider control | `{{rating \| range:min=1:max=5}}` |

### System Variables

Automatically available variables:

- `{{CURRENT_DATE}}` - Current date (YYYY-MM-DD)
- `{{CURRENT_TIME}}` - Current time (HH:MM:SS)
- `{{CURRENT_DATETIME}}` - Current date and time
- `{{CURRENT_WEEKDAY}}` - Current day of week
- `{{CURRENT_TIMEZONE}}` - Current timezone

*Note: Variables like `{{USER_NAME}}`, `{{CLIPBOARD}}` require additional client-side implementation.*

## API Methods

### Core CRUD Operations

```python
# Get all prompts
prompts = client.get_prompts()

# Get prompts with user info
detailed_prompts = client.get_prompts_list()

# Create a new prompt
prompt = client.create_prompt(
    command="/summarize",
    title="Text Summarizer",
    content="Summarize: {{text}}"
)

# Get prompt by command
prompt = client.get_prompt_by_command("/summarize")

# Update prompt
updated = client.update_prompt_by_command(
    command="/summarize",
    content="Provide detailed summary of: {{text}}"
)

# Delete prompt
success = client.delete_prompt_by_command("/summarize")
```

### Variable Operations

```python
# Extract variables from content
variables = client.extract_variables("Hello {{name}}, your score is {{score}}")
# Returns: ["name", "score"]

# Substitute variables
content = "Hello {{name}}, today is {{CURRENT_DATE}}"
variables = {"name": "Alice"}
system_vars = client.get_system_variables()
result = client.substitute_variables(content, variables, system_vars)
```

### Batch Operations

```python
# Batch create prompts
prompts_data = [
    {"command": "/task1", "title": "Task 1", "content": "Do {{action}}"},
    {"command": "/task2", "title": "Task 2", "content": "Review {{item}}"}
]
results = client.batch_create_prompts(prompts_data)

# Batch delete prompts
commands = ["/task1", "/task2"]
results = client.batch_delete_prompts(commands)
```

### Search and Discovery

```python
# Search prompts
results = client.search_prompts("summary", by_title=True)
results = client.search_prompts("/translate", by_command=True)
results = client.search_prompts("code", by_content=True)
```

## Best Practices

### 1. Command Naming
- Use descriptive slash commands: `/summarize`, `/translate`, `/analyze`
- Follow consistent naming patterns
- Avoid special characters except underscores

### 2. Variable Design
- Use clear, descriptive variable names
- Provide helpful placeholder text
- Set appropriate defaults for select/number inputs
- Use typed variables for better UX

### 3. Content Structure
- Write clear instructions
- Group related variables logically
- Include examples where helpful
- Consider the end-user experience

### 4. Error Handling
- Always check return values from API calls
- Use batch operations with `continue_on_error=True` for resilience
- Implement proper logging for debugging

## Integration Examples

### Using Prompts in Chat

```python
# Get a prompt
prompt = client.get_prompt_by_command("/article_writer")

# Extract variables
variables = client.extract_variables(prompt['content'])

# Collect user input (in real app, this would be a form)
user_data = {
    "title": "AI in Healthcare", 
    "audience": "Technical",
    "length": "Medium (500-1000 words)"
}

# Substitute variables
final_prompt = client.substitute_variables(
    prompt['content'], 
    user_data, 
    client.get_system_variables()
)

# Use in chat
response = client.chat(final_prompt, chat_title="Article Generation")
```

### Dynamic Prompt Creation

```python
def create_context_aware_prompt(client, domain, task):
    """Create prompts based on user context."""
    
    command = f"/{domain}_{task}"
    title = f"{domain.title()} {task.replace('_', ' ').title()}"
    
    # Generate content based on domain
    if domain == "marketing":
        content = "Analyze {{campaign}} performance..."
    elif domain == "development":
        content = "Review {{code}} for {{focus}}..."
    
    return client.create_prompt(command, title, content)
```

## Environment Setup

Create a `.env` file with:

```bash
OUI_BASE_URL=http://localhost:3000
OUI_AUTH_TOKEN=your_openwebui_api_token
OUI_DEFAULT_MODEL=gpt-4.1
```

## Error Handling

Common issues and solutions:

1. **Command conflicts**: Ensure unique command names
2. **Variable syntax errors**: Check double braces `{{}}` format
3. **Network timeouts**: Implement retry logic for API calls
4. **Permission errors**: Verify API token has prompt permissions

## Next Steps

After running these examples:

1. Explore creating domain-specific prompt libraries
2. Integrate prompts with your application's chat workflows
3. Implement user interfaces for prompt variable collection
4. Consider prompt versioning and management strategies
5. Build automated prompt testing and validation