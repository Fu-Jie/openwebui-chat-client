# 选择性测试系统使用示例

## 📚 实际使用案例

### 案例 1: 修改聊天管理器

#### 场景

你正在修复聊天管理器中的一个bug。

#### 操作

```bash
# 1. 修改文件
vim openwebui_chat_client/modules/chat_manager.py

# 2. 提交前检查会触发哪些测试
python .github/scripts/validate_test_mapping.py \
  --test-file "openwebui_chat_client/modules/chat_manager.py"
```

#### 输出

```
📄 File: openwebui_chat_client/modules/chat_manager.py
   ✅ Exact Matches (1):
      Pattern: openwebui_chat_client/modules/chat_manager.py
      Description: Sync chat manager - triggers chat-related tests
      Tests: basic_chat, model_switching
   🎯 Total Tests Triggered: 2
```

#### 结果

- ✅ 只运行3个相关测试
- ✅ 跳过18个不相关的测试
- ✅ CI时间从15分钟减少到4分钟

---

### 案例 2: 添加新的笔记功能

#### 场景

你正在为笔记API添加新功能。

#### 操作

```bash
# 1. 修改笔记管理器
vim openwebui_chat_client/modules/notes_manager.py

# 2. 更新示例代码
vim examples/notes_api/basic_notes.py

# 3. 检查测试触发
python .github/scripts/validate_test_mapping.py \
  --test-files "openwebui_chat_client/modules/notes_manager.py,examples/notes_api/basic_notes.py"
```

#### 输出

```
📄 File: openwebui_chat_client/modules/notes_manager.py
   ✅ Exact Matches (1):
      Tests: notes_api
   🎯 Total Tests Triggered: 1

📄 File: examples/notes_api/basic_notes.py
   ✅ Exact Matches (1):
      Tests: notes_api
   🎯 Total Tests Triggered: 1
```

#### 结果

- ✅ 只运行1个notes_api测试
- ✅ 完美的精确匹配
- ✅ 最小化的测试开销

---

### 案例 3: 开发异步客户端功能

#### 场景

你正在为异步客户端添加新的流式聊天功能。

#### 操作

```bash
# 1. 修改异步聊天管理器
vim openwebui_chat_client/modules/async_chat_manager.py

# 2. 创建示例
vim examples/chat_features/async_streaming_chat.py

# 3. 检查测试
python .github/scripts/validate_test_mapping.py \
  --test-files "openwebui_chat_client/modules/async_chat_manager.py,examples/chat_features/async_streaming_chat.py"
```

#### 输出

```
📄 File: openwebui_chat_client/modules/async_chat_manager.py
   ✅ Exact Matches (1):
      Tests: async_basic_chat, async_streaming_chat
   🎯 Total Tests Triggered: 2

📄 File: examples/chat_features/async_streaming_chat.py
   ✅ Exact Matches (1):
      Tests: async_streaming_chat
   🎯 Total Tests Triggered: 1
```

#### 结果

- ✅ 运行2个异步相关测试
- ✅ 不触发同步测试
- ✅ 精确的功能隔离

---

### 案例 4: 添加全新功能模块

#### 场景

你正在添加一个全新的"工作流管理"功能。

#### 步骤 1: 创建管理器

```python
# openwebui_chat_client/modules/workflow_manager.py
class WorkflowManager:
    def create_workflow(self, name: str):
        pass
```

#### 步骤 2: 创建示例

```python
# examples/workflow_management/basic_workflow.py
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(...)
workflow = client.create_workflow("my_workflow")
```

#### 步骤 3: 更新 test-mapping.yml

```yaml
# 添加测试类别
test_categories:
  workflow_management:
    name: "Workflow Management Integration Test"
    command: "python examples/workflow_management/basic_workflow.py"
    description: "Tests workflow management functionality"

# 添加文件映射
file_mappings:
  - pattern: "openwebui_chat_client/modules/workflow_manager.py"
    categories:
      - "workflow_management"
    description: "Workflow manager - triggers workflow tests"
  
  - pattern: "examples/workflow_management/basic_workflow.py"
    categories:
      - "workflow_management"
    description: "Workflow example - triggers workflow test"
```

#### 步骤 4: 验证配置

```bash
# 验证配置文件
python .github/scripts/validate_test_mapping.py

# 测试新映射
python .github/scripts/validate_test_mapping.py \
  --test-file "openwebui_chat_client/modules/workflow_manager.py"
```

#### 输出

```
✅ Configuration is valid!

📄 File: openwebui_chat_client/modules/workflow_manager.py
   ✅ Exact Matches (1):
      Pattern: openwebui_chat_client/modules/workflow_manager.py
      Description: Workflow manager - triggers workflow tests
      Tests: workflow_management
   🎯 Total Tests Triggered: 1
```

#### 步骤 5: 提交代码

```bash
git add .
git commit -m "feat: add workflow management functionality"
git push
```

#### 结果

- ✅ GitHub Actions自动检测新功能
- ✅ 只运行workflow_management测试
- ✅ 完美的CI集成

---

### 案例 5: 修复核心客户端bug

#### 场景

你在核心同步客户端中发现了一个bug。

#### 操作

```bash
# 1. 修改核心客户端
vim openwebui_chat_client/openwebui_chat_client.py

# 2. 检查影响范围
python .github/scripts/validate_test_mapping.py \
  --test-file "openwebui_chat_client/openwebui_chat_client.py"
```

