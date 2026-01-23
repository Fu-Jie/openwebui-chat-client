# 选择性集成测试系统使用指南

## 📋 概述

本项目采用**精确的选择性集成测试系统**，根据代码变更自动选择相关测试类别，显著提升CI效率并减少不必要的测试运行。

### 核心优势

- ✅ **精确映射**: 每个文件都有明确的测试映射规则
- ✅ **优先级匹配**: 精确路径优先于通配符模式
- ✅ **详细日志**: 完整的调试信息帮助理解测试选择
- ✅ **易于维护**: 清晰的配置文件和验证工具
- ✅ **高效CI**: 只运行相关测试，节省60-80%的CI时间

---

## 🏗️ 系统架构

### 1. 配置文件结构

```
.github/
├── test-mapping.yml          # 核心配置文件
└── scripts/
    ├── detect_required_tests.py      # 测试检测脚本
    ├── validate_test_mapping.py      # 配置验证工具
    └── run_all_integration_tests.py  # 测试运行器
```

### 2. 匹配优先级

测试映射按以下优先级匹配：

1. **精确路径匹配** (最高优先级)
   - 例如: `openwebui_chat_client/modules/chat_manager.py`
   - 无通配符，完全匹配文件路径

2. **通配符模式匹配**
   - 例如: `openwebui_chat_client/modules/async_*.py`
   - 使用 `*` 和 `?` 通配符

3. **默认类别** (最低优先级)
   - 当没有任何模式匹配时使用
   - 默认运行: `connectivity` 和 `basic_chat`

---

## 📝 配置文件说明

### test-mapping.yml 结构

```yaml
# 测试类别定义
test_categories:
  basic_chat:
    name: "Basic Usage Integration Test"
    command: "python examples/getting_started/basic_chat.py"
    description: "Tests basic chat functionality"

# 文件映射规则
file_mappings:
  # 精确路径映射（优先级最高）
  - pattern: "openwebui_chat_client/modules/chat_manager.py"
    categories:
      - "basic_chat"
      - "model_switching"
    description: "Sync chat manager - triggers chat-related tests"
  
  # 通配符映射
  - pattern: "openwebui_chat_client/modules/async_*.py"
    categories:
      - "async_basic_chat"
    description: "Async modules - triggers async tests"

# 默认类别（无匹配时使用）
default_categories:
  - "connectivity"
  - "basic_chat"
```

### 映射规则最佳实践

#### ✅ 推荐做法

```yaml
# 1. 精确映射核心文件
- pattern: "openwebui_chat_client/modules/notes_manager.py"
  categories: ["notes_api"]
  description: "Notes manager - triggers notes API tests"

# 2. 使用描述性说明
- pattern: "examples/getting_started/basic_chat.py"
  categories: ["basic_chat"]
  description: "Basic chat example - triggers basic chat test"

# 3. 合理的测试覆盖
- pattern: "openwebui_chat_client/core/base_client.py"
  categories:
    - "connectivity"
    - "basic_chat"
  description: "Base client - triggers core connectivity tests"
```

#### ❌ 避免的做法

```yaml
# 1. 过度宽泛的通配符
- pattern: "**/*.py"  # 太宽泛，会触发所有Python文件
  categories: ["all_tests"]

# 2. 重复的精确模式
- pattern: "openwebui_chat_client/modules/chat_manager.py"
  categories: ["basic_chat"]
- pattern: "openwebui_chat_client/modules/chat_manager.py"  # 重复！
  categories: ["model_switching"]

# 3. 未定义的测试类别
- pattern: "some_file.py"
  categories: ["non_existent_test"]  # 类别不存在
```

---

## 🔧 使用工具

### 1. 验证配置文件

```bash
# 验证配置文件的正确性
python .github/scripts/validate_test_mapping.py

# 输出示例:
# ✅ Found 20 test categories
# ✅ Found 50 file mapping rules
# ✅ Configuration is valid!
```

### 2. 测试特定文件

