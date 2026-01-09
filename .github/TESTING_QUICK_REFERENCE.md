# 集成测试快速参考

## 🚀 快速开始

### 验证配置
```bash
python .github/scripts/validate_test_mapping.py
```

### 测试文件映射
```bash
# 单个文件
python .github/scripts/validate_test_mapping.py --test-file "path/to/file.py"

# 多个文件
python .github/scripts/validate_test_mapping.py --test-files "file1.py,file2.py"
```

### 查看所有映射
```bash
python .github/scripts/validate_test_mapping.py --show-all
```

---

## 📋 核心文件映射表

### 同步客户端

| 文件 | 触发的测试 |
|------|-----------|
| `openwebui_chat_client/openwebui_chat_client.py` | connectivity, basic_chat, model_management, sync_live_client, sync_live_stream |
| `openwebui_chat_client/core/base_client.py` | connectivity, basic_chat, sync_live_client |
| `openwebui_chat_client/modules/chat_manager.py` | basic_chat, model_switching, continuous_conversation |
| `openwebui_chat_client/modules/model_manager.py` | model_management, connectivity |
| `openwebui_chat_client/modules/notes_manager.py` | notes_api |
| `openwebui_chat_client/modules/prompts_manager.py` | prompts_api |
| `openwebui_chat_client/modules/knowledge_base_manager.py` | rag_integration |
| `openwebui_chat_client/modules/file_manager.py` | rag_integration |

### 异步客户端

| 文件 | 触发的测试 |
|------|-----------|
| `openwebui_chat_client/async_openwebui_client.py` | connectivity, async_basic_chat, async_streaming_chat, async_model_operations, async_live_client, async_live_stream, async_live_model_ops |
| `openwebui_chat_client/core/async_base_client.py` | connectivity, async_basic_chat, async_live_client |
| `openwebui_chat_client/modules/async_chat_manager.py` | async_basic_chat, async_streaming_chat |
| `openwebui_chat_client/modules/async_model_manager.py` | async_model_operations |
| `openwebui_chat_client/modules/async_notes_manager.py` | notes_api |
| `openwebui_chat_client/modules/async_prompts_manager.py` | prompts_api |

### 示例文件

| 文件 | 触发的测试 |
|------|-----------|
| `examples/getting_started/basic_chat.py` | basic_chat |
| `examples/getting_started/async_basic_chat.py` | async_basic_chat |
| `examples/getting_started/quick_start.py` | comprehensive_demos |
| `examples/chat_features/model_switching.py` | model_switching |
| `examples/chat_features/streaming_chat.py` | sync_live_stream |
| `examples/chat_features/async_streaming_chat.py` | async_streaming_chat |
| `examples/advanced_features/continuous_conversation.py` | continuous_conversation |
| `examples/model_management/model_operations.py` | model_management |
| `examples/model_management/async_model_operations.py` | async_model_operations |
| `examples/notes_api/basic_notes.py` | notes_api |
| `examples/prompts_api/basic_prompts.py` | prompts_api |
| `examples/rag_knowledge/file_rag.py` | rag_integration |

---

## 🎯 测试类别说明

| 类别 | 说明 | 测试命令 |
|------|------|----------|
| `connectivity` | 基础连接测试 | Python连接验证 |
| `basic_chat` | 基础聊天功能 | `examples/getting_started/basic_chat.py` |
| `async_basic_chat` | 异步基础聊天 | `examples/getting_started/async_basic_chat.py` |
| `model_switching` | 模型切换 | `examples/chat_features/model_switching.py` |
| `model_management` | 模型管理 | `examples/model_management/model_operations.py` |
| `async_model_operations` | 异步模型操作 | `examples/model_management/async_model_operations.py` |
| `notes_api` | 笔记API | `examples/notes_api/basic_notes.py` |
| `prompts_api` | Prompts API | `examples/prompts_api/basic_prompts.py` |
| `rag_integration` | RAG集成 | `examples/rag_knowledge/file_rag.py` |
| `continuous_conversation` | 连续对话 | `examples/advanced_features/continuous_conversation.py` |
| `comprehensive_demos` | 综合演示 | `examples/getting_started/quick_start.py` |
| `sync_live_stream` | 同步流式聊天 | `examples/integration/test_integration_sync_stream_chat.py` |
| `async_streaming_chat` | 异步流式聊天 | `examples/chat_features/async_streaming_chat.py` |

---

## 🔧 添加新映射

### 1. 编辑 test-mapping.yml

```yaml
# 添加测试类别
test_categories:
  your_new_test:
    name: "Your New Test"
    command: "python examples/your_feature/test.py"
    description: "Tests your new feature"

# 添加文件映射
file_mappings:
  - pattern: "openwebui_chat_client/modules/your_manager.py"
    categories:
      - "your_new_test"
    description: "Your manager - triggers your test"
```

### 2. 验证配置

```bash
python .github/scripts/validate_test_mapping.py
```

### 3. 测试映射

```bash
python .github/scripts/validate_test_mapping.py \
  --test-file "openwebui_chat_client/modules/your_manager.py"
```

---

## 📊 常见场景

### 场景 1: 修改聊天管理器

```bash
# 文件: openwebui_chat_client/modules/chat_manager.py
# 触发: basic_chat, model_switching, continuous_conversation
```

### 场景 2: 添加新的异步功能

```bash
# 文件: openwebui_chat_client/modules/async_new_manager.py
# 需要添加映射到 test-mapping.yml
```

### 场景 3: 更新示例代码

```bash
# 文件: examples/getting_started/basic_chat.py
# 触发: basic_chat
```

### 场景 4: 修改核心客户端

```bash
# 文件: openwebui_chat_client/openwebui_chat_client.py
# 触发: connectivity, basic_chat, model_management, sync_live_client, sync_live_stream
```

---

## 🐛 故障排除

### 问题: 没有触发测试

```bash
# 1. 检查文件映射
python .github/scripts/validate_test_mapping.py --test-file "your_file.py"

# 2. 如果显示 "No tests matched"，需要添加映射
```

### 问题: 触发了错误的测试

```bash
# 1. 查看当前映射
python .github/scripts/validate_test_mapping.py --test-file "your_file.py"

# 2. 修改 test-mapping.yml 中的映射规则

# 3. 重新验证
python .github/scripts/validate_test_mapping.py
```

### 问题: 配置验证失败

```bash
# 查看详细错误信息
python .github/scripts/validate_test_mapping.py

# 常见错误:
# - 引用了未定义的测试类别
# - 缺少必需字段 (command, pattern, categories)
# - YAML 语法错误
```

---

## 📚 更多信息

详细文档: [SELECTIVE_TESTING_GUIDE.md](SELECTIVE_TESTING_GUIDE.md)

配置文件: [test-mapping.yml](test-mapping.yml)
