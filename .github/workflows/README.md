# GitHub Actions 工作流说明

本目录包含三个主要的CI/CD工作流，全部采用**按需测试**策略，只运行与代码变更相关的测试。

## 工作流概览

### 1. test.yml - 单元测试工作流

**触发条件:**
- Push到main/master分支
- Pull Request到main/master分支
- 手动触发

**跳过条件（paths-ignore）:**
当变更仅涉及以下文件时，整个工作流将被跳过：
- `docs/**` - 文档目录
- `*.md` - 所有Markdown文件
- `mkdocs.yml` - MkDocs配置
- `.github/workflows/deploy.yml` - 文档部署工作流
- `LICENSE` - 许可证文件
- `.gitignore` - Git忽略配置

**智能测试选择:**
- 自动检测修改的文件
- 根据源代码到测试文件的映射，只运行相关的单元测试
- 文档和配置文件变更不触发测试
- 核心文件变更会触发所有测试

**测试矩阵:**
- Python 3.8-3.13多版本并行测试

**工作流程:**
```
检测变更文件 → 确定测试范围 → 运行选定的测试 → 生成测试总结
```

### 2. integration-test.yml - 集成测试工作流

**触发条件:**
- Test工作流成功完成后自动触发
- Push到main/master分支
- Pull Request到main/master分支
- 手动触发

**跳过条件（paths-ignore）:**
当变更仅涉及以下文件时，直接push和pull_request触发的工作流将被跳过：
- `docs/**` - 文档目录
- `*.md` - 所有Markdown文件
- `mkdocs.yml` - MkDocs配置
- `.github/workflows/deploy.yml` - 文档部署工作流
- `LICENSE` - 许可证文件
- `.gitignore` - Git忽略配置

**智能测试选择:**
- 基于`.github/test-mapping.yml`配置
- 检测文件变更并映射到集成测试类别
- 只运行与变更相关的集成测试类别
- 支持手动覆盖，运行所有测试

**测试类别:**
- connectivity（连接性测试）
- basic_chat（基础聊天）
- notes_api（笔记API）
- prompts_api（提示词API）
- rag_integration（RAG集成）
- model_management（模型管理）
- model_switching（模型切换）
- comprehensive_demos（综合演示）
- continuous_conversation（连续对话）
- deep_research（深度研究）

**工作流程:**
```
检测变更文件 → 映射到测试类别 → 并行运行选定类别 → 生成测试总结
```

### 3. publish.yml - 发布工作流

**触发条件:**
- CHANGELOG.md文件更新时自动触发
- 只在CHANGELOG中出现正式版本号时执行发布（如`[0.1.14]`）
- `[Unreleased]`条目不会触发发布

**智能测试选择（发布前）:**
- 比较当前版本与上一个版本标签之间的所有变更
- 只运行与这些变更相关的单元测试和集成测试
- 首次发布时运行所有测试

**发布流程:**
```
检测版本 → 创建Git标签 → 检测测试范围 → 运行单元测试 → 运行集成测试 → 构建包 → 发布到PyPI → 创建GitHub Release
```

## 按需测试的工作原理

### 单元测试映射

通过`.github/scripts/detect_unit_tests.py`脚本实现：

```python
# 源文件到测试文件的映射示例
"openwebui_chat_client/modules/notes_manager.py" → test_notes_functionality.py
"openwebui_chat_client/modules/prompts_manager.py" → test_prompts_functionality.py
```

**规则:**
- 修改核心文件（如`__init__.py`）→ 运行所有测试
- 修改特定模块 → 只运行该模块的测试
- 修改文档/配置 → 跳过测试
- 修改测试文件本身 → 只运行该测试

### 集成测试映射

通过`.github/test-mapping.yml`配置文件定义：

```yaml
file_mappings:
  - pattern: "openwebui_chat_client/modules/notes_manager.py"
    categories: ["notes_api"]
  
  - pattern: "openwebui_chat_client/**/*chat*.py"
    categories: ["basic_chat", "model_switching"]
```

