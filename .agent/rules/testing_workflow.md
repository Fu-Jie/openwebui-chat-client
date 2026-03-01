## 选择性集成测试系统

### 1. 测试系统概述

#### 智能测试选择

openwebui-chat-client项目采用**智能选择性集成测试系统**，根据代码变更自动选择相关测试类别，显著提升CI效率：

- **变更分析**: 自动分析PR/push中的文件变更，支持多种GitHub事件类型
- **模式匹配**: 根据`.github/test-mapping.yml`配置映射测试类别
- **并行执行**: 使用GitHub Actions矩阵策略并行运行
- **手动覆盖**: 提供完整测试的手动触发选项
- **事件类型适配**: 正确处理`workflow_run`、`push`、`pull_request`等不同事件类型

#### 测试效率提升

- **优化前**: 每次变更运行全部8个集成测试类别
- **优化后**: 仅运行相关测试类别（通常1-3个）
- **时间节省**: CI运行时间减少60-80%
- **资源节约**: 显著降低GitHub Actions使用量

#### 工作流事件处理

- **workflow_run事件**: 从主测试工作流触发时，正确获取变更文件的SHA上下文
- **直接触发事件**: 支持push和PR的直接触发，使用当前分支的SHA
- **SHA上下文管理**: 确保文件变更检测在所有事件类型中都能正确工作

### 2. 测试配置管理

#### `.github/test-mapping.yml` 配置文件

这是核心配置文件，定义文件模式到测试类别的映射：

```yaml
# 测试类别定义
test_categories:
  connectivity:
    name: "Basic Connectivity Test"
    command: "python -c \"...\""  # 基础连接测试
    description: "Tests basic client connectivity"
  
  basic_chat:
    name: "Basic Usage Integration Test"
    command: "python examples/getting_started/basic_chat.py"
    description: "Tests basic chat functionality"

# 文件模式映射
file_mappings:
  - pattern: "openwebui_chat_client/openwebui_chat_client.py"
    categories: ["connectivity", "basic_chat", "model_management"]
  
  - pattern: "examples/notes_api/**"
    categories: ["notes_api"]
```

#### 配置维护原则

- **精确映射**: 确保文件变更触发最相关的测试
- **避免过度测试**: 不要为小变更触发过多测试类别
- **保证覆盖**: 重要功能变更必须有对应测试
- **默认安全**: 未匹配模式时运行核心测试

### 3. 测试类别标准

#### 标准测试类别

项目定义了以下标准测试类别：

| 类别 | 用途 | 测试命令 | 触发条件 |
|------|------|----------|----------|
| `connectivity` | 基础连接验证 | Python客户端连接测试 | 核心文件、配置变更 |
| `basic_chat` | 基础聊天功能 | `examples/getting_started/basic_chat.py` | 聊天相关代码变更 |
| `notes_api` | 笔记API功能 | `examples/notes_api/basic_notes.py` | 笔记相关文件变更 |
| `rag_integration` | RAG集成测试 | `examples/rag_knowledge/file_rag.py` | RAG、知识库相关变更 |
| `model_management` | 模型管理 | `examples/model_management/model_operations.py` | 模型相关功能变更 |
| `model_switching` | 模型切换 | `examples/chat_features/model_switching.py` | 模型切换功能变更 |
| `comprehensive_demos` | 综合演示 | `examples/getting_started/quick_start.py` | 复杂功能、示例变更 |

#### 新测试类别添加流程

1. **定义测试目标**: 明确测试类别要验证的功能
2. **创建测试命令**: 在`test-mapping.yml`中添加测试定义
3. **配置文件映射**: 添加相应的`file_mappings`规则
4. **验证测试**: 确保测试命令可以独立执行
5. **更新文档**: 在集成测试文档中说明新类别

### 4. 脚本工具使用

#### `.github/scripts/detect_required_tests.py`

测试检测脚本，分析变更文件并确定需要运行的测试：

```bash
# 检测当前分支相对于main的变更需要的测试
python .github/scripts/detect_required_tests.py

# 检测特定文件变更需要的测试
python .github/scripts/detect_required_tests.py --files "file1.py,file2.py"

# 输出详细映射信息
python .github/scripts/detect_required_tests.py --verbose
```

#### `.github/scripts/run_all_integration_tests.py`

完整集成测试运行器，用于手动执行：

```bash
# 运行所有集成测试
python .github/scripts/run_all_integration_tests.py

# 运行特定测试类别
python .github/scripts/run_all_integration_tests.py --category notes_api

# 列出所有可用测试类别
python .github/scripts/run_all_integration_tests.py --list-categories

# 并行运行（默认）
python .github/scripts/run_all_integration_tests.py --parallel

# 串行运行（调试用）
python .github/scripts/run_all_integration_tests.py --no-parallel
```

