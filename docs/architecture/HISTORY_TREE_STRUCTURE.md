# Open WebUI History Tree 结构详解

## 核心概念

Open WebUI 的 `history.messages` 使用**树形结构**来支持对话的**分支、重新生成和多模型并行**功能。

## 数据结构

```json
{
  "history": {
    "messages": {
      "msg-user-1": {
        "id": "msg-user-1",
        "parentId": null,
        "childrenIds": ["msg-asst-1", "msg-asst-2", "msg-asst-3"],
        "role": "user",
        "content": "What is the capital of France?",
        "timestamp": 1737619200
      },
      "msg-asst-1": {
        "id": "msg-asst-1",
        "parentId": "msg-user-1",
        "childrenIds": ["msg-user-2"],
        "role": "assistant",
        "model": "gpt-4.1",
        "modelIdx": 0,
        "content": "The capital of France is Paris.",
        "timestamp": 1737619201
      },
      "msg-asst-2": {
        "id": "msg-asst-2",
        "parentId": "msg-user-1",
        "childrenIds": [],
        "role": "assistant",
        "model": "gpt-4.1",
        "modelIdx": 0,
        "content": "Paris is the capital city of France.",
        "timestamp": 1737619205
      },
      "msg-asst-3": {
        "id": "msg-asst-3",
        "parentId": "msg-user-1",
        "childrenIds": [],
        "role": "assistant",
        "model": "gemini-2.5-flash",
        "modelIdx": 1,
        "content": "The capital of France is Paris (French: Paris).",
        "timestamp": 1737619201
      },
      "msg-user-2": {
        "id": "msg-user-2",
        "parentId": "msg-asst-1",
        "childrenIds": ["msg-asst-4"],
        "role": "user",
        "content": "What about Germany?",
        "timestamp": 1737619210
      }
    },
    "currentId": "msg-asst-4"
  }
}
```

## 三种主要使用场景

### 1. 重新生成（Regenerate）

用户对 AI 的回答不满意，点击"重新生成"按钮：

```
用户消息 A (msg-user-1)
├─ 助手响应 1 (msg-asst-1) - 第一次生成
└─ 助手响应 2 (msg-asst-2) - 重新生成（相同模型，不同内容）
```

**特征**：

- 两个 assistant 消息有**相同的 parentId**
- 两个 assistant 消息有**相同的 model** 和 **modelIdx**
- 前端可以在这两个响应之间切换
- `currentId` 指向用户当前查看的响应

### 2. 编辑历史消息（Branching）

用户编辑之前的消息，创建新的对话分支：

```
用户消息 A
└─ 助手响应 1
   ├─ 用户消息 B (原始)
   │  └─ 助手响应 2
   └─ 用户消息 B' (编辑后)
      └─ 助手响应 3
```

**特征**：

- 编辑创建新的用户消息节点
- 原有分支保留但不在当前路径
- 通过 parentId 和 childrenIds 导航不同分支

### 3. 并行多模型（Parallel Multi-Model）

用户选择多个模型，同时生成多个响应：

```
用户消息 A
├─ 助手响应 1 (gpt-4.1, modelIdx=0)
├─ 助手响应 2 (gemini-2.5-flash, modelIdx=1)
└─ 助手响应 3 (claude-3-5-sonnet, modelIdx=2)
```

**特征**：

- 多个 assistant 消息有**相同的 parentId**
- 每个 assistant 消息有**不同的 model**
- 每个 assistant 消息有**不同的 modelIdx**（在 models 列表中的索引）
- 前端使用标签页或其他 UI 组件切换不同模型的响应

## 关键字段说明

### parentId

- 指向父消息的 ID
- 用于向上遍历构建消息链
- 根消息的 parentId 为 null

### childrenIds

- 数组，包含所有子消息的 ID
- 支持多个子节点（重新生成、分支、并行模型）
- 用于向下遍历和分支导航

### currentId

- 指向用户当前查看的消息
- 用于确定当前活跃的对话路径
- UI 从 currentId 向上遍历到根节点显示完整对话

### modelIdx

- 在 models 列表中的索引（从 0 开始）
- 用于前端标签页分组和显示
- 相同 modelIdx 的消息使用相同的标签页

### model

- 完整的模型 ID（如 "gpt-4.1", "gemini-2.5-flash"）
- 用于标识使用的具体模型
- 可以从 modelIdx 和 models 列表推导，但直接存储更方便

## Python 客户端实现

### 并行聊天实现

```python
# openwebui_chat_client/modules/chat_operations.py

def parallel_chat(
    self,
    question: str,
    chat_title: str,
    model_ids: List[str],
    **kwargs
) -> Optional[ParallelChatResponse]:
    """
    向多个模型并行发送相同的问题。
    
    生成的 tree 结构：
    用户消息
    ├─ 助手响应 (model_ids[0], modelIdx=0)
    ├─ 助手响应 (model_ids[1], modelIdx=1)
    └─ 助手响应 (model_ids[2], modelIdx=2)
    """
    
    # 1. 创建用户消息
    user_message_id = str(uuid.uuid4())
    storage_user_message = {
        "id": user_message_id,
        "parentId": last_message_id,
        "childrenIds": [],  # 将填充所有 assistant 消息 ID
        "role": "user",
        "content": question,
        "models": model_ids,  # 标记这是多模型请求
    }
    
    # 2. 并行请求所有模型
    with ThreadPoolExecutor(max_workers=len(model_ids)) as executor:
        futures = {
            executor.submit(self._get_single_model_response, model_id): model_id
            for model_id in model_ids
        }
        
        # 收集所有响应
        responses = {}
        for future in as_completed(futures):
            model_id = futures[future]
            content, sources, followUps = future.result()
            responses[model_id] = {"content": content, "sources": sources}
    
    # 3. 为每个成功的响应创建 assistant 消息
    assistant_message_ids = []
    for idx, (model_id, resp_data) in enumerate(responses.items()):
        assistant_id = str(uuid.uuid4())
        assistant_message_ids.append(assistant_id)
        
        storage_assistant_message = {
            "id": assistant_id,
            "parentId": user_message_id,  # 相同的父节点
            "childrenIds": [],
            "role": "assistant",
            "content": resp_data["content"],
            "model": model_id,
            "modelIdx": model_ids.index(model_id),  # 关键：modelIdx
            "timestamp": int(time.time()),
        }
        
        chat_core["history"]["messages"][assistant_id] = storage_assistant_message
    
    # 4. 更新用户消息的 childrenIds
    chat_core["history"]["messages"][user_message_id]["childrenIds"] = assistant_message_ids
    
    # 5. 设置 currentId（通常是第一个响应）
    chat_core["history"]["currentId"] = assistant_message_ids[0]
    
    # 6. 同步到后端
    self._update_remote_chat()
```