```bash
# 测试单个文件会触发哪些测试
python .github/scripts/validate_test_mapping.py \
  --test-file "openwebui_chat_client/modules/chat_manager.py"

# 输出示例:
# 📄 File: openwebui_chat_client/modules/chat_manager.py
#    ✅ Exact Matches (1):
#       Pattern: openwebui_chat_client/modules/chat_manager.py
#       Description: Sync chat manager - triggers chat-related tests
#       Tests: basic_chat, model_switching
#    🎯 Total Tests Triggered: 2
```

### 3. 测试多个文件

```bash
# 测试多个文件的组合效果
python .github/scripts/validate_test_mapping.py \
  --test-files "openwebui_chat_client/modules/chat_manager.py,openwebui_chat_client/modules/notes_manager.py"
```

### 4. 查看所有映射

```bash
# 显示所有文件映射规则
python .github/scripts/validate_test_mapping.py --show-all

# 输出示例:
# 📋 All File Mappings (50 rules)
# 📌 Exact Patterns (35):
#    openwebui_chat_client/modules/chat_manager.py
#       → Sync chat manager - triggers chat-related tests
#       Tests: basic_chat, model_switching
# ...
```

### 5. 本地测试检测

```bash
# 模拟GitHub Actions的测试检测
export VERBOSE=true
python .github/scripts/detect_required_tests.py

# 输出示例:
# 🔍 Comparing: HEAD~1...HEAD
# 📝 Found 2 changed file(s):
#    - openwebui_chat_client/modules/chat_manager.py
#    - examples/getting_started/basic_chat.py
# 
# 📋 Analyzing 2 non-documentation files:
# 🔍 Checking: openwebui_chat_client/modules/chat_manager.py
#   ✓ Exact match: openwebui_chat_client/modules/chat_manager.py
#   ✅ Triggered 2 test(s): ['basic_chat', 'model_switching']
# ...
```

---

## 🎯 添加新功能的工作流

### 步骤 1: 开发新功能

假设你正在添加一个新的"用户管理"功能：

```python
# openwebui_chat_client/modules/user_manager.py
class UserManager:
    def list_users(self):
        pass
```

### 步骤 2: 创建示例代码

```python
# examples/user_management/basic_users.py
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(...)
users = client.list_users()
```

### 步骤 3: 创建集成测试

示例代码本身就是集成测试，确保它可以独立运行。

### 步骤 4: 更新 test-mapping.yml

```yaml
# 1. 添加测试类别
test_categories:
  user_management:
    name: "User Management Integration Test"
    command: "python examples/user_management/basic_users.py"
    description: "Tests user management functionality"

# 2. 添加文件映射
file_mappings:
  # 精确映射管理器文件
  - pattern: "openwebui_chat_client/modules/user_manager.py"
    categories:
      - "user_management"
    description: "User manager - triggers user management tests"
  
  # 映射示例文件
  - pattern: "examples/user_management/basic_users.py"
    categories:
      - "user_management"
    description: "User management example - triggers user management test"
```

### 步骤 5: 验证配置

```bash
# 验证配置文件
python .github/scripts/validate_test_mapping.py

# 测试新文件的映射
python .github/scripts/validate_test_mapping.py \
  --test-file "openwebui_chat_client/modules/user_manager.py"
```

### 步骤 6: 提交代码

```bash
git add .
git commit -m "feat: add user management functionality"
git push
```

GitHub Actions 会自动：

1. 检测到 `user_manager.py` 的变更
2. 触发 `user_management` 集成测试
3. 只运行相关测试，不运行其他无关测试

---

## 🐛 故障排除

### 问题 1: 测试没有被触发

**症状**: 修改了文件，但没有运行预期的测试

**解决方案**:

```bash
# 1. 检查文件是否在映射中
python .github/scripts/validate_test_mapping.py \
  --test-file "your_changed_file.py"

# 2. 如果没有匹配，添加映射规则到 test-mapping.yml

# 3. 验证配置
python .github/scripts/validate_test_mapping.py
```

### 问题 2: 触发了太多测试

**症状**: 小改动触发了大量不相关的测试

**原因**: 通配符模式太宽泛

**解决方案**:

