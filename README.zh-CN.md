# OpenWebUI Python 客户端

[English](./README.md) | [简体中文](./README.zh-CN.md)

[![PyPI 版本](https://img.shields.io/pypi/v/openwebui-chat-client?style=flat-square&color=brightgreen)](https://pypi.org/project/openwebui-chat-client/)
[![更新日志](https://img.shields.io/badge/更新日志-最新-blue.svg)](./CHANGELOG.zh-CN.md)
[![许可证: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![支持的 Python 版本](https://img.shields.io/pypi/pyversions/openwebui-chat-client.svg)](https://pypi.org/project/openwebui-chat-client/)
[![测试](https://github.com/Fu-Jie/openwebui-chat-client/actions/workflows/test.yml/badge.svg)](https://github.com/Fu-Jie/openwebui-chat-client/actions/workflows/test.yml)
[![覆盖率](https://img.shields.io/badge/coverage-69%25-yellow?style=flat-square)](https://github.com/Fu-Jie/openwebui-chat-client/actions/workflows/coverage.yml)

**openwebui-chat-client** 是面向 [Open WebUI](https://github.com/open-webui/open-webui) API 的状态化 Python 客户端库，支持单/多模型对话、工具调用、文件上传、RAG、知识库管理和高级聊天组织。

> [!IMPORTANT]
> 本项目正处于积极开发阶段，API 可能会在未来版本中发生变化。请查阅最新文档和 [CHANGELOG.zh-CN.md](./CHANGELOG.zh-CN.md) 以获取最新信息。

---

## 🚀 安装

```bash
pip install openwebui-chat-client
```

---

## ⚡ 快速开始

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="你的令牌",
    default_model_id="gpt-4.1"
)

# chat 方法返回一个包含回复、chat_id 和 message_id 的字典
result = client.chat(
    question="你好，你怎么样？",
    chat_title="我的第一次聊天"
)
if result:
    print(f"回复: {result['response']}")
    print(f"Chat ID: {result['chat_id']}")
```

---

## ✨ 主要功能

- **自主任务处理**: 使用 `process_task` 和 `stream_process_task` 方法进行多步骤迭代式问题解决，支持工具和知识库集成。
- **自动元数据生成**: 为您的对话自动生成标签和标题。
- **手动元数据更新**: 按需为现有对话重新生成标签和标题。
- **实时流式聊天更新**: 在流式聊天期间体验打字机效果的实时内容更新。
- **聊天追问生成选项**: 支持在聊天方法中生成追问问题或选项。
- **自主深度研究**: 一个作为自主代理的新 `deep_research` 方法，可对任何给定主题执行多步骤研究。
- 多模态对话：文本、图片、文件上传
- 单模型 & 并行模型对话（A/B 测试）
- 工具集成：在对话中调用服务器端工具
- RAG 检索增强：文件/知识库辅助回复
- 知识库管理：创建、更新、查询
- **笔记管理**：创建、检索、更新和删除带有结构化数据和元数据的笔记。
- **提示词管理**：创建、管理和使用带有变量替换和交互式表单的自定义提示词。
- 模型管理：列出、创建、更新、删除自定义模型条目，并增强了 `get_model` 的自动创建/重试功能。
- 聊天组织：重命名、文件夹、标签、搜索
- **并发处理**: 并行模型查询，实现快速多模型响应。

---

## 🧑‍💻 基本示例

### 单模型对话

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="你的令牌",
    default_model_id="gpt-4.1"
)

result = client.chat(
    question="介绍一下 OpenAI GPT-4.1 的主要功能？",
    chat_title="GPT-4.1 功能演示"
)
if result:
    print(result['response'])
```

### 并行模型对话

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="你的令牌",
    default_model_id="gpt-4.1"
)

result = client.parallel_chat(
    question="比较 GPT-4.1 和 Gemini 2.5 Flash 在文档摘要方面的优势。",
    chat_title="模型对比",
    model_ids=["gpt-4.1", "gemini-2.5-flash"],
    folder_name="技术对比" # 你可以选择将聊天整理到文件夹中
)
if result and result.get("responses"):
    for model, resp in result["responses"].items():
        print(f"{model} 回复:\n{resp}\n")
    print(f"聊天已保存，ID: {result.get('chat_id')}")
```

### 🖥️ 示例：页面渲染 (Web UI 集成)

运行上述 Python 代码后，你可以在 Open WebUI 网页界面中查看对话和模型比较结果：

- **单模型** (`gpt-4.1`):  
  聊天记录将在对话时间线中显示你的输入问题和 GPT-4.1 模型的回应。  
  ![单模型对话示例](https://cdn.jsdelivr.net/gh/Fu-Jie/openwebui-chat-client@main/examples/images/single-model-chat.png)

- **并行模型** (`gpt-4.1` & `gemini-2.5-flash`):  
  聊天将并排（或分组）显示两个模型对同一输入的响应，通常会按模型进行标记或颜色编码。  
  ![并行模型比较示例](https://cdn.jsdelivr.net/gh/Fu-Jie/openwebui-chat-client@main/examples/images/parallel-model-chat.png)

> **提示:**  
> Web UI 会使用模型名称来直观地区分响应。你可以展开、折叠或复制每个答案，还可以在界面中直接对聊天进行标记、整理和搜索。

---

## 🧠 高级聊天示例

### 1. 使用工具 (函数)

如果你的 Open WebUI 实例中配置了工具（例如天气工具或网页搜索工具），你可以在请求中指定使用哪些工具。

```python
# 假设你的服务器上配置了一个 ID 为 'search-the-web-tool' 的工具。
# 这个工具需要在 Open WebUI 的“工具”部分创建。

result = client.chat(
    question="欧盟人工智能监管的最新进展是什么？",
    chat_title="AI 监管新闻",
    model_id="gpt-4.1",
    tool_ids=["search-the-web-tool"] # 传入要使用的工具 ID
)

if result:
    print(result['response'])
```

### 2. 多模态聊天 (带图片)

将图片与文本提示一起发送给支持视觉的模型。

```python
# 确保 'chart.png' 存在于你的脚本所在的目录中。
# 模型 'gpt-4.1' 支持视觉功能。

result = client.chat(
    question="请分析附带的销售图表，并提供趋势摘要。",
    chat_title="销售图表分析",
    model_id="gpt-4.1",
    image_paths=["./chart.png"] # 图片的本地文件路径列表
)

if result:
    print(result['response'])
```

### 3. 在同一聊天中切换模型

你可以用一个模型开始对话，然后切换到另一个模型进行后续提问，所有这些都在同一个聊天历史中。客户端无缝处理状态。

### 7. 深度研究代理

使用 `deep_research` 方法启动一个自主研究代理。该代理将对给定主题进行多轮规划和执行，并将整个过程作为多轮对话呈现在UI上，最终生成一份综合报告。

```python
# 启动一个研究代理来分析一个主题
result = client.deep_research(
    topic="生成式AI对软件开发行业的影响",
    num_steps=3,  # 代理将执行3轮“规划-执行”循环
    model_id="llama3"
)

if result:
    print("--- 最终报告 ---")
    print(result.get('final_report'))
    print(f"\n👉 在UI中查看标题为 '{result.get('chat_title')}' 的完整研究过程。")
```

```python
# 用一个强大的通用模型开始聊天
result_1 = client.chat(
    question="用简单的语言解释相对论。",
    chat_title="科学与速度",
    model_id="gpt-4.1"
)
if result_1:
    print(f"GPT-4.1 回答: {result_1['response']}")

# 现在，在同一个聊天中提出一个不同的问题，但切换到一个快速高效的模型
result_2 = client.chat(
    question="现在，陆地上跑得最快的 3 种动物是什么？",
    chat_title="科学与速度",   # 使用相同的标题继续聊天
    model_id="gemini-2.5-flash"  # 切换到不同的模型
)
if result_2:
    print(f"\nGemini 2.5 Flash 回答: {result_2['response']}")

# 两个结果的 chat_id 将相同。
if result_1 and result_2:
    print(f"\n两次交互的 Chat ID: {result_1['chat_id']}")
```

### 8. 自主任务处理

`process_task` 和 `stream_process_task` 方法支持多步骤迭代式问题解决，具有工具集成、知识库支持和智能决策能力。

#### 核心特性

- **关键发现累积**：AI 会维护一个"关键发现"部分，在整个问题解决过程中持久化工具调用结果，确保关键信息不会在迭代之间丢失。
- **决策模型支持**：当 AI 提出多个解决方案时，可选的决策模型可以自动分析并选择最佳方案，无需用户干预。
- **待办事项管理**：AI 在整个任务解决过程中维护和更新结构化的待办事项列表。
- **工具集成**：与 Open WebUI 工具服务器无缝集成，用于外部数据检索和计算。

#### 基本用法

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

# 基本任务处理
result = client.process_task(
    question="研究量子计算的最新发展并总结关键突破",
    model_id="gpt-4.1",
    tool_server_ids="web-search-tool",
    max_iterations=10,
    summarize_history=True
)

if result:
    print("--- 解决方案 ---")
    print(result['solution'])
    print("\n--- 待办事项 ---")
    for item in result['todo_list']:
        status = "✅" if item['status'] == 'completed' else "⏳"
        print(f"{status} {item['task']}")
```

#### 使用决策模型自动选择方案

当 AI 识别出多种可能的方法时，决策模型会自动选择最佳选项：

```python
# 带决策模型的任务处理
result = client.process_task(
    question="分析高流量电商应用的最佳缓存策略",
    model_id="gpt-4.1",
    tool_server_ids=["web-search", "code-analyzer"],
    decision_model_id="claude-3-sonnet",  # 当出现多个选项时自动选择
    max_iterations=15,
    summarize_history=True
)

if result:
    print(f"解决方案: {result['solution']}")
```

#### 流式任务处理

实时查看问题解决过程：

```python
# 带决策模型的流式任务处理
stream = client.stream_process_task(
    question="为社交媒体平台设计微服务架构",
    model_id="gpt-4.1",
    tool_server_ids="architecture-tools",
    decision_model_id="claude-3-sonnet",
    max_iterations=10
)

try:
    while True:
        event = next(stream)
        event_type = event.get("type")
        
        if event_type == "iteration_start":
            print(f"\n--- 迭代 {event['iteration']} ---")
        elif event_type == "thought":
            print(f"🤔 思考中: {event['content'][:100]}...")
        elif event_type == "todo_list_update":
            print("📋 待办事项已更新")
        elif event_type == "tool_call":
            print(f"🛠️ 调用工具: {event['content']}")
        elif event_type == "decision":
            print(f"🎯 决策模型选择了选项 {event['selected_option']}")
        elif event_type == "observation":
            print(f"👀 观察结果: {event['content'][:100]}...")
        elif event_type == "final_answer":
            print(f"\n✅ 最终答案: {event['content']}")
            
except StopIteration as e:
    final_result = e.value
    print(f"\n📊 任务完成，解决方案: {final_result['solution'][:200]}...")
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `question` | str | 要解决的任务或问题 |
| `model_id` | str | 用于任务执行的模型 ID |
| `tool_server_ids` | str \| List[str] | 工具服务器 ID，用于外部功能 |
| `knowledge_base_name` | str (可选) | 知识库名称，用于 RAG 增强 |
| `max_iterations` | int | 问题解决的最大迭代次数（默认：25） |
| `summarize_history` | bool | 是否总结对话历史（默认：False） |
| `decision_model_id` | str (可选) | 决策模型 ID，当出现多个方案时自动选择 |

#### 流事件类型

| 事件类型 | 说明 |
|----------|------|
| `iteration_start` | 每次推理迭代开始时发出 |
| `thought` | AI 的当前思考和推理 |
| `todo_list_update` | 待办事项已更新 |
| `tool_call` | AI 正在调用外部工具 |
| `observation` | 工具调用或操作的结果 |
| `decision` | 决策模型选择了一个选项（当提供 `decision_model_id` 时） |
| `final_answer` | 任务完成，给出最终解决方案 |
| `error` | 处理过程中发生错误 |

### 4. 批量模型权限管理

您可以一次性管理多个模型的权限，支持公共、私有和基于群组的访问控制。

```python
# 将多个模型设置为公共访问
result = client.batch_update_model_permissions(
    model_identifiers=["gpt-4.1", "gemini-2.5-flash"],
    permission_type="public"
)

# 将包含"gpt"的所有模型设置为特定用户的私有访问
result = client.batch_update_model_permissions(
    model_keyword="gpt",
    permission_type="private",
    user_ids=["user-id-1", "user-id-2"]
)

# 使用群组名称将模型设置为基于群组的权限
result = client.batch_update_model_permissions(
    model_keyword="claude",
    permission_type="group",
    group_identifiers=["admin", "normal"]  # 群组名称将被解析为ID
)

print(f"✅ 成功更新: {len(result['success'])} 个模型")
print(f"❌ 更新失败: {len(result['failed'])} 个模型")

# 列出可用于权限管理的群组
groups = client.list_groups()
if groups:
    for group in groups:
        print(f"群组: {group['name']} (ID: {group['id']})")
```

### 5. 归档聊天会话

您可以单独归档聊天会话，或根据其时间和文件夹组织进行批量归档。

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient("http://localhost:3000", "your_token_here", "gpt-4.1")

# 归档特定聊天
success = client.archive_chat("chat-id-here")
if success:
    print("✅ 聊天归档成功")

# 批量归档超过30天且不在文件夹中的聊天
results = client.archive_chats_by_age(days_since_update=30)
print(f"已归档 {results['total_archived']} 个聊天")

# 批量归档特定文件夹中超过7天的聊天
results = client.archive_chats_by_age(
    days_since_update=7, 
    folder_name="旧项目"
)
print(f"从文件夹归档了 {results['total_archived']} 个聊天")

# 获取详细结果
for chat in results['archived_chats']:
    print(f"已归档: {chat['title']}")

for chat in results['failed_chats']:
    print(f"失败: {chat['title']} - {chat['error']}")
```

**归档逻辑:**

- **无文件夹过滤**: 仅归档不在任何文件夹中的聊天
- **有文件夹过滤**: 仅归档在指定文件夹中的聊天
- **时间过滤**: 仅归档在指定天数内未更新的聊天
- **并行处理**: 使用并发处理提高批量操作效率

### 6. 使用带变量替换的提示词

创建和使用交互式提示词，通过动态变量替换实现可重用的AI交互。

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

# 创建带变量的提示词
prompt = client.create_prompt(
    command="/summarize",
    title="文章摘要器",
    content="""请为{{audience}}受众总结这篇{{document_type}}：

标题：{{title}}
内容：{{content}}

提供一个{{length}}摘要，重点关注{{key_points}}。"""
)

# 从提示词中提取变量
variables = client.extract_variables(prompt['content'])
print(f"发现的变量: {variables}")

# 用实际值替换变量
variables_data = {
    "document_type": "研究论文",
    "audience": "普通大众",
    "title": "AI在医疗中的应用",
    "content": "人工智能正在改变...",
    "length": "简洁的",
    "key_points": "主要发现和影响"
}

# 获取系统变量并进行替换
system_vars = client.get_system_variables()
final_prompt = client.substitute_variables(
    prompt['content'], 
    variables_data, 
    system_vars
)

# 在聊天中使用处理后的提示词
result = client.chat(
    question=final_prompt,
    chat_title="AI医疗摘要"
)

print(f"摘要: {result['response']}")
```

**提示词功能：**

- **变量类型**: 支持文本、选择、日期、数字、复选框等
- **系统变量**: 自动填充的 CURRENT_DATE、CURRENT_TIME 等
- **批量操作**: 高效创建/删除多个提示词
- **搜索过滤**: 按命令、标题或内容查找提示词
- **交互式表单**: 用户友好的提示词收集复杂输入类型

---

## 🔑 如何获取你的 API 密钥

1. 登录你的 Open WebUI 账户。
2. 点击左下角的个人资料图片/名称，然后进入 **设置**。
3. 在设置菜单中，导航到 **账户** 部分。
4. 找到 **API 密钥** 区域并 **创建新密钥**。
5. 复制生成的密钥，并将其设置为你的 `OUI_AUTH_TOKEN` 环境变量，或直接在客户端代码中使用。

---

## 📚 API 参考

### 💬 聊天操作

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `chat()` | 启动/继续单模型对话，支持追问生成选项 | `question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling` |
| `stream_chat()` | 启动/继续单模型流式对话，支持实时更新 | `question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling` |
| `parallel_chat()` | 启动/继续多模型并行对话 | `question, chat_title, model_ids, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling` |
| `process_task()` | 执行自主多步骤任务处理和迭代式问题解决，支持关键发现累积和可选的决策模型自动选择方案 | `question, model_id, tool_server_ids, knowledge_base_name, max_iterations, summarize_history, decision_model_id` |
| `stream_process_task()` | 流式自主多步骤任务处理，支持实时更新、关键发现累积和可选的决策模型 | `question, model_id, tool_server_ids, knowledge_base_name, max_iterations, summarize_history, decision_model_id` |

### 🛠️ 聊天管理

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `rename_chat()` | 重命名现有聊天 | `chat_id, new_title` |
| `set_chat_tags()` | 为聊天应用标签 | `chat_id, tags` |
| `update_chat_metadata()` | 为现有聊天重新生成和更新标签和/或标题 | `chat_id, regenerate_tags, regenerate_title` |
| `switch_chat_model()` | 切换现有聊天的模型 | `chat_id, new_model_id` |
| `create_folder()` | 创建聊天文件夹进行组织 | `folder_name` |
| `list_chats()` | 获取用户聊天列表，支持分页 | `page` |
| `get_chats_by_folder()` | 获取特定文件夹中的聊天 | `folder_id` |
| `archive_chat()` | 归档特定聊天 | `chat_id` |
| `archive_chats_by_age()` | 基于时间和文件夹条件批量归档聊天 | `days_since_update, folder_name` |

### 🤖 模型管理

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `list_models()` | 列出用户所有可用的模型，包括基础模型和用户创建的自定义模型。排除禁用的基础模型。对应聊天页面左上角显示的模型列表。 | None |
| `list_base_models()` | 列出可用于创建变体的所有基础模型。包括禁用的基础模型。对应管理设置页面中的模型列表，包括 PIPE 类型模型。 | None |
| `list_custom_models()` | 列出用户可以使用或已创建的自定义模型（非基础模型）。 | None |
| `list_groups()` | 列出所有可用的权限管理用户组 | None |
| `get_model()` | 获取特定模型的详细信息，支持自动重试创建 | `model_id` |
| `create_model()` | 创建详细的自定义模型变体 | `model_config` |
| `update_model()` | 使用细粒度更改更新现有模型条目 | `model_id, access_control, **kwargs` |
| `delete_model()` | 从服务器删除模型条目 | `model_id` |
| `batch_update_model_permissions()` | 批量更新多个模型的访问控制权限 | `model_identifiers, model_keyword, permission_type, group_identifiers, user_ids, max_workers` |

### 👥 用户管理

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `get_users()` | 列出所有用户，支持分页 | `skip, limit` |
| `get_user_by_id()` | 获取特定用户的详细信息 | `user_id` |
| `update_user_role()` | 更新用户角色（admin/user） | `user_id, role` |
| `delete_user()` | 删除用户 | `user_id` |

### ⚡ 异步客户端

`AsyncOpenWebUIClient` 为所有操作提供异步接口，适用于高性能异步应用（FastAPI、Sanic 等）。所有方法的签名与同步版本相同，但需要使用 `async`/`await` 前缀。

**主要区别：**

- 所有方法都是 `async` 的，必须使用 `await` 调用
- 使用 `httpx.AsyncClient` 进行 HTTP 操作，而不是 `requests`
- 支持异步上下文管理器（`async with`）
- 流式方法返回 `AsyncGenerator` 对象

**初始化：**

```python
from openwebui_chat_client import AsyncOpenWebUIClient

# 基本初始化
client = AsyncOpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

# 使用自定义 httpx 配置
client = AsyncOpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1",
    timeout=120.0,
    verify=False,  # 禁用 SSL 验证
    limits=httpx.Limits(max_connections=100)  # 自定义连接限制
)

# 使用上下文管理器（推荐）
async with AsyncOpenWebUIClient(base_url, token, model_id) as client:
    result = await client.chat("你好", "我的对话")
    # client.close() 会自动调用
```

**可用的异步方法：**

所有同步方法都有异步等效方法：

| 异步方法 | 同步等效方法 | 返回值 |
|-------------|----------------|---------|
| `await client.chat(...)` | `client.chat(...)` | `Optional[Dict[str, Any]]` |
| `async for chunk in client.stream_chat(...)` | `for chunk in client.stream_chat(...)` | `AsyncGenerator[str, None]` |
| `await client.list_models()` | `client.list_models()` | `Optional[List[Dict[str, Any]]]` |
| `await client.get_users(...)` | `client.get_users(...)` | `Optional[List[Dict[str, Any]]]` |
| `await client.create_knowledge_base(...)` | `client.create_knowledge_base(...)` | `Optional[Dict[str, Any]]` |
| ... | ... | ... |

**使用示例：**

```python
import asyncio
from openwebui_chat_client import AsyncOpenWebUIClient

async def main():
    async with AsyncOpenWebUIClient(
        base_url="http://localhost:3000",
        token="your-token",
        default_model_id="gpt-4.1"
    ) as client:
        # 基本对话
        result = await client.chat(
            question="什么是 Python？",
            chat_title="Python 讨论"
        )
        print(result['response'])
        
        # 流式对话
        print("流式响应：")
        async for chunk in client.stream_chat(
            question="给我讲个故事",
            chat_title="故事时间"
        ):
            print(chunk, end='', flush=True)
        
        # 用户管理
        users = await client.get_users(skip=0, limit=50)
        print(f"找到 {len(users)} 个用户")
        
        # 模型操作
        models = await client.list_models()
        for model in models:
            print(f"- {model['id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**FastAPI 集成示例：**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openwebui_chat_client import AsyncOpenWebUIClient

app = FastAPI()

# 在启动时初始化客户端一次
client = AsyncOpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-token",
    default_model_id="gpt-4.1"
)

class ChatRequest(BaseModel):
    question: str
    chat_title: str

@app.on_event("shutdown")
async def shutdown():
    await client.close()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    result = await client.chat(
        question=request.question,
        chat_title=request.chat_title
    )
    if not result:
        raise HTTPException(status_code=500, detail="对话失败")
    return result

@app.get("/models")
async def list_models():
    models = await client.list_models()
    return {"models": models}
```

**性能考虑：**

- **并发性**：异步客户端允许并发处理多个请求
- **连接池**：使用 httpx 的连接池提高效率
- **超时配置**：根据用例自定义超时
- **错误处理**：异步方法与同步方法抛出相同的异常

**文件 I/O 注意事项：**

某些操作（如 `AsyncFileManager` 中的 `encode_image_to_base64()`）是同步的，因为它们是 CPU 密集型的。对于大文件，可以将这些操作包装在 `asyncio.to_thread()` 中：

```python
# 对于大文件
encoded = await asyncio.to_thread(
    client._file_manager.encode_image_to_base64,
    "large_image.jpg"
)
```

### 📚 知识库操作

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `create_knowledge_base()` | 创建新的知识库 | `name, description` |
| `add_file_to_knowledge_base()` | 向现有知识库添加文件 | `kb_id, file_path` |
| `get_knowledge_base_by_name()` | 根据名称检索知识库 | `name` |
| `delete_knowledge_base()` | 根据ID删除特定知识库 | `kb_id` |
| `delete_all_knowledge_bases()` | 删除所有知识库（批量操作） | None |
| `delete_knowledge_bases_by_keyword()` | 删除名称包含关键字的知识库 | `keyword` |
| `create_knowledge_bases_with_files()` | 创建多个知识库并向每个库添加文件 | `kb_file_mapping` |

### 📝 笔记 API

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `get_notes()` | 获取当前用户的所有笔记及完整详细信息 | None |
| `get_notes_list()` | 获取基本信息的简化笔记列表 | None |
| `create_note()` | 创建具有可选元数据和访问控制的新笔记 | `title, data, meta, access_control` |
| `get_note_by_id()` | 根据ID检索特定笔记 | `note_id` |
| `update_note_by_id()` | 使用新内容或元数据更新现有笔记 | `note_id, title, data, meta, access_control` |
| `delete_note_by_id()` | 根据ID删除笔记 | `note_id` |

### 📝 提示词 API

| 方法 | 描述 | 参数 |
|--------|-------------|------------|
| `get_prompts()` | 获取当前用户的所有提示词 | None |
| `get_prompts_list()` | 获取带有详细用户信息的提示词列表 | None |
| `create_prompt()` | 创建带有变量和访问控制的新提示词 | `command, title, content, access_control` |
| `get_prompt_by_command()` | 根据斜杠命令检索特定提示词 | `command` |
| `update_prompt_by_command()` | 根据命令更新现有提示词 | `command, title, content, access_control` |
| `delete_prompt_by_command()` | 根据斜杠命令删除提示词 | `command` |
| `search_prompts()` | 按各种条件搜索提示词 | `query, by_command, by_title, by_content` |
| `extract_variables()` | 从提示词内容中提取变量名称 | `content` |
| `substitute_variables()` | 用值替换提示词内容中的变量 | `content, variables, system_variables` |
| `get_system_variables()` | 获取用于替换的当前系统变量 | None |
| `batch_create_prompts()` | 在单个操作中创建多个提示词 | `prompts_data, continue_on_error` |
| `batch_delete_prompts()` | 根据命令删除多个提示词 | `commands, continue_on_error` |

### 📊 返回值示例

**聊天操作返回：**

```python
{
    "response": "生成的响应文本",
    "chat_id": "聊天-uuid-字符串",
    "message_id": "消息-uuid-字符串",
    "sources": [...]  # RAG 操作时
}
```

**并行聊天返回：**

```python
{
    "responses": {
        "model-1": "模型 1 的响应",
        "model-2": "模型 2 的响应"
    },
    "chat_id": "聊天-uuid-字符串",
    "message_ids": {
        "model-1": "消息-uuid-1",
        "model-2": "消息-uuid-2"
    }
}
```

**知识库/笔记返回：**

```python
{
    "id": "资源-uuid",
    "name": "资源名称",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    ...
}
```

---

## 📚 文档

完整文档可在以下网址获取：**[https://fu-jie.github.io/openwebui-chat-client/](https://fu-jie.github.io/openwebui-chat-client/)**

文档包括：

- 详细的安装和设置指南
- 全面的使用示例
- 完整的 API 参考
- 开发指南

### 本地构建文档

要在本地构建和预览文档：

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs serve
```

然后在浏览器中访问 `http://localhost:8000`。

### 部署文档

当更改推送到主分支时，文档会自动部署到 GitHub Pages。

**首次设置：** 如果您是首次设置存储库，需要启用 GitHub Pages：

1. 进入存储库设置：`https://github.com/Fu-Jie/openwebui-chat-client/settings/pages`
2. 在"构建和部署"下，选择 **"GitHub Actions"** 作为源
3. 保存设置

详细说明请参阅 [docs/github-pages-setup.md](docs/github-pages-setup.md)。

---

## 🛠️ 故障排除

- **认证错误**：确保你的 Bearer Token 是有效的。
- **找不到模型**：检查模型 ID 是否正确（例如 `"gpt-4.1"`, `"gemini-2.5-flash"`）并且在你的 Open WebUI 实例上可用。
- **找不到工具**：确保你提供的 `tool_ids` 与在 Open WebUI 设置中配置的工具 ID 匹配。
- **文件/图片上传问题**：确保文件路径正确，并且应用程序有读取这些文件的必要权限。
- **Web UI 未更新**：刷新页面或检查服务器日志以获取任何潜在的错误信息。

---

## 🧪 集成冒烟测试 (可选)

轻量级的实时检查位于 `examples/integration/` 目录下，并受环境变量控制，因此在没有配置凭据时可以自动跳过。

**前置条件:**

- `OUI_BASE_URL` (例如：`http://localhost:3000`)
- `OUI_AUTH_TOKEN` (具有聊天访问权限的 Bearer token；用户/模型操作需要管理员 token)
- `OUI_DEFAULT_MODEL` (如果省略，默认使用 `gpt-4.1`)

**运行选定的测试分类:**

```bash
python run_integration_tests.py --category sync_live_stream --verbose
```

常见的分类包括 `sync_live_stream`, `async_live_stream`, `model_management`, `notes_api`, 和 `prompts_api`。请查看 `examples/integration/` 目录获取完整列表。

> 这些测试在本地运行是可选且安全的；当未配置 secrets 时，CI 会自动跳过它们。

---

## 🤝 贡献代码

欢迎提交代码、反馈问题和功能请求！  
随时查看 [Issues 页面](https://github.com/Fu-Jie/openwebui-chat-client/issues) 或是提交 Pull Request。

---

## 📄 用户协议

本项目遵循 **GNU General Public License v3.0 (GPLv3)** 协议。  
了解更多细节，请查看 [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) 文件。

---
