# 按需测试系统完整指南

## 概述

本项目实现了完整的**按需测试（On-Demand Testing）**系统，在所有CI/CD工作流中只运行与代码变更真正相关的测试。这大大提高了CI效率，减少了等待时间和资源消耗。

## 🎯 核心理念

**"只测试你修改的内容"**

- ✅ 修改`notes_manager.py` → 只运行笔记相关测试
- ✅ 修改`README.md` → 跳过所有测试
- ✅ 修改核心文件 → 运行所有相关测试
- ✅ 发布版本 → 只测试自上个版本以来的变更

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     代码变更触发                              │
│  (Push / Pull Request / CHANGELOG更新)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              变更检测 (Change Detection)                      │
│                                                               │
│  1. 获取变更文件列表 (git diff)                              │
│  2. 分析文件类型和模式                                        │
│  3. 映射到测试范围                                           │
└───────────┬───────────────────────────┬─────────────────────┘
            │                           │
            ▼                           ▼
┌───────────────────────┐   ┌──────────────────────────────┐
│   单元测试检测         │   │   集成测试检测                │
│  (detect_unit_tests)  │   │ (detect_required_tests)      │
│                       │   │                              │
│  - 源码到测试映射      │   │  - 文件模式到类别映射         │
│  - 跳过文档/配置       │   │  - 支持多类别并行            │
│  - 智能模式匹配        │   │  - 默认类别兜底              │
└───────────┬───────────┘   └──────────────┬───────────────┘
            │                              │
            ▼                              ▼
┌───────────────────────┐   ┌──────────────────────────────┐
│   运行选定的单元测试   │   │   运行选定的集成测试          │
│  (Python 3.8-3.13)    │   │  (并行执行各类别)            │
└───────────┬───────────┘   └──────────────┬───────────────┘
            │                              │
            └──────────────┬───────────────┘
                          ▼
              ┌───────────────────────┐
              │   测试结果汇总         │
              │   构建 / 发布         │
              └───────────────────────┘
```

## 🔧 实现细节

### 1. 单元测试按需运行

**脚本:** `.github/scripts/detect_unit_tests.py`

**工作原理:**

```python
# 1. 定义源码到测试的映射
SOURCE_TO_TEST_MAPPING = {
    "openwebui_chat_client/modules/notes_manager.py": ["notes_functionality"],
    "openwebui_chat_client/modules/prompts_manager.py": ["prompts_functionality"],
    # ... 更多映射
}

# 2. 定义触发所有测试的文件
TRIGGER_ALL_TESTS = [
    "setup.py",
    "pyproject.toml",
    "openwebui_chat_client/__init__.py",
]

# 3. 定义跳过测试的文件模式
SKIP_TEST_PATTERNS = [
    "*.md",
    "*.txt",
    "docs/**",
    "examples/**",
    "CHANGELOG*",
]
```

**决策流程:**

```
修改文件
    │
    ├─→ 是核心文件？ → 是 → 运行所有测试
    │
    ├─→ 是文档/配置？ → 是 → 跳过测试
    │
    ├─→ 有映射关系？ → 是 → 运行映射的测试
    │
    └─→ 其他情况 → 运行核心连接测试
```

**输出格式:**

```json
{
  "should_run": true,
  "patterns": "test_{notes,prompts}*.py"
}
```

### 2. 集成测试按需运行

**配置文件:** `.github/test-mapping.yml`

**工作原理:**

```yaml
# 1. 定义测试类别
test_categories:
  notes_api:
    name: "Notes API Integration Test"
    command: "python examples/notes_api/basic_notes.py"
    description: "Tests notes CRUD operations"

# 2. 定义文件模式到类别的映射
file_mappings:
  - pattern: "openwebui_chat_client/modules/notes_manager.py"
    categories: ["notes_api"]
  
  - pattern: "openwebui_chat_client/**/*chat*.py"
    categories: ["basic_chat", "model_switching"]
```

**脚本:** `.github/scripts/detect_required_tests.py`

**决策流程:**

```
变更文件
    │
    ├─→ 匹配模式1？ → 是 → 添加对应类别
    ├─→ 匹配模式2？ → 是 → 添加对应类别
    ├─→ ...
    │
    └─→ 无匹配 → 使用默认类别 (connectivity + basic_chat)
```

**输出格式:**

```json
["notes_api", "basic_chat", "connectivity"]
```

### 3. 发布时的智能测试

**工作流:** `.github/workflows/publish.yml`

**特殊处理:**

```bash
# 获取上一个版本标签
LAST_TAG=$(git describe --tags --abbrev=0 $CURRENT_TAG^ 2>/dev/null)