#### `run_integration_tests.py` (根目录)

用户友好的测试运行器，简化本地开发体验：

```bash
# 简单运行
python run_integration_tests.py

# 运行特定类别
python run_integration_tests.py --category basic_chat
```

### 5. GitHub Actions集成

#### 工作流配置要点

`.github/workflows/integration-test.yml`配置要点：

```yaml
# 支持多种触发事件
on:
  workflow_run:
    workflows: ["Test"]
    types: [completed]
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
  workflow_dispatch:  # 手动触发支持

# 动态文件变更检测
detect-changes:
  steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0  # 需要完整历史进行git diff
      # 为workflow_run事件使用正确的commit SHA
      ref: ${{ github.event_name == 'workflow_run' && github.event.workflow_run.head_sha || github.sha }}

# 使用矩阵策略并行运行选定的测试类别
strategy:
  matrix:
    test-category: ${{ fromJson(needs.detect-tests.outputs.test-categories) }}
  fail-fast: false  # 允许部分测试失败时继续其他测试

# 环境变量传递和验证
env:
  OUI_BASE_URL: ${{ github.event.inputs.base_url || secrets.OUI_BASE_URL }}
  OUI_AUTH_TOKEN: ${{ github.event.inputs.auth_token || secrets.OUI_AUTH_TOKEN }}
  OUI_DEFAULT_MODEL: ${{ github.event.inputs.default_model || secrets.OUI_DEFAULT_MODEL }}
```

#### 文件变更检测机制

工作流使用智能文件变更检测：

1. **SHA上下文处理**:
   - `workflow_run`事件: 使用`github.event.workflow_run.head_sha`
   - 直接触发事件: 使用`github.sha`
   - 确保在所有触发类型中都能正确检测变更

2. **Git Diff策略**:
   - 优先使用三点比较: `git diff --name-only base...head`
   - 回退到单提交比较: `git diff --name-only HEAD~1 HEAD`
   - 支持多种分支和引用类型

3. **调试和故障排除**:
   - 为workflow_run事件提供详细的调试输出
   - 记录关键的SHA和分支信息
   - 便于问题诊断和修复

#### 手动触发完整测试

开发者可以通过GitHub UI手动触发完整测试：

1. 访问Actions页面
2. 选择"Integration Test"工作流
3. 点击"Run workflow"
4. 配置参数:
   - 设置`run_all_tests`为`true`运行所有测试
   - 可选择覆盖环境变量 (base_url, auth_token等)
   - 指定特定的模型进行测试

#### 环境变量优先级

工作流支持灵活的环境变量配置：

1. **手动输入参数** (最高优先级): workflow_dispatch输入
2. **仓库Secrets** (默认): 存储的加密环境变量
3. **默认值** (兜底): 硬编码的合理默认值

> [!IMPORTANT]
> **本地与 Agent 测试环境配置读取规则**
> 任何开发者或 AI Agent 在进行本地 OpenWebUI 实例测试、编写示例代码、或者运行调试脚本时，**必须**从项目根目录的 `.env` 文件读取测试所需的环境变量：
>
> - `OUI_AUTH_TOKEN`: 认证令牌
> - `OUI_BASE_URL`: OpenWebUI 实例的基础地址（如 `http://localhost:3003`）
> - `OUI_PARALLEL_MODELS`: 并发测试使用的模型列表
> - `OUI_DEFAULT_MODEL`: 默认模型
> - `OUI_CLEANUP_BEFORE_TEST`: 测试是否需要自动清理
> *始终避免将敏感测试凭据硬编码到源码或脚本中。建议使用 `python-dotenv` 加载。*

### 6. 开发最佳实践

#### 功能开发时的测试策略

- **原子化变更**: 每次提交专注于单一功能，便于精确测试
- **本地验证**: 使用本地测试脚本验证变更
- **测试映射检查**: 确认文件变更触发了正确的测试类别
- **CI反馈**: 关注CI结果，必要时手动触发完整测试

#### 测试配置维护

- **定期审查**: 定期检查测试映射的准确性
- **新功能适配**: 新功能开发时同步更新测试映射
- **性能监控**: 关注测试执行时间，优化慢速测试
- **覆盖率检查**: 确保重要代码路径有相应测试覆盖

#### 故障排除指南

- **测试失败分析**: 区分是代码问题还是测试环境问题
- **映射调试**: 使用`detect_required_tests.py`验证文件映射
- **本地复现**: 在本地环境复现CI测试失败
- **环境变量**: 确保所有必需的环境变量正确配置
- **工作流事件调试**: 检查workflow_run事件的SHA上下文是否正确
- **文件变更验证**: 确认文件变更检测逻辑正确识别了修改的文件

#### 常见问题解决

