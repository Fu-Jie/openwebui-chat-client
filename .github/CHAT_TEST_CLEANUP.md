# Chat测试清理机制

## 📋 概述

为了确保集成测试的可靠性和一致性，我们实现了**自动清理机制**，在运行chat相关的集成测试前自动清理所有现有的聊天会话。

---

## 🎯 为什么需要清理？

### 问题场景

1. **测试污染**: 之前的测试可能留下大量聊天会话
2. **状态不一致**: 旧的聊天可能影响新测试的结果
3. **资源占用**: 累积的聊天会话占用存储空间
4. **测试失败**: 某些测试可能因为旧数据而失败

### 解决方案

在每次运行chat相关测试前，自动清理所有聊天会话，确保：

- ✅ 干净的测试环境
- ✅ 可预测的测试结果
- ✅ 避免测试间的相互影响
- ✅ 更可靠的CI/CD流程

---

## 🔧 实现方式

### 1. 自动清理（CI/CD）

#### GitHub Actions工作流

在 `.github/workflows/integration-test.yml` 中，chat相关测试会自动触发清理：

```yaml
- name: Cleanup Test Environment (for chat tests)
  if: contains(matrix.test-category, 'chat') || contains(matrix.test-category, 'conversation')
  run: |
    echo "🧹 Cleaning up test environment for chat-related tests..."
    python .github/scripts/cleanup_test_chats.py || echo "⚠️ Cleanup failed, continuing anyway..."
  continue-on-error: true
```

#### 触发条件

清理会在以下测试类别运行前自动执行：

- `basic_chat`
- `async_basic_chat`
- `model_switching`
- `sync_live_stream`
- `async_streaming_chat`
- 任何包含 "chat" 或 "conversation" 的测试类别

### 2. 环境变量控制

所有chat示例都支持通过环境变量控制清理行为：

```bash
# 启用自动清理（推荐用于CI/CD）
export OUI_CLEANUP_BEFORE_TEST=true

# 禁用自动清理（默认，用于本地开发）
export OUI_CLEANUP_BEFORE_TEST=false
```

#### 示例代码中的实现

```python
# 在示例代码中
CLEANUP_BEFORE_TEST = os.getenv("OUI_CLEANUP_BEFORE_TEST", "false").lower() == "true"

if CLEANUP_BEFORE_TEST:
    logger.info("🧹 Cleaning up existing chats for clean test environment...")
    cleanup_success = client.delete_all_chats()
    if cleanup_success:
        logger.info("✅ Test environment cleaned (all previous chats deleted)")
    else:
        logger.warning("⚠️ Could not clean up previous chats, continuing anyway...")
```

### 3. 独立清理脚本

提供独立的清理脚本用于手动清理：

```bash
# 手动清理所有聊天
python .github/scripts/cleanup_test_chats.py
```

---

## 📊 清理流程

### 完整流程图

```
开始集成测试
    ↓
检测测试类别
    ↓
是否包含 "chat" 或 "conversation"?
    ├─ 是 → 执行清理脚本
    │         ↓
    │      连接到OpenWebUI
    │         ↓
    │      获取现有聊天列表
    │         ↓
    │      删除所有聊天
    │         ↓
    │      验证清理结果
    │         ↓
    └─ 否 → 跳过清理
    ↓
运行集成测试
    ↓
完成
```

### 清理脚本执行步骤

1. **环境验证**
   - 检查 `OUI_AUTH_TOKEN` 是否设置
   - 验证 `OUI_BASE_URL` 配置

2. **连接OpenWebUI**
   - 初始化客户端
   - 测试连接性

3. **获取聊天列表**
   - 列出所有现有聊天
   - 记录聊天数量

4. **执行删除**
   - 调用 `delete_all_chats()` 方法
   - 批量删除所有聊天

5. **验证结果**
   - 再次列出聊天
   - 确认清理成功

---

## 🚀 使用方法

### CI/CD环境（自动）

在GitHub Actions中，清理会自动执行，无需额外配置：

```yaml
# 工作流会自动检测chat测试并执行清理
env:
  OUI_BASE_URL: ${{ secrets.OUI_BASE_URL }}
  OUI_AUTH_TOKEN: ${{ secrets.OUI_AUTH_TOKEN }}
  OUI_CLEANUP_BEFORE_TEST: 'true'  # 自动设置
```

### 本地开发环境

#### 方法 1: 使用环境变量

```bash
# 启用自动清理
export OUI_CLEANUP_BEFORE_TEST=true

# 运行测试
python examples/getting_started/basic_chat.py
```

#### 方法 2: 手动清理

```bash
# 先清理
python .github/scripts/cleanup_test_chats.py

# 再运行测试
python examples/getting_started/basic_chat.py
```

#### 方法 3: 临时启用

```bash
# 一次性启用清理
OUI_CLEANUP_BEFORE_TEST=true python examples/getting_started/basic_chat.py
```

---

## 📝 支持清理的测试

### 已集成清理功能的示例

所有以下示例都支持 `OUI_CLEANUP_BEFORE_TEST` 环境变量：

#### 同步示例

