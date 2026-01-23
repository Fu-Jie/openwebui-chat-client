# Parallel Chat Integration Tests

本文档说明如何运行和理解并行聊天（Parallel Chat）的集成测试。

## 测试内容

### 1. 功能测试

#### Test 1: chat() 方法支持 chat_id 参数

- ✅ 创建初始聊天
- ✅ 使用 chat_id 继续对话
- ✅ 验证 chat_id 保持一致
- ✅ 验证 history tree 结构
- ✅ 验证消息链正确构建

#### Test 2: parallel_chat() 方法支持 chat_id 参数

- ✅ 创建单模型聊天
- ✅ 在同一聊天中使用多个模型
- ✅ 验证所有模型都有响应
- ✅ 验证 modelIdx 字段正确设置
- ✅ 验证 tree 结构：相同 parentId，多个 childrenIds

#### Test 3: History Tree 导航

- ✅ 创建包含多条消息的对话
- ✅ 从 currentId 回溯到根节点
- ✅ 验证完整的消息链
- ✅ 确认 parentId/childrenIds 双向链接

### 2. History Tree 结构验证

测试验证以下 history tree 特性：

```json
{
  "history": {
    "messages": {
      "user-1": {
        "id": "user-1",
        "parentId": null,
        "childrenIds": ["asst-1", "asst-2"],
        "role": "user",
        "content": "Question"
      },
      "asst-1": {
        "id": "asst-1",
        "parentId": "user-1",
        "childrenIds": [],
        "role": "assistant",
        "model": "gpt-4.1",
        "modelIdx": 0,
        "content": "Response from GPT-4"
      },
      "asst-2": {
        "id": "asst-2",
        "parentId": "user-1",
        "childrenIds": [],
        "role": "assistant",
        "model": "gemini-2.5-flash",
        "modelIdx": 1,
        "content": "Response from Gemini"
      }
    },
    "currentId": "asst-1"
  }
}
```

验证项：

1. ✅ `history.messages` 是字典（dict）而非数组
2. ✅ `currentId` 指向有效的消息 ID
3. ✅ 每个消息的 `parentId` 指向存在的父消息
4. ✅ 每个消息的 `childrenIds` 都指向存在的子消息
5. ✅ 子消息的 `parentId` 正确指回父消息（双向链接）
6. ✅ Assistant 消息包含 `model` 和 `modelIdx` 字段
7. ✅ 并行响应共享相同的 `parentId`
8. ✅ 父消息的 `childrenIds` 包含所有并行响应的 ID

## 运行测试

### 方式 1: 使用脚本（推荐）

```bash
./run_parallel_chat_tests.sh
```

这个脚本会：

1. 检查环境变量
2. 运行简单示例（`parallel_chat_simple.py`）
3. 运行完整集成测试（`parallel_chat_with_history.py`）
4. 提供清晰的成功/失败反馈

### 方式 2: 单独运行

```bash
# 简单示例
python examples/chat_features/parallel_chat_simple.py

# 完整集成测试
python examples/chat_features/parallel_chat_with_history.py
```

## 环境变量

必需的环境变量：

```bash
export OUI_BASE_URL="http://localhost:3000"
export OUI_AUTH_TOKEN="your_token_here"
```

可选的环境变量：

```bash
export OUI_DEFAULT_MODEL="gpt-4.1"
export OUI_PARALLEL_MODELS="gpt-4.1,gemini-2.5-flash,claude-3-5-sonnet"
```

## 测试输出

### 成功示例

```
🚀 Starting 3-step chat workflow: 'What is the capital of France?'...
✅ Created chat with ID: 7bf88a99...
🤖 Response 1: The capital of France is **Paris**...

📝 Step 2: Continue in same chat using chat_id
✅ Continued in same chat: 7bf88a99...
🤖 Response 2: The capital of Germany is **Berlin**...

📊 Chat has 4 messages in history.messages
🎯 currentId: asst-message-id-2
✅ history.messages is a dict
✅ currentId points to valid message
  ✅ Message user-1... role=user, model=None, modelIdx=None
  ✅ Message asst-1... role=assistant, model=gpt-4.1, modelIdx=None
✅ All tree structure validations passed

✅ Test 1 PASSED: chat() with chat_id works correctly
```