1. **工作流未触发集成测试**:
   - 检查主测试工作流是否成功完成
   - 验证文件变更是否匹配任何映射模式
   - 确认环境变量是否正确设置

2. **文件变更检测失败**:
   - 检查git历史完整性 (`fetch-depth: 0`)
   - 验证分支引用和SHA上下文
   - 确认`detect_required_tests.py`脚本正常运行

3. **矩阵策略测试失败**:
   - 检查测试类别JSON格式是否正确
   - 验证各个测试命令是否可独立执行
   - 确认测试环境依赖项完整安装

### 8. 工作流事件处理详解

#### workflow_run 事件处理

`workflow_run`事件是选择性测试系统的核心触发机制：

```yaml
# 正确的workflow_run配置
on:
  workflow_run:
    workflows: ["Test"]  # 依赖主测试工作流
    types: [completed]   # 只有成功完成后才触发
    branches: [main, master]
```

#### 关键修复点

近期修复了以下关键问题：

1. **SHA上下文获取**:

   ```yaml
   # 修复前: 使用错误的github.sha
   ref: ${{ github.sha }}
   
   # 修复后: 根据事件类型使用正确的SHA
   ref: ${{ github.event_name == 'workflow_run' && github.event.workflow_run.head_sha || github.sha }}
   ```

2. **文件变更检测逻辑**:

   ```bash
   # 增强调试输出
   if [ "${{ github.event_name }}" = "workflow_run" ]; then
     echo "🔍 Workflow run context:"
     echo "  - Head SHA: ${{ github.event.workflow_run.head_sha }}"
     echo "  - Head Branch: ${{ github.event.workflow_run.head_branch }}"
   fi
   ```

3. **环境变量传递**:

   ```yaml
   env:
     WORKFLOW_RUN_HEAD_SHA: ${{ github.event.workflow_run.head_sha }}
     WORKFLOW_RUN_HEAD_BRANCH: ${{ github.event.workflow_run.head_branch }}
     GITHUB_EVENT_NAME: ${{ github.event_name }}
   ```

#### 事件类型优先级

工作流支持多种触发方式，按优先级排序：

1. **workflow_dispatch** (手动触发): 最高优先级，支持完全控制
2. **workflow_run** (自动触发): 标准CI流程
3. **push/pull_request** (直接触发): 开发过程中的即时反馈

#### 测试结果汇总

工作流提供详细的测试结果汇总：

```yaml
integration-test-summary:
  steps:
  - name: Integration Test Summary
    run: |
      echo '${{ needs.detect-changes.outputs.required-tests }}' | jq -r '.[]' | while read category; do
        echo "  ✅ $category"
      done
```

### 9. 高级配置和优化

#### 测试并行度控制

通过GitHub Actions矩阵策略实现最优并行度：

```yaml
strategy:
  matrix:
    test-category: ${{ fromJson(needs.detect-tests.outputs.test-categories) }}
  fail-fast: false  # 关键：允许部分失败继续执行
  max-parallel: 8   # 可选：限制最大并行数
```

#### 条件执行逻辑

智能的条件执行确保资源有效利用：

```yaml
# 只有在测试工作流成功时才执行
if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}

# 只有在检测到相关变更时才执行测试
if: ${{ needs.detect-changes.outputs.required-tests != '[]' }}
```

#### 超时和重试配置

为长时间运行的集成测试配置合理的超时：

```yaml
# 在test-mapping.yml中配置
test_categories:
  comprehensive_demos:
    timeout: 1200  # 10分钟超时
    retry: 2      # 失败时重试2次
```

### 10. 配置文件更新指南

#### 添加新文件映射

当项目结构发生变化时，需要更新文件映射：

```yaml
# 示例：添加新的API模块映射
- pattern: "openwebui_chat_client/**/api_*"
  categories: ["connectivity", "basic_chat"]

# 示例：添加新的示例目录映射  
- pattern: "examples/new_feature/**"
  categories: ["new_feature_test", "comprehensive_demos"]


```

#### 测试类别配置更新

添加新测试类别时的完整配置：

```yaml
test_categories:
  new_feature_test:
    name: "New Feature Integration Test"
    command: "python examples/new_feature/test_new_feature.py"
    description: "Tests new feature functionality"
    timeout: 1200  # 可选：测试超时时间（秒）
    retry: 1      # 可选：失败重试次数
```

#### 验证配置更新

配置更新后的验证步骤：

1. **本地验证测试映射**:

   ```bash
   python .github/scripts/detect_required_tests.py --files "your_changed_file.py" --verbose
   ```

2. **测试命令验证**:

   ```bash
   python .github/scripts/run_all_integration_tests.py --category new_category --verbose
   ```

3. **工作流语法检查**:

   ```bash
   # 使用GitHub CLI验证工作流语法
   gh workflow view integration-test.yml
   ```

---