## 配置说明

### 环境变量和密钥

**必需的仓库密钥（用于集成测试和发布）:**
- `OUI_BASE_URL` - OpenWebUI实例URL
- `OUI_AUTH_TOKEN` - API认证令牌
- `PYPI_API_TOKEN` - PyPI发布令牌

**可选密钥:**
- `OUI_DEFAULT_MODEL` - 默认模型ID
- `OUI_PARALLEL_MODELS` - 并行模型列表

### 手动运行测试

**运行所有集成测试:**
```bash
# 使用workflow_dispatch，设置run_all_tests=true
```

**本地运行特定类别的集成测试:**
```bash
python .github/scripts/run_all_integration_tests.py --category notes_api
```

**本地测试检测逻辑:**
```bash
# 检测单元测试范围
python .github/scripts/detect_unit_tests.py HEAD~1 HEAD

# 检测集成测试范围
python .github/scripts/detect_required_tests.py HEAD~1 HEAD
```

## 优势

### 1. 效率提升
- ⚡ 只运行必要的测试，节省CI时间
- 🚀 更快的反馈循环
- 💰 降低CI/CD资源消耗

### 2. 精准度
- 🎯 准确识别受影响的测试
- 🔍 避免运行无关测试
- ✅ 确保所有相关测试都被执行

### 3. 可维护性
- 📝 清晰的映射配置
- 🔧 易于添加新的测试映射
- 📊 详细的测试执行报告

## 最佳实践

### 添加新功能时

1. **创建源代码文件**
2. **创建对应的测试文件**
3. **更新映射配置:**
   - 在`detect_unit_tests.py`中添加源文件到测试的映射
   - 在`test-mapping.yml`中添加集成测试映射
4. **提交代码** - 工作流会自动运行相关测试

### 发布新版本时

1. **开发期间** - 在CHANGELOG的`[Unreleased]`部分记录所有变更
2. **准备发布** - 将`[Unreleased]`改为具体版本号（如`[0.1.15]`）
3. **推送到main** - 工作流会自动：
   - 检测上个版本以来的所有变更
   - 只运行受影响的测试
   - 创建标签并发布到PyPI

### 调试测试失败

如果测试失败：
1. 查看GitHub Actions日志，了解哪些测试被运行
2. 本地复现问题
3. 修复后推送，只会重新运行相关的测试

## 维护指南

### 更新测试映射

**单元测试映射** (`.github/scripts/detect_unit_tests.py`):
```python
SOURCE_TO_TEST_MAPPING = {
    "新的源文件路径": ["对应的测试名称"],
}
```

**集成测试映射** (`.github/test-mapping.yml`):
```yaml
file_mappings:
  - pattern: "新的文件模式"
    categories: ["相关的测试类别"]
```

### 添加新的测试类别

1. 在`test-mapping.yml`的`test_categories`部分定义新类别
2. 添加文件模式映射到该类别
3. 创建对应的集成测试脚本

## 故障排除

### 问题: 测试没有运行
- 检查文件是否在跳过列表中（如`.md`文件）
- 验证文件模式是否正确配置在映射中
- 查看工作流日志中的"检测"步骤输出

### 问题: 运行了过多的测试
- 检查是否有文件触发了"运行所有测试"（如`pyproject.toml`）
- 优化映射，使其更加精确

### 问题: 遗漏了某些测试
- 在映射配置中添加缺失的文件模式
- 考虑使用更宽泛的glob模式

## 相关文档

- [INTEGRATION_TESTING.md](../INTEGRATION_TESTING.md) - 集成测试详细说明
- [test-mapping.yml](../test-mapping.yml) - 测试映射配置
- [detect_unit_tests.py](../scripts/detect_unit_tests.py) - 单元测试检测脚本
- [detect_required_tests.py](../scripts/detect_required_tests.py) - 集成测试检测脚本
