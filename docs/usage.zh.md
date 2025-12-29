# 用户指南

本指南涵盖 `openwebui-chat-client` 库的主要功能和使用模式。

---

## 基本使用

### 初始化客户端

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)
```

### 简单聊天

```python
result = client.chat(
    question="法国的首都是什么？",
    chat_title="地理问题"
)

if result:
    print(f"响应: {result['response']}")
    print(f"聊天 ID: {result['chat_id']}")
    print(f"消息 ID: {result['message_id']}")
```

---

## 聊天功能

### 并行模型聊天

同时查询多个模型并比较它们的响应：

```python
result = client.parallel_chat(
    question="用简单的话解释量子计算。",
    chat_title="AI 模型比较",
    model_ids=["gpt-4.1", "gemini-2.5-flash"],
    folder_name="技术比较"
)

if result and result.get("responses"):
    for model, response in result["responses"].items():
        print(f"--- {model} ---")
        print(response)
        print()
```

### 流式聊天

获取具有打字机效果的实时响应：

```python
stream = client.stream_chat(
    question="讲一个关于机器人的短故事。",
    chat_title="创意写作"
)

for chunk in stream:
    print(chunk, end="", flush=True)
print()  # 结尾换行
```

### 图像聊天（多模态）

发送图像和文本提示：

```python
result = client.chat(
    question="你在这张图片中看到了什么？",
    chat_title="图像分析",
    model_id="gpt-4.1",
    image_paths=["./my_image.png"]
)

if result:
    print(result['response'])
```

### 使用工具聊天

使用 Open WebUI 中配置的服务器端工具（函数）：

```python
result = client.chat(
    question="东京的天气怎么样？",
    chat_title="天气查询",
    model_id="gpt-4.1",
    tool_ids=["weather-tool"]
)

if result:
    print(result['response'])
```

### 使用 RAG 聊天（检索增强生成）

使用文件或知识库作为上下文：

```python
# 使用文件 RAG
result = client.chat(
    question="总结这份文档的要点。",
    chat_title="文档摘要",
    rag_files=["./document.pdf"]
)

# 使用知识库 RAG
result = client.chat(
    question="文档中关于认证说了什么？",
    chat_title="文档查询",
    rag_collections=["my-knowledge-base"]
)
```

---

## 聊天管理

### 重命名聊天

```python
success = client.rename_chat(
    chat_id="your-chat-id",
    new_title="新聊天标题"
)
```

### 设置标签

```python
client.set_chat_tags(
    chat_id="your-chat-id",
    tags=["重要", "项目-x"]
)
```

### 自动生成元数据

```python
# 启用自动标签和标题生成
result = client.chat(
    question="机器学习有什么好处？",
    chat_title="机器学习讨论",
    enable_auto_tagging=True,
    enable_auto_titling=True
)
```

### 使用文件夹组织聊天

```python
# 创建文件夹
folder_id = client.create_folder("工作项目")

# 将聊天移动到文件夹
client.move_chat_to_folder("your-chat-id", folder_id)
```

### 归档聊天

```python
# 归档单个聊天
client.archive_chat("your-chat-id")

# 批量归档旧聊天
results = client.archive_chats_by_age(
    days_since_update=30,
    folder_name="旧项目"  # 可选：按文件夹筛选
)

print(f"已归档 {results['total_archived']} 个聊天")
```

---

## 模型管理

### 列出模型

```python
# 列出所有可用模型
models = client.list_models()
for model in models:
    print(f"{model['id']}: {model['name']}")

# 仅列出基础模型
base_models = client.list_base_models()

# 仅列出自定义模型
custom_models = client.list_custom_models()
```

### 创建自定义模型

```python
new_model = client.create_model(
    model_id="my-custom-gpt",
    name="我的自定义 GPT",
    base_model_id="gpt-4.1",
    description="为我的项目定制的 GPT 模型",
    params={"temperature": 0.7},
    permission_type="private",  # "public"、"private" 或 "group"
    tags=["自定义", "项目-x"]
)

if new_model:
    print(f"已创建模型: {new_model['id']}")
```

### 更新模型权限

```python
# 更新单个模型
client.update_model(
    model_id="my-model",
    permission_type="group",
    group_identifiers=["开发者", "管理员"]
)