### Tree 遍历算法

```python
def get_message_chain(messages_dict: dict, message_id: str) -> List[dict]:
    """
    从指定消息向上遍历到根节点，构建完整消息链。
    这是官方后端使用的算法。
    """
    message_list = []
    current_message = messages_dict.get(message_id)
    
    while current_message:
        message_list.insert(0, current_message)  # 插入到开头
        parent_id = current_message.get("parentId")
        current_message = messages_dict.get(parent_id) if parent_id else None
    
    return message_list
```

## 前端如何使用 Tree 结构

### 1. 显示当前对话路径

```typescript
// 从 currentId 向上遍历到根节点
function getCurrentPath(history) {
    const messages = [];
    let currentId = history.currentId;
    
    while (currentId) {
        const message = history.messages[currentId];
        messages.unshift(message);  // 添加到开头
        currentId = message.parentId;
    }
    
    return messages;
}
```

### 2. 多模型标签页显示

```typescript
// 按 modelIdx 分组显示
function groupByModelIdx(assistantMessages) {
    const grouped = {};
    
    for (const msg of assistantMessages) {
        const idx = msg.modelIdx ?? 0;
        if (!grouped[idx]) {
            grouped[idx] = [];
        }
        grouped[idx].push(msg);
    }
    
    return grouped;
}
```

### 3. 切换不同响应

```typescript
// 切换到同一 parentId 下的另一个 assistant 响应
function switchToResponse(history, newAssistantId) {
    history.currentId = newAssistantId;
    // 重新渲染 UI
}
```

## 与 messages 数组的关系

```json
{
  "chat": {
    "history": {
      "messages": { /* 树形结构，完整数据 */ },
      "currentId": "msg-asst-4"
    },
    "messages": [ /* 线性数组，当前路径的扁平化表示 */ ]
  }
}
```

- **history.messages**（字典）：完整的树形结构，所有分支都保留
- **messages**（数组）：当前对话路径的扁平化表示，用于 UI 快速渲染
- **messages 数组由 history.messages 生成**，不是数据源

## 最佳实践

### 1. 读取当前响应

```python
# ✅ 正确：从 history.messages[currentId] 读取
history = chat.get("history", {})
messages_dict = history.get("messages", {})
current_id = history.get("currentId")

if current_id and current_id in messages_dict:
    current_message = messages_dict[current_id]
    content = current_message.get("content", "")
```

### 2. 支持重新生成

```python
# 为同一用户消息生成新响应
def regenerate_response(chat_core, user_message_id, model_id):
    # 创建新的 assistant 消息
    new_assistant_id = str(uuid.uuid4())
    new_assistant_message = {
        "id": new_assistant_id,
        "parentId": user_message_id,  # 相同的父节点
        "childrenIds": [],
        "role": "assistant",
        "model": model_id,
        "modelIdx": 0,  # 如果是单模型重新生成
        "content": generate_content(),
    }
    
    # 添加到 messages 字典
    chat_core["history"]["messages"][new_assistant_id] = new_assistant_message
    
    # 添加到用户消息的 childrenIds
    user_message = chat_core["history"]["messages"][user_message_id]
    user_message["childrenIds"].append(new_assistant_id)
    
    # 更新 currentId
    chat_core["history"]["currentId"] = new_assistant_id
```

### 3. 支持分支对话

```python
# 编辑用户消息创建新分支
def edit_and_branch(chat_core, old_user_message_id, new_content):
    old_message = chat_core["history"]["messages"][old_user_message_id]
    
    # 创建新的用户消息
    new_user_id = str(uuid.uuid4())
    new_user_message = {
        "id": new_user_id,
        "parentId": old_message["parentId"],  # 相同的父节点
        "childrenIds": [],
        "role": "user",
        "content": new_content,
    }
    
    chat_core["history"]["messages"][new_user_id] = new_user_message
    
    # 更新父消息的 childrenIds
    parent_id = old_message["parentId"]
    if parent_id:
        parent_message = chat_core["history"]["messages"][parent_id]
        parent_message["childrenIds"].append(new_user_id)
```

## 总结

1. **history.messages 是字典**：支持 O(1) 访问，适合树形结构
2. **使用 parentId 和 childrenIds**：构建完整的对话树
3. **currentId 指向当前路径**：确定用户当前查看的消息
4. **modelIdx 支持多模型**：前端用于标签页分组显示
5. **messages 数组是派生数据**：从 history.messages 生成，不应作为数据源

这个设计使 Open WebUI 能够支持：

- ✅ 对话分支和历史编辑
- ✅ 重新生成响应
- ✅ 多模型并行比较
- ✅ 灵活的 UI 导航和显示