#### 输出

```
📄 File: openwebui_chat_client/openwebui_chat_client.py
   ✅ Exact Matches (1):
      Tests: connectivity, basic_chat, model_management, 
             sync_live_client, sync_live_stream
   🎯 Total Tests Triggered: 5
```

#### 分析

- ⚠️ 核心文件变更触发5个测试（合理）
- ✅ 这些都是直接依赖核心客户端的测试
- ✅ 不触发异步、笔记、prompts等无关测试

#### 结果

- ✅ 运行5个核心测试确保稳定性
- ✅ 跳过16个不相关的测试
- ✅ 平衡了覆盖率和效率

---

### 案例 6: 批量更新示例代码

#### 场景

你正在更新多个示例文件以使用新的API。

#### 操作

```bash
# 1. 修改多个示例
vim examples/getting_started/basic_chat.py
vim examples/chat_features/model_switching.py
vim examples/notes_api/basic_notes.py

# 2. 检查总体影响
python .github/scripts/validate_test_mapping.py \
  --test-files "examples/getting_started/basic_chat.py,examples/chat_features/model_switching.py,examples/notes_api/basic_notes.py"
```

#### 输出

```
📄 File: examples/getting_started/basic_chat.py
   🎯 Total Tests Triggered: 1 (basic_chat)

📄 File: examples/chat_features/model_switching.py
   🎯 Total Tests Triggered: 1 (model_switching)

📄 File: examples/notes_api/basic_notes.py
   🎯 Total Tests Triggered: 1 (notes_api)

Total unique tests: 3
```

#### 结果

- ✅ 3个文件只触发3个测试
- ✅ 每个示例只测试自己的功能
- ✅ 完美的测试隔离

---

### 案例 7: 调试测试触发问题

#### 场景

你发现某个文件变更没有触发预期的测试。

#### 操作

```bash
# 1. 启用详细日志
export VERBOSE=true

# 2. 检查文件映射
python .github/scripts/validate_test_mapping.py \
  --test-file "your_file.py"

# 3. 如果没有匹配，查看所有映射
python .github/scripts/validate_test_mapping.py --show-all | grep "your_pattern"
```

#### 调试输出

```
📄 File: your_file.py
   ⚠️  No tests matched (would use default categories)

# 查看所有映射后发现缺少规则
```

#### 解决方案

```yaml
# 在 test-mapping.yml 中添加映射
file_mappings:
  - pattern: "your_file.py"
    categories:
      - "your_test_category"
    description: "Your file - triggers your test"
```

#### 验证

```bash
python .github/scripts/validate_test_mapping.py
python .github/scripts/validate_test_mapping.py --test-file "your_file.py"
```

---

### 案例 8: 本地模拟CI测试检测

#### 场景

你想在提交前知道CI会运行哪些测试。

#### 操作

```bash
# 1. 查看当前分支的变更
git diff --name-only origin/main...HEAD

# 2. 模拟CI检测
export VERBOSE=true
python .github/scripts/detect_required_tests.py
```

#### 输出

```
🔍 Comparing: origin/main...HEAD

📝 Found 3 changed file(s):
   - openwebui_chat_client/modules/chat_manager.py
   - openwebui_chat_client/modules/notes_manager.py
   - examples/getting_started/basic_chat.py

📋 Analyzing 3 non-documentation files:

🔍 Checking: openwebui_chat_client/modules/chat_manager.py
  ✓ Exact match: openwebui_chat_client/modules/chat_manager.py
   ✅ Triggered 2 test(s): ['basic_chat', 'model_switching']

🔍 Checking: openwebui_chat_client/modules/notes_manager.py
  ✓ Exact match: openwebui_chat_client/modules/notes_manager.py
  ✅ Triggered 1 test(s): ['notes_api']

🔍 Checking: examples/getting_started/basic_chat.py
  ✓ Exact match: examples/getting_started/basic_chat.py
  ✅ Triggered 1 test(s): ['basic_chat']

================================================================================
📊 SUMMARY
================================================================================
Changed files analyzed: 3
Files with specific mappings: 3
Files using default mappings: 0
Total unique test categories: 4

🎯 Tests to run: ['basic_chat', 'model_switching', 'notes_api']
================================================================================
```

#### 结果

- ✅ 清楚知道会运行4个测试
- ✅ 可以预估CI运行时间
- ✅ 提交前心中有数

---

## 🎯 关键要点

### 1. 精确映射的价值

- 每个文件都有明确的测试映射
- 避免不必要的测试运行
- 显著提升CI效率

### 2. 工具的重要性

- 使用验证工具确保配置正确
- 提交前本地测试映射
- 详细日志帮助调试

### 3. 维护策略

- 新功能同步更新映射
- 定期验证配置文件
- 监控测试触发情况

### 4. 最佳实践

- 精确路径优于通配符
- 每个映射添加描述
- 保持测试类别清晰

---

## 📚 更多资源

- [完整指南](SELECTIVE_TESTING_GUIDE.md)
- [快速参考](TESTING_QUICK_REFERENCE.md)
- [优化总结](../INTEGRATION_TEST_OPTIMIZATION_SUMMARY.md)
- [测试映射配置](test-mapping.yml)