- ✅ `examples/getting_started/basic_chat.py`
- ✅ `examples/chat_features/model_switching.py`
- ✅ `examples/chat_features/streaming_chat.py`

#### 异步示例

- ✅ `examples/getting_started/async_basic_chat.py`
- ✅ `examples/chat_features/async_streaming_chat.py`

### 测试类别映射

| 测试类别 | 是否清理 | 原因 |
|---------|---------|------|
| `basic_chat` | ✅ 是 | 聊天功能测试 |
| `async_basic_chat` | ✅ 是 | 异步聊天测试 |
| `model_switching` | ✅ 是 | 模型切换测试 |
| `sync_live_stream` | ✅ 是 | 流式聊天测试 |
| `async_streaming_chat` | ✅ 是 | 异步流式测试 |
| `connectivity` | ❌ 否 | 只测试连接 |
| `model_management` | ❌ 否 | 模型管理测试 |
| `notes_api` | ❌ 否 | 笔记API测试 |
| `prompts_api` | ❌ 否 | Prompts测试 |
| `rag_integration` | ❌ 否 | RAG测试 |

---

## 🔍 清理日志示例

### 成功清理

```
🧹 Starting chat cleanup process...
✅ Connected to OpenWebUI at http://localhost:3000
📊 Found 15 chat(s) to clean up
✅ Successfully deleted all chats
✅ Verified: No chats remaining
✅ Cleanup completed successfully
🎯 Test environment is ready for integration tests
```

### 清理失败（继续测试）

```
🧹 Starting chat cleanup process...
❌ OUI_AUTH_TOKEN environment variable not set
⚠️ Cleanup failed, continuing anyway...
🧪 Running integration test for category: basic_chat
```

---

## ⚙️ 配置选项

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OUI_CLEANUP_BEFORE_TEST` | `false` | 是否在测试前清理聊天 |
| `OUI_BASE_URL` | `http://localhost:3000` | OpenWebUI实例URL |
| `OUI_AUTH_TOKEN` | (必需) | 认证令牌 |
| `OUI_DEFAULT_MODEL` | `gpt-4.1` | 默认模型ID |

### 工作流配置

在 `.github/workflows/integration-test.yml` 中：

```yaml
env:
  OUI_CLEANUP_BEFORE_TEST: 'true'  # 启用清理
```

---

## 🐛 故障排除

### 问题 1: 清理失败但测试继续

**现象**: 看到清理失败的警告，但测试仍在运行

**原因**: 清理步骤设置为 `continue-on-error: true`

**影响**: 测试可能受到旧数据影响

**解决方案**:

```bash
# 手动清理
python .github/scripts/cleanup_test_chats.py

# 然后重新运行测试
```

### 问题 2: 认证失败

**现象**: `❌ OUI_AUTH_TOKEN environment variable not set`

**解决方案**:

```bash
# 设置认证令牌
export OUI_AUTH_TOKEN='your_token_here'

# 验证设置
echo $OUI_AUTH_TOKEN
```

### 问题 3: 连接超时

**现象**: 清理脚本连接OpenWebUI超时

**解决方案**:

```bash
# 检查URL是否正确
echo $OUI_BASE_URL

# 测试连接
curl $OUI_BASE_URL/api/health

# 如果需要，更新URL
export OUI_BASE_URL='http://your-openwebui-instance:3000'
```

### 问题 4: 部分聊天未删除

**现象**: 清理后仍有聊天残留

**原因**: 可能是权限问题或API限制

**解决方案**:

```bash
# 多次运行清理脚本
python .github/scripts/cleanup_test_chats.py
python .github/scripts/cleanup_test_chats.py

# 或手动在UI中删除
```

---

## 📚 相关文档

- [集成测试工作流](.github/workflows/integration-test.yml)
- [清理脚本](.github/scripts/cleanup_test_chats.py)
- [测试映射配置](.github/test-mapping.yml)
- [选择性测试指南](SELECTIVE_TESTING_GUIDE.md)

---

## 🎯 最佳实践

### CI/CD环境

1. ✅ **始终启用清理**: 设置 `OUI_CLEANUP_BEFORE_TEST=true`
2. ✅ **允许失败继续**: 使用 `continue-on-error: true`
3. ✅ **记录清理日志**: 保留清理过程的日志
4. ✅ **验证清理结果**: 检查清理后的聊天数量

### 本地开发

1. ✅ **默认禁用清理**: 避免意外删除重要聊天
2. ✅ **需要时手动清理**: 使用独立清理脚本
3. ✅ **测试前确认**: 确保不会删除重要数据
4. ✅ **使用测试账号**: 在测试环境中使用专门的测试账号

### 测试编写

1. ✅ **支持清理标志**: 在新测试中添加清理支持
2. ✅ **记录清理状态**: 在日志中明确显示是否清理
3. ✅ **优雅降级**: 清理失败时继续测试
4. ✅ **验证环境**: 测试前检查环境变量

---

## 🔄 更新历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2025-01-09 | 1.0 | 初始版本，实现自动清理机制 |

---

**维护者**: openwebui-chat-client 团队  
**最后更新**: 2025-01-09