# 批量更新多个模型
result = client.batch_update_model_permissions(
    model_keyword="gpt",  # 更新所有包含 "gpt" 的模型
    permission_type="private",
    user_ids=["user-1", "user-2"]
)

print(f"已更新 {len(result['success'])} 个模型")
```

---

## 知识库操作

### 创建知识库

```python
kb = client.create_knowledge_base(
    name="项目文档",
    description="所有项目相关文档"
)

if kb:
    print(f"已创建知识库: {kb['id']}")
```

### 向知识库添加文件

```python
success = client.add_file_to_knowledge_base(
    file_path="./docs/guide.pdf",
    knowledge_base_name="项目文档"
)
```

### 批量创建带文件的知识库

```python
kb_configs = [
    {
        "name": "技术文档",
        "description": "技术文档",
        "files": ["./tech1.pdf", "./tech2.pdf"]
    },
    {
        "name": "用户指南",
        "description": "用户指南和手册",
        "files": ["./user_guide.pdf"]
    }
]

results = client.create_knowledge_bases_with_files(kb_configs, max_workers=3)
```

### 删除知识库

```python
# 按 ID 删除
client.delete_knowledge_base("kb-id")

# 删除全部
deleted, failed = client.delete_all_knowledge_bases()

# 按关键词删除
deleted, failed, names = client.delete_knowledge_bases_by_keyword("test")
```

---

## 笔记管理

### 创建笔记

```python
note = client.create_note(
    title="会议记录",
    data={"content": "今天会议的讨论要点..."},
    meta={"category": "会议", "priority": "高"}
)

if note:
    print(f"已创建笔记: {note['id']}")
```

### CRUD 操作

```python
# 获取所有笔记
notes = client.get_notes()

# 获取特定笔记
note = client.get_note_by_id("note-id")

# 更新笔记
updated = client.update_note_by_id(
    note_id="note-id",
    title="更新的标题",
    data={"content": "更新的内容..."}
)

# 删除笔记
client.delete_note_by_id("note-id")
```

---

## 提示词管理

### 创建带变量的提示词

```python
prompt = client.create_prompt(
    command="/summarize",
    title="文档总结器",
    content="""为 {{audience}} 受众总结以下 {{document_type}}：

标题：{{title}}
内容：{{content}}

提供一个 {{length}} 的摘要，重点关注 {{key_points}}。"""
)
```

### 使用提示词

```python
# 从提示词中提取变量
variables = client.extract_variables(prompt['content'])
print(f"变量: {variables}")  # ['document_type', 'audience', 'title', 'content', 'length', 'key_points']

# 替换变量
final_prompt = client.substitute_variables(
    prompt['content'],
    {
        "document_type": "研究论文",
        "audience": "普通",
        "title": "AI 在医疗中的应用",
        "content": "...",
        "length": "简洁",
        "key_points": "主要发现"
    }
)

# 在聊天中使用
result = client.chat(question=final_prompt, chat_title="摘要")
```

---

## 高级功能

### 自主任务处理

使用代理解决多步骤问题：

```python
result = client.process_task(
    question="研究量子计算趋势并创建摘要报告",
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

### 深度研究代理

执行自主多步骤研究：

```python
result = client.deep_research(
    topic="AI 对软件开发的影响",
    num_steps=3,
    general_models=["gpt-4.1"],
    search_models=["duckduckgo-search"]
)

if result:
    print("--- 最终报告 ---")
    print(result['final_report'])
```

### 用户管理（仅管理员）

```python
# 列出用户
users = client.get_users(limit=50)

# 更新用户角色
client.update_user_role("user-id", "admin")

# 删除用户
client.delete_user("user-id")
```

---

## 异步客户端

用于高性能异步应用程序：

```python
import asyncio
from openwebui_chat_client import AsyncOpenWebUIClient

async def main():
    async with AsyncOpenWebUIClient(
        base_url="http://localhost:3000",
        token="your-token",
        default_model_id="gpt-4.1"
    ) as client:
        # 所有方法都支持 async/await
        result = await client.chat(
            question="你好！",
            chat_title="异步演示"
        )
        print(result['response'])
        
        # 流式传输
        async for chunk in client.stream_chat(
            question="讲个笑话",
            chat_title="笑话"
        ):
            print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 下一步

- [API 参考](api.zh.md) - 探索完整的 API 文档
- [GitHub 示例](https://github.com/Fu-Jie/openwebui-chat-client/tree/main/examples) - 更多代码示例