if [ -z "$LAST_TAG" ]; then
  # 首次发布 → 运行所有测试
  run_all_tests
else
  # 比较两个标签之间的变更
  detect_tests_between "$LAST_TAG" "$CURRENT_TAG"
fi
```

**优势:**

- 🎯 只测试发布涉及的变更
- ⏱️ 加速发布流程
- 🔒 确保质量（首次发布运行所有测试）

## 📝 使用指南

### 添加新功能时

**步骤 1: 创建源代码和测试**

```bash
# 创建新模块
touch openwebui_chat_client/modules/new_feature.py

# 创建对应测试
touch tests/test_new_feature.py
```

**步骤 2: 更新单元测试映射**

编辑 `.github/scripts/detect_unit_tests.py`:

```python
SOURCE_TO_TEST_MAPPING = {
    # ... 现有映射 ...
    "openwebui_chat_client/modules/new_feature.py": ["new_feature"],
}
```

**步骤 3: 更新集成测试映射**

编辑 `.github/test-mapping.yml`:

```yaml
# 1. 添加测试类别（如果是新类别）
test_categories:
  new_feature_test:
    name: "New Feature Integration Test"
    command: "python examples/new_feature/demo.py"
    description: "Tests new feature functionality"

# 2. 添加文件映射
file_mappings:
  - pattern: "openwebui_chat_client/modules/new_feature.py"
    categories: ["new_feature_test"]
```

**步骤 4: 提交并测试**

```bash
git add .
git commit -m "Add new feature"
git push

# 工作流会自动：
# 1. 检测到 new_feature.py 的变更
# 2. 运行 test_new_feature.py
# 3. 运行 new_feature_test 集成测试
```

### 本地测试检测

**预览将运行哪些单元测试:**

```bash
# 比较当前分支与main分支
python .github/scripts/detect_unit_tests.py origin/main HEAD

# 输出示例:
# Analyzing 3 changed files...
#   openwebui_chat_client/modules/notes_manager.py -> tests: notes_functionality
#   README.md -> skip (documentation/config only)
#   tests/test_notes_functionality.py -> tests: notes_functionality
# 
# Final test pattern: test_notes_functionality*.py
# Required tests: ['notes_functionality']
```

**预览将运行哪些集成测试:**

```bash
# 比较当前分支与main分支
python .github/scripts/detect_required_tests.py origin/main HEAD

# 输出示例:
# Changed files (2): ['openwebui_chat_client/modules/notes_manager.py', 'README.md']
# Checking file: openwebui_chat_client/modules/notes_manager.py
#   -> Matched categories: ['notes_api']
# Checking file: README.md
#   -> No specific patterns matched
# 
# Required test categories: ['notes_api']
# ["notes_api"]
```

### 模拟发布测试

```bash
# 获取当前最新标签
LAST_TAG=$(git describe --tags --abbrev=0)

# 比较当前代码与最新标签
echo "单元测试范围:"
python .github/scripts/detect_unit_tests.py $LAST_TAG HEAD

echo "集成测试范围:"
python .github/scripts/detect_required_tests.py $LAST_TAG HEAD
```

## 🎨 最佳实践

### 1. 精确的映射

❌ **不好的映射（过于宽泛）:**

```python
"openwebui_chat_client/**/*.py": ["all_tests"]
```

✅ **好的映射（精确且有层次）:**

```python
"openwebui_chat_client/modules/notes_manager.py": ["notes_functionality"],
"openwebui_chat_client/modules/prompts_manager.py": ["prompts_functionality"],
"openwebui_chat_client/openwebui_chat_client.py": ["openwebui_chat_client"],
```

### 2. 合理的默认值

确保有默认类别，防止漏测：

```yaml
default_categories:
  - "connectivity"      # 至少测试连接性
  - "basic_chat"        # 至少测试基础功能
```

### 3. 特殊文件的处理

```python
# 核心文件 → 运行所有测试（安全第一）
TRIGGER_ALL_TESTS = [
    "setup.py",
    "pyproject.toml",
    "openwebui_chat_client/__init__.py",
]

# 纯文档 → 跳过测试（效率优先）
SKIP_TEST_PATTERNS = [
    "*.md",
    "docs/**",
    "examples/**",  # 示例代码有独立的集成测试
]
```

### 4. 测试文件本身的变更

当修改测试文件时，应该运行该测试：

```python
# 自动处理
if filepath.startswith("tests/") and filepath.endswith(".py"):
    test_name = Path(filepath).stem.replace("test_", "")
    test_files.add(test_name)