### 并行聊天成功示例

```
📝 Step 2: Use parallel_chat with chat_id
🤖 Querying models: ['gpt-4.1', 'gemini-2.5-flash']
✅ Parallel chat completed

📊 Received 2 responses:
  🤖 gpt-4.1: Solar and wind energy are both renewable sources...
  🤖 gemini-2.5-flash: Solar energy harnesses power from the sun...

📝 Step 5: Verify modelIdx field in parallel responses
📊 Found 2 assistant responses
  ✅ model=gpt-4.1, modelIdx=0
  ✅ model=gemini-2.5-flash, modelIdx=1
✅ modelIdx values are properly set: [0, 1]

✅ All 2 responses share same parent
✅ Parent's childrenIds contains all responses

✅ Test 2 PASSED: parallel_chat() with chat_id works correctly
```

## 故障排除

### 常见问题

1. **认证失败**

   ```
   ❌ OUI_AUTH_TOKEN environment variable not set
   ```

   解决：设置环境变量 `export OUI_AUTH_TOKEN='your_token'`

2. **模型不足**

   ```
   ❌ Need at least 2 models, got: ['gpt-4.1']
   ```

   解决：设置 `export OUI_PARALLEL_MODELS="gpt-4.1,gemini-2.5-flash"`

3. **连接错误**

   ```
   ❌ Failed to connect to http://localhost:3000
   ```

   解决：确保 Open WebUI 服务器正在运行

4. **Tree 结构验证失败**

   ```
   ❌ Message has invalid parentId
   ```

   这通常表示实现有 bug，请检查代码逻辑。

### 调试技巧

1. **查看详细日志**：代码中已包含详细的 logger.info() 输出

2. **手动检查 chat 数据**：

   ```python
   chat_obj = client.get_chat_by_id(chat_id)
   import json
   print(json.dumps(chat_obj.get("chat", {}).get("history", {}), indent=2))
   ```

3. **验证特定消息**：

   ```python
   messages_dict = history.get("messages", {})
   msg = messages_dict.get(message_id)
   print(f"Message: {json.dumps(msg, indent=2)}")
   ```

## 测试覆盖范围

| 功能 | 覆盖状态 | 测试文件 |
|------|---------|---------|
| chat() with chat_id | ✅ 完全覆盖 | parallel_chat_with_history.py |
| parallel_chat() with chat_id | ✅ 完全覆盖 | parallel_chat_with_history.py |
| history.messages 字典结构 | ✅ 完全覆盖 | parallel_chat_with_history.py |
| parentId/childrenIds 双向链接 | ✅ 完全覆盖 | parallel_chat_with_history.py |
| modelIdx 字段 | ✅ 完全覆盖 | parallel_chat_with_history.py |
| currentId 验证 | ✅ 完全覆盖 | parallel_chat_with_history.py |
| 消息链构建 | ✅ 完全覆盖 | parallel_chat_with_history.py |
| 混合单/多模型聊天 | ✅ 完全覆盖 | parallel_chat_simple.py |

## 预期结果

运行完整测试套件后，应该看到：

```
📊 Overall: 3/3 tests passed
🎉 All tests passed!
```

如果所有测试通过，说明：

1. ✅ chat_id 参数功能正常
2. ✅ History tree 结构正确
3. ✅ 并行聊天实现完整
4. ✅ modelIdx 字段正确设置
5. ✅ 与前端完全兼容

## 参考文档

- [History Tree Structure](../docs/architecture/HISTORY_TREE_STRUCTURE.md) - 详细的 tree 结构说明
- [Examples README](./README.md) - 所有示例的总览
- [Main README](../README.md) - 项目主文档