```yaml
# 修改前（太宽泛）
- pattern: "openwebui_chat_client/**/*.py"
  categories: ["all_tests"]

# 修改后（精确）
- pattern: "openwebui_chat_client/modules/chat_manager.py"
  categories: ["basic_chat", "model_switching"]
```

### 问题 3: 配置验证失败

**症状**: `validate_test_mapping.py` 报错

**常见错误**:

```bash
# 错误 1: 引用了未定义的测试类别
❌ Mapping 'some_file.py' references undefined category 'non_existent_test'

# 解决: 在 test_categories 中定义该类别

# 错误 2: 缺少必需字段
❌ Test category 'my_test' missing 'command'

# 解决: 添加 command 字段
```

### 问题 4: 本地测试与CI不一致

**症状**: 本地检测的测试与CI运行的不同

**解决方案**:

```bash
# 1. 确保使用相同的配置文件
cat .github/test-mapping.yml

# 2. 模拟GitHub Actions环境
export GITHUB_ACTIONS=true
export GITHUB_EVENT_NAME=push
python .github/scripts/detect_required_tests.py

# 3. 启用详细日志
export VERBOSE=true
python .github/scripts/detect_required_tests.py
```

---

## 📊 性能优化建议

### 1. 精确映射优先

```yaml
# ✅ 好：精确映射
- pattern: "openwebui_chat_client/modules/chat_manager.py"
  categories: ["basic_chat"]

# ❌ 差：过度使用通配符
- pattern: "**/*chat*.py"
  categories: ["basic_chat"]
```

### 2. 合理的测试覆盖

```yaml
# ✅ 好：只触发相关测试
- pattern: "openwebui_chat_client/modules/notes_manager.py"
  categories: ["notes_api"]

# ❌ 差：触发所有测试
- pattern: "openwebui_chat_client/modules/notes_manager.py"
  categories: ["notes_api", "basic_chat", "model_management", ...]
```

### 3. 避免重复映射

```yaml
# ✅ 好：一个文件一个映射
- pattern: "openwebui_chat_client/modules/chat_manager.py"
  categories: ["basic_chat", "model_switching"]

# ❌ 差：重复映射
- pattern: "openwebui_chat_client/modules/chat_manager.py"
  categories: ["basic_chat"]
- pattern: "openwebui_chat_client/modules/chat_manager.py"
  categories: ["model_switching"]
```

---

## 📈 监控和维护

### 定期审查

```bash
# 每月运行一次，检查配置健康度
python .github/scripts/validate_test_mapping.py --show-all

# 检查是否有未映射的文件
find openwebui_chat_client -name "*.py" | while read file; do
  python .github/scripts/validate_test_mapping.py --test-file "$file" | grep "No tests matched" && echo "⚠️  $file"
done
```

### 性能指标

跟踪以下指标：

- 平均触发的测试数量
- CI运行时间
- 测试覆盖率
- 误触发率（不相关的测试被触发）

---

## 🎓 最佳实践总结

1. ✅ **精确优于通配**: 优先使用精确路径映射
2. ✅ **描述清晰**: 每个映射都添加描述性说明
3. ✅ **定期验证**: 使用验证工具检查配置
4. ✅ **测试本地**: 提交前在本地测试映射
5. ✅ **保持简洁**: 避免过度复杂的映射规则
6. ✅ **文档同步**: 更新功能时同步更新映射
7. ✅ **监控效果**: 定期检查测试触发的准确性

---

## 🔗 相关资源

- [test-mapping.yml](.github/test-mapping.yml) - 核心配置文件
- [detect_required_tests.py](.github/scripts/detect_required_tests.py) - 检测脚本
- [validate_test_mapping.py](.github/scripts/validate_test_mapping.py) - 验证工具
- [integration-test.yml](.github/workflows/integration-test.yml) - CI工作流

---

## 💡 获取帮助

如果遇到问题：

1. 运行验证工具: `python .github/scripts/validate_test_mapping.py`
2. 启用详细日志: `export VERBOSE=true`
3. 查看CI日志中的"Detection Results"部分
4. 参考本文档的故障排除章节

---

**最后更新**: 2025-01-09
**维护者**: openwebui-chat-client 团队