```

## 📈 效率提升示例

### 场景 1: 修改文档

**变更:**
```
README.md
CHANGELOG.md
```

**传统方式:**
- 运行所有单元测试 (20个测试 × 6个Python版本 = 120次测试)
- 运行所有集成测试 (10个类别)
- ⏱️ 总耗时: ~15分钟

**按需测试:**
- 跳过所有测试
- ⏱️ 总耗时: ~30秒（仅检测时间）
- 💰 节省: **96%的CI时间**

### 场景 2: 修改单个模块

**变更:**
```
openwebui_chat_client/modules/notes_manager.py
tests/test_notes_functionality.py
```

**传统方式:**
- 运行所有单元测试 (120次测试)
- 运行所有集成测试 (10个类别)
- ⏱️ 总耗时: ~15分钟

**按需测试:**
- 运行1个单元测试 × 6个Python版本 = 6次测试
- 运行1个集成测试类别
- ⏱️ 总耗时: ~3分钟
- 💰 节省: **80%的CI时间**

### 场景 3: 发布新版本

**变更（自v0.1.13以来）:**
```
openwebui_chat_client/modules/notes_manager.py
openwebui_chat_client/modules/prompts_manager.py
README.md
CHANGELOG.md
```

**传统方式:**
- 运行所有测试
- ⏱️ 总耗时: ~15分钟

**按需测试:**
- 运行2个单元测试类别 × 6版本 = 12次测试
- 运行2个集成测试类别
- ⏱️ 总耗时: ~5分钟
- 💰 节省: **66%的CI时间**

## 🔍 故障排除

### 问题 1: 测试没有运行

**症状:** 期望运行的测试没有执行

**排查步骤:**

1. **检查文件是否在跳过列表中**
   ```bash
   # 查看detect_unit_tests.py中的SKIP_TEST_PATTERNS
   # 确认你的文件不匹配这些模式
   ```

2. **检查映射配置**
   ```bash
   # 确认文件路径在映射中
   grep "你的文件路径" .github/scripts/detect_unit_tests.py
   grep "你的文件模式" .github/test-mapping.yml
   ```

3. **本地测试检测逻辑**
   ```bash
   python .github/scripts/detect_unit_tests.py HEAD~1 HEAD
   python .github/scripts/detect_required_tests.py HEAD~1 HEAD
   ```

### 问题 2: 运行了过多的测试

**症状:** CI运行了不相关的测试

**可能原因:**

1. **修改了触发所有测试的核心文件**
   ```python
   TRIGGER_ALL_TESTS = [
       "setup.py",        # ← 这些文件会触发所有测试
       "pyproject.toml",
       "openwebui_chat_client/__init__.py",
   ]
   ```

2. **映射过于宽泛**
   ```yaml
   # 不好的例子
   - pattern: "openwebui_chat_client/**"
     categories: ["all", "tests"]
   ```

**解决方案:**
- 使用更精确的文件模式
- 将宽泛的映射拆分为多个精确的映射

### 问题 3: 遗漏了某些测试

**症状:** 应该运行的测试没有被触发

**解决方案:**

1. **添加缺失的映射**
   ```python
   # 在 detect_unit_tests.py 中
   SOURCE_TO_TEST_MAPPING = {
       # 添加新的映射
       "你的源文件": ["对应的测试"],
   }
   ```

2. **使用更宽泛的glob模式**
   ```yaml
   # 在 test-mapping.yml 中
   - pattern: "openwebui_chat_client/**/*feature*.py"
     categories: ["feature_test"]
   ```

3. **配置合理的默认类别**
   ```yaml
   default_categories:
     - "connectivity"
     - "basic_chat"  # 至少运行这些
   ```

## 📚 相关文档

- [workflows/README.md](.github/workflows/README.md) - 工作流详细说明
- [test-mapping.yml](.github/test-mapping.yml) - 集成测试映射配置
- [detect_unit_tests.py](.github/scripts/detect_unit_tests.py) - 单元测试检测脚本
- [detect_required_tests.py](.github/scripts/detect_required_tests.py) - 集成测试检测脚本
- [INTEGRATION_TESTING.md](.github/INTEGRATION_TESTING.md) - 集成测试指南

## 🎓 总结

按需测试系统带来的价值：

✅ **效率提升**
- 平均节省 60-90% 的CI时间
- 更快的反馈循环
- 降低CI资源消耗

✅ **精准度提高**
- 准确识别受影响的测试
- 避免运行无关测试
- 确保覆盖所有相关测试

✅ **易于维护**
- 清晰的映射配置
- 简单的添加流程
- 详细的执行日志

✅ **开发体验改善**
- 快速获得测试反馈
- 专注于真正重要的测试
- 减少等待时间

**记住核心原则: 只测试你修改的内容！** 🎯
