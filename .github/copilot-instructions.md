# OpenWebUI Chat Client - Copilot开发指南

## 项目概述

**openwebui-chat-client** 是一个全面的、有状态的Python客户端库，用于与 [Open WebUI](https://github.com/open-webui/open-webui) API进行智能交互。本项目支持单/多模型聊天、工具使用、文件上传、检索增强生成(RAG)、知识库管理和高级聊天组织功能。

### 核心目标
- **编程方式创建和管理聊天**: 通过代码创建、查询、管理聊天会话，确保与Open WebUI前端完美同步
- **批量与自动化功能**: 提供高效的批量操作和自动化维护脚本
- **全面的API覆盖**: 封装Open WebUI的主要OpenAPI接口，提供功能完整、接口友好的客户端库

### 技术栈
- **主要语言**: Python (>=3.8)
- **核心依赖**: `requests`, `python-dotenv`
- **并发处理**: `concurrent.futures.ThreadPoolExecutor`
- **测试框架**: unittest
- **CI/CD**: GitHub Actions
- **包管理**: PyPI

---

## 开发规范

### 1. 代码风格与结构

#### 命名规范
- 遵循PEP 8编码规范
- 内部辅助方法使用单个下划线前缀（如`_ask`、`_upload_file`）
- 常量和配置项在`__init__`方法中初始化为实例属性
- 优先使用f-string进行字符串格式化

#### 类型提示
- **必须**: 所有函数和方法的参数及返回值都必须有明确的类型提示
- **使用**: `typing`模块中的`Optional`, `List`, `Dict`, `Tuple`, `Union`, `Generator`等
- **示例**:
```python
def chat(self, question: str, chat_title: Optional[str] = None, 
         model_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    pass
```

#### 日志记录
- **关键操作**: 在所有API请求、文件操作、状态变更前后记录日志
- **日志级别**:
  - `logger.info()`: 正常操作流程
  - `logger.warning()`: 警告信息
  - `logger.error()`: 错误信息
  - `logger.debug()`: 详细调试信息（如请求载荷）
- **日志内容**: 必须包含关键上下文信息（如`chat_id`、`model_id`、`file_path`等）

#### 异常处理
- **必须**: 对所有可能失败的操作使用`try...except`块
- **优先**: 捕获具体的异常类型（如`requests.exceptions.RequestException`, `json.JSONDecodeError`, `KeyError`）
- **避免**: 宽泛的`except Exception`
- **要求**: 在`except`块中使用`logger.error()`记录详细错误信息

### 2. 架构原则

#### 状态持久化
- 客户端的所有操作都应与Open WebUI后端同步
- 通过API所做的更改必须能够持久化并反映在UI上
- 维护聊天会话状态的一致性

#### 原子化与批量化
- 提供原子化的API操作方法
- 在原子操作基础上构建批量处理方法
- 满足不同层次的自动化需求

#### 用户友好与健壮性
- 提供清晰的日志记录和精细的异常处理
- 所有与外部交互的方法都必须有明确的成功/失败返回
- 方便用户进行调试和集成

---

## 开发工作流

### 1. 功能开发流程

#### 新功能开发
1. **需求分析**: 确保新功能符合项目核心目标
2. **API设计**: 在`openwebui_chat_client/openwebui_chat_client.py`中添加新方法
3. **编码规范**: 严格遵循上述编码规范
4. **示例代码**: 在`examples/`目录下添加相应示例
5. **单元测试**: 在`tests/`目录下添加对应测试
6. **集成测试映射**: 更新`.github/test-mapping.yml`以包含新功能的测试映射

#### 代码结构
- **主要代码**: `openwebui_chat_client/openwebui_chat_client.py`
- **初始化文件**: `openwebui_chat_client/__init__.py`
- **测试代码**: `tests/test_*.py`
- **示例代码**: `examples/` 目录下按功能分类组织

### 2. 测试要求

#### 测试覆盖
- **单元测试**: 每个新功能都必须有对应的单元测试
- **集成测试**: 关键功能需要集成测试
- **测试命令**: `python -m unittest discover -s tests -p "test_*.py" -v`

#### 测试分类
- `test_openwebui_chat_client.py`: 主要客户端功能测试
- `test_chat_functionality.py`: 聊天功能测试
- `test_knowledge_base.py`: 知识库功能测试
- `test_notes_functionality.py`: 笔记功能测试
- `test_error_handling.py`: 错误处理测试

#### 测试编写原则
- 使用`unittest.mock`模拟外部依赖
- 测试应该独立且可重复
- 包含正常情况和异常情况的测试

### 3. 文档维护

#### 必须更新的文档
- **README.md**: 英文版本功能说明和使用指南
- **README.zh-CN.md**: 中文版本功能说明和使用指南
- **CHANGELOG.md**: 版本变更记录
- **CHANGELOG.zh-CN.md**: 中文版本变更记录

#### 文档更新要求
- 新功能必须在README中添加使用示例
- API变更必须在CHANGELOG中记录
- 文档应与代码保持同步
- 示例代码必须可执行且有效

#### CHANGELOG 管理规范
- **每次功能修改都必须更新 CHANGELOG**: 无论修改大小，任何与**模型功能**相关的增加、修改或修复都必须在 CHANGELOG 中记录。
- **未发布更改标记**: 在没有版本发布要求时，所有更改都应添加到 `[未发布]` / `[Unreleased]` 部分。
- **版本发布时转换**: 只有在正式版本发布时，才将 `[未发布]` 部分转换为具体版本号（如 `[0.1.14]`）。
- **README 更新时机**: README 文件只在版本发布时才进行更新，平时的功能修改不更新 README。
- **双语同步**: CHANGELOG.md 和 CHANGELOG.zh-CN.md 必须同时更新，保持内容一致。
- **变更分类**: 使用标准分类：`Added`/`新增`、`Changed`/`变更`、`Fixed`/`修复`、`Removed`/`移除`。
- **详细描述**: 每个变更项都应包含清晰的**模型功能**描述和影响范围。

#### 版本发布流程中的文档更新
1. **功能开发阶段**: 只更新 CHANGELOG 的 `[未发布]` 部分，不更新 README。
2. **版本发布准备**: 将 `[未发布]` 更改为具体版本号和发布日期。
3. **版本发布时**: 同时更新 README 文件以反映新功能和 API 变更。
4. **发布完成后**: 在 CHANGELOG 顶部添加新的 `[未发布]` 部分，准备下一轮开发。

---

## API设计标准

### 1. 方法命名规范

#### 核心方法类型
- **聊天相关**: `chat()`, `stream_chat()`, `parallel_chat()`
- **管理相关**: `list_*()`, `get_*()`, `create_*()`, `update_*()`, `delete_*()` 
- **批量操作**: `*_all()`, `*_by_keyword()`
- **状态管理**: `rename_*()`, `set_*()`, `switch_*()`

#### 参数设计原则
- **必需参数**: 放在前面，类型明确
- **可选参数**: 使用默认值，支持None
- **批量参数**: 使用List类型，支持空列表
- **标识参数**: 使用字符串ID，支持验证

### 2. 返回值标准

#### 成功返回
- **单一对象**: 返回Dict包含核心数据和元数据
- **列表对象**: 返回List[Dict]或空列表
- **操作结果**: 返回包含状态和相关ID的Dict

#### 失败处理
- **返回None**: 当操作失败且可恢复时
- **抛出异常**: 当遇到不可恢复的错误时
- **记录日志**: 所有失败情况都必须记录详细日志

### 3. 并发处理

#### ThreadPoolExecutor使用
- 用于并行API请求
- 提升批量操作效率
- 合理控制并发数量

#### 示例模式
```python
def parallel_operation(self, items: List[str]) -> Dict[str, Any]:
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_item = {
            executor.submit(self._single_operation, item): item 
            for item in items
        }
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                results[item] = future.result()
            except Exception as e:
                logger.error(f"Failed to process {item}: {e}")
                results[item] = None
    return results
```

---

---

## 选择性集成测试系统

### 1. 测试系统概述

#### 智能测试选择
openwebui-chat-client项目采用**智能选择性集成测试系统**，根据代码变更自动选择相关测试类别，显著提升CI效率：

- **变更分析**: 自动分析PR/push中的文件变更
- **模式匹配**: 根据`.github/test-mapping.yml`配置映射测试类别
- **并行执行**: 使用GitHub Actions矩阵策略并行运行
- **手动覆盖**: 提供完整测试的手动触发选项

#### 测试效率提升
- **优化前**: 每次变更运行全部7个集成测试类别
- **优化后**: 仅运行相关测试类别（通常1-3个）
- **时间节省**: CI运行时间减少60-80%
- **资源节约**: 显著降低GitHub Actions使用量

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

| 类别 | 用途 | 触发条件 |
|------|------|----------|
| `connectivity` | 基础连接验证 | 核心文件、配置变更 |
| `basic_chat` | 基础聊天功能 | 聊天相关代码变更 |
| `notes_api` | 笔记API功能 | 笔记相关文件变更 |
| `rag_integration` | RAG集成测试 | RAG、知识库相关变更 |
| `model_management` | 模型管理 | 模型相关功能变更 |
| `model_switching` | 模型切换 | 模型切换功能变更 |
| `comprehensive_demos` | 综合演示 | 复杂功能、示例变更 |

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
# 使用矩阵策略并行运行选定的测试类别
strategy:
  matrix:
    test-category: ${{ fromJson(needs.detect-tests.outputs.test-categories) }}
  fail-fast: false  # 允许部分测试失败时继续其他测试

# 动态检测需要运行的测试
detect-tests:
  outputs:
    test-categories: ${{ steps.detect.outputs.categories }}
```

#### 手动触发完整测试
开发者可以通过GitHub UI手动触发完整测试：

1. 访问Actions页面
2. 选择"Integration Test"工作流
3. 点击"Run workflow"
4. 设置`run_all_tests`为`true`

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

### 7. 配置文件更新指南

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
    timeout: 300  # 可选：测试超时时间（秒）
    retry: 1      # 可选：失败重试次数
```

---

## CI/CD与发布流程

### 1. GitHub Actions工作流

#### 测试工作流 (test.yml)
- **触发条件**: push到main/master分支，PR到main/master
- **Python版本**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **测试命令**: `python -m unittest discover -s tests -p "test_*.py" -v`

#### 集成测试 (integration-test.yml)
- **用途**: 更全面的集成测试，采用智能选择性测试
- **环境**: 真实OpenWebUI服务器环境
- **选择性测试**: 根据变更文件自动选择相关测试类别
- **并行执行**: 使用GitHub Actions矩阵策略并行运行测试

#### 发布工作流 (publish.yml)
- **触发条件**: 推送标签 `v*`
- **流程**: 测试 -> 构建 -> 发布到PyPI -> 创建GitHub Release
- **依赖**: PYPI_API_TOKEN密钥

#### 版本号规范
- 遵循语义化版本控制 (Semantic Versioning)
- 格式: `MAJOR.MINOR.PATCH`
- 当前版本: 0.1.12

---

## 特定功能开发指南

### 1. 聊天功能

#### 核心方法实现要点
- **状态管理**: 维护`self.chat_id`和`self.chat_object_from_server`
- **模型切换**: 支持在同一聊天中切换模型
- **流式响应**: 实现实时内容更新
- **错误恢复**: 处理网络中断和API错误

#### 重要实现细节
- 自动生成聊天标题和标签
- 支持文件上传和多模态输入
- RAG集成（文件和知识库）
- 工具调用支持

### 2. 知识库管理

#### 设计原则
- **CRUD操作**: 完整的创建、读取、更新、删除功能
- **批量处理**: 支持批量创建和删除
- **文件管理**: 支持向知识库添加文件
- **搜索功能**: 按名称搜索和过滤

#### 实现要点
- 异步文件上传处理
- 知识库状态监控
- 错误重试机制

### 3. 模型管理

#### 功能覆盖
- **列表操作**: `list_models()`, `list_base_models()`
- **详情获取**: `get_model()`带自动重试
- **创建更新**: `create_model()`, `update_model()` 
- **删除操作**: `delete_model()`

#### 特殊处理
- 自动创建重试机制
- 模型ID验证
- 配置参数验证

---

## 调试与故障排除

### 1. 常见问题

#### 认证错误
- 检查Bearer token有效性
- 验证API密钥配置
- 确认权限设置

#### 模型未找到
- 验证模型ID正确性（如`"gpt-4.1"`, `"gemini-2.5-flash"`）
- 确认模型在Open WebUI实例中可用
- 检查模型配置

#### 工具未找到
- 确认`tool_ids`匹配Open WebUI设置中配置的工具ID
- 验证工具权限和可用性

#### 文件上传问题
- 检查文件路径正确性
- 验证应用程序文件读取权限
- 确认文件格式支持

### 2. 日志调试

#### 启用详细日志
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

#### 日志级别说明
- `INFO`: 正常操作流程
- `WARNING`: 可恢复的问题
- `ERROR`: 需要注意的错误
- `DEBUG`: 详细的调试信息

---

## 未来发展方向

### 1. API同步
- 持续关注OpenWebUI官方更新
- 新API优先适配
- 向后兼容性维护

### 2. 效率提升
- 开发更多自动化功能
- 优化批量操作性能
- 增强并发处理能力

### 3. 功能扩展
- 更多RAG集成选项
- 增强的聊天组织功能
- 高级分析和监控功能

---

## Copilot使用指南

### 1. 代码生成原则
- 严格遵循现有代码风格
- 保持类型提示完整性
- 添加适当的日志记录
- 包含异常处理

### 2. 功能扩展建议
- 基于现有方法模式实现新功能
- 优先考虑用户体验和API一致性
- 充分测试边界情况
- 更新相关文档

### 3. 问题解决策略
- 查看现有类似实现
- 参考测试用例了解预期行为
- 检查日志输出定位问题
- 参考Open WebUI API文档

### 4. 最佳实践
- 小步迭代，频繁测试
- 保持代码简洁易读
- 充分利用现有工具和方法
- 注重向后兼容性

### 5. 选择性集成测试使用
- **测试映射维护**: 新功能开发时同步更新`.github/test-mapping.yml`
- **本地测试验证**: 使用`run_integration_tests.py`在本地验证测试
- **CI优化意识**: 避免不必要的测试触发，提高CI效率
- **配置文件理解**: 熟悉测试类别和文件映射规则

---

这份指南涵盖了openwebui-chat-client项目的完整开发工作流程，为AI助手提供了全面的开发规范和最佳实践。在进行任何开发工作时，请严格遵循这些指导原则，确保代码质量和项目一致性。

---

## API文档维护规范

### 1. API Reference 组织原则

#### 功能分组标准
- **聊天操作 (💬 Chat Operations)**: 核心对话功能
  - `chat()`, `stream_chat()`, `parallel_chat()`
  - 这些是用户最常用的核心功能，优先展示
  
- **聊天管理 (🛠️ Chat Management)**: 聊天会话管理
  - `rename_chat()`, `set_chat_tags()`, `update_chat_metadata()`, `switch_chat_model()`, `create_folder()`
  - 组织和管理现有聊天的功能
  
- **模型管理 (🤖 Model Management)**: 模型CRUD操作
  - `list_models()`, `get_model()`, `create_model()`, `update_model()`, `delete_model()`
  - 模型的完整生命周期管理
  
- **知识库操作 (📚 Knowledge Base Operations)**: RAG相关功能
  - 知识库的创建、管理、删除和批量操作
  - 文件上传和知识库关联
  
- **笔记API (📝 Notes API)**: 笔记管理功能
  - 笔记的CRUD操作和元数据管理

#### 表格结构规范
- **方法名称**: 使用代码格式 `method_name()`
- **说明**: 简洁明了的功能描述，突出关键特性
- **参数**: 列出主要参数，使用逗号分隔，复杂对象用简化名称

#### 返回值文档化
- **提供具体示例**: 展示实际返回的数据结构
- **说明关键字段**: 解释重要字段的含义和用途
- **区分操作类型**: 不同类型操作的返回值格式

### 2. 文档同步维护流程

#### 双语文档一致性
- **英文优先**: 先更新英文版本，确保术语准确
- **中文同步**: 立即同步中文版本，保持结构一致
- **格式统一**: 确保表格格式、emoji使用、章节结构完全一致

#### 版本控制要求
- **原子化提交**: 英文和中文文档在同一个commit中更新
- **清晰的commit message**: 说明文档更新的具体内容
- **交叉引用检查**: 确保内部链接在两个版本中都有效

### 3. API文档质量标准

#### 完整性要求
- **无遗漏**: 所有公共方法都必须在API Reference中有文档
- **参数完整**: 所有重要参数都要列出，可选参数要标明
- **返回值明确**: 清晰说明返回值的类型和结构

#### 准确性验证
- **代码同步**: 文档必须与实际代码实现保持同步
- **示例有效**: 所有代码示例必须可以实际运行
- **链接检查**: 确保所有内部和外部链接都有效

#### 可用性优化
- **逻辑分组**: 按功能逻辑分组，便于查找
- **搜索友好**: 使用准确的关键词和描述
- **层次清晰**: 合理的标题层次和结构

### 4. 文档更新触发条件

#### 必须更新文档的情况
- **新增API方法**: 添加新的公共方法
- **参数变更**: 修改方法签名、添加/删除参数
- **返回值变更**: 修改返回值结构或类型
- **行为变更**: 方法行为有重大变化

#### 文档审查检查项
- **功能分组正确**: 新方法归类到正确的功能组
- **描述准确简洁**: 功能描述准确且不冗余
- **参数列表完整**: 重要参数都已列出
- **中英文一致**: 两个版本的结构和内容保持一致

### 5. 自动化文档维护

#### 文档生成辅助
- **参数提取**: 从代码注释中提取参数信息
- **返回值示例**: 根据代码生成返回值示例
- **链接检查**: 定期检查文档中的链接有效性

#### 质量检查自动化
- **格式一致性**: 检查表格格式和markdown结构
- **双语同步检查**: 验证中英文版本的章节对应关系
- **完整性验证**: 确保所有公共API都有文档

### 6. README.md 维护最佳实践

#### 主README.md结构原则
- **用户导向**: 以用户使用流程为主线组织内容
- **渐进式**: 从简单示例到复杂功能
- **完整性**: 涵盖安装、配置、使用、故障排除

#### examples/README.md管理
- **目录同步**: 确保目录结构描述与实际文件结构一致
- **示例分类**: 按功能和复杂度进行合理分类
- **运行指导**: 提供清晰的运行前提和步骤

#### 链接维护
- **相对路径**: 使用相对路径确保在不同环境中的可访问性
- **定期检查**: 验证所有链接的有效性
- **标准化**: 统一链接格式和命名规范

---

## 故障排除文档规范

### 1. 常见问题分类

#### 环境配置问题
- **认证错误**: Bearer token相关问题
- **连接问题**: 网络和服务器连接失败
- **依赖问题**: Python包和版本兼容性

#### 功能使用问题
- **模型相关**: 模型ID、可用性、权限问题
- **文件操作**: 上传、路径、权限问题
- **API调用**: 参数错误、返回值异常

#### 性能和稳定性
- **并发问题**: 多线程和异步操作
- **内存使用**: 大文件处理和批量操作
- **网络超时**: 长时间操作和重试机制

### 2. 解决方案文档化

#### 问题描述标准
- **症状描述**: 清晰描述用户遇到的现象
- **错误信息**: 提供具体的错误消息示例
- **环境信息**: 说明问题发生的环境条件

#### 解决步骤格式
- **分步骤**: 将解决方案分解为可操作的步骤
- **代码示例**: 提供具体的代码修复示例
- **验证方法**: 说明如何验证问题是否解决

### 3. 预防性文档

#### 最佳实践指导
- **配置建议**: 推荐的配置和设置方式
- **使用模式**: 推荐的API使用模式和反模式
- **性能优化**: 提高性能和稳定性的建议

#### 注意事项
- **限制说明**: 明确API的限制和约束
- **兼容性**: 说明版本兼容性和升级注意事项
- **安全建议**: 关于API密钥和数据安全的指导

---

## 示例代码开发规范

### 1. 示例目录结构

#### 目录组织
```
examples/
├── README.md                     # 示例总览和使用指南
├── config/                       # 配置和环境设置
│   ├── basic_config.py          # 基础客户端配置
│   └── environment_setup.py     # 环境变量设置指南
├── getting_started/              # 入门示例
│   ├── hello_world.py           # 最简单的使用示例
│   ├── basic_chat.py            # 基础聊天功能
│   └── quick_start.py           # 快速开始指南
├── chat_features/                # 聊天功能示例
│   ├── streaming_chat.py        # 流式聊天
│   ├── parallel_chat.py         # 并行多模型聊天
│   ├── follow_up_suggestions.py # 后续建议功能
│   ├── chat_with_images.py      # 多模态聊天
│   └── chat_management.py       # 聊天管理功能
├── rag_knowledge/                # RAG和知识库示例
│   ├── file_rag.py              # 文件RAG
│   ├── knowledge_base.py        # 知识库管理
│   ├── batch_knowledge_ops.py   # 批量知识库操作
│   └── advanced_rag.py          # 高级RAG功能
├── model_management/             # 模型管理示例
│   ├── list_models.py           # 列出可用模型
│   ├── model_operations.py      # 模型CRUD操作
│   └── model_switching.py       # 模型切换
├── notes_api/                    # 笔记API示例
│   ├── basic_notes.py           # 基础笔记操作
│   └── advanced_notes.py        # 高级笔记管理
├── advanced_features/            # 高级功能示例
│   ├── real_time_streaming.py   # 实时流式更新
│   ├── concurrent_operations.py # 并发操作
│   ├── error_handling.py        # 错误处理模式
│   └── custom_tools.py          # 自定义工具使用
├── comprehensive/                # 综合示例
│   ├── full_demo.py             # 全功能演示
│   └── use_case_scenarios.py    # 实际用例场景
└── utils/                        # 工具和辅助函数
    ├── example_base.py          # 示例基类
    ├── file_helpers.py          # 文件操作辅助
    └── test_data.py             # 测试数据生成
```

### 2. 示例代码标准

#### 文件结构模板
每个示例文件都应遵循以下模板结构：

```python
#!/usr/bin/env python3
"""
示例功能的简要描述。

本示例演示的功能：
- 功能1
- 功能2
- 功能3

要求：
- 环境变量: OUI_BASE_URL
- 环境变量: OUI_AUTH_TOKEN
- 模型可用性: 特定模型（如果需要）

使用方法：
    python examples/category/example_name.py
"""

import logging
import os
from typing import Optional, Dict, Any

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# 日志设置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """演示示例功能的主函数。"""
    # 验证环境变量
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN 环境变量未设置")
        return
    
    # 客户端初始化
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ 客户端初始化成功")
    except Exception as e:
        logger.error(f"❌ 客户端初始化失败: {e}")
        return
    
    # 示例实现
    # ... 你的示例代码 ...
    
    logger.info("🎉 示例执行完成")


if __name__ == "__main__":
    main()
```

#### 命名规范
- **文件名**: 使用 `snake_case.py`，描述性命名
- **函数名**: 遵循 PEP 8，使用 `snake_case`
- **类名**: 使用 `PascalCase`
- **常量**: 使用 `UPPER_SNAKE_CASE`

#### 代码规范
- **导入顺序**: 标准库 → 第三方库 → 本地库
- **环境变量**: 统一的环境变量处理方式
- **错误处理**: 适当的异常处理和日志记录
- **类型提示**: 完整的类型注解
- **文档**: 清晰的docstring和注释

#### 文档规范
- **文件头部**: 功能描述、演示功能列表、要求、使用方法
- **函数文档**: 清晰的参数和返回值描述
- **注释**: 解释复杂逻辑的有意义注释
- **错误消息**: 用户友好的错误消息

### 3. 示例开发流程

#### 新示例开发
1. **需求分析**: 确定要演示的功能和目标用户
2. **分类放置**: 根据功能将示例放在合适的目录中
3. **遵循模板**: 使用标准模板结构
4. **功能实现**: 实现核心演示功能
5. **测试验证**: 确保示例可以正常运行
6. **文档更新**: 更新相关README和说明

#### 示例质量标准
- **可执行性**: 示例必须可以直接运行
- **教育性**: 代码清晰易懂，有教育价值
- **完整性**: 包含必要的错误处理和验证
- **一致性**: 遵循项目的代码风格和约定
- **实用性**: 演示真实的使用场景

### 4. 环境变量规范

#### 标准环境变量
所有示例都应支持以下环境变量：

```bash
# 必需
export OUI_BASE_URL="http://localhost:3000"
export OUI_AUTH_TOKEN="your_api_token_here"

# 可选
export OUI_DEFAULT_MODEL="gpt-4.1"
export OUI_PARALLEL_MODELS="gpt-4.1,gemini-2.5-flash"
export OUI_RAG_MODEL="gemini-2.5-flash"
export OUI_MULTIMODAL_MODEL="gpt-4.1"
```

#### 环境变量处理
- **加载方式**: 使用 `python-dotenv` 加载 `.env` 文件
- **默认值**: 为可选变量提供合理的默认值
- **验证**: 验证必需的环境变量是否设置
- **错误提示**: 提供清晰的设置指导

### 5. 工具类使用

#### 基础类
- **ExampleBase**: 所有示例的基类，提供通用功能
- **FileHelper**: 文件操作辅助工具
- **TestDataGenerator**: 测试数据生成工具

#### 使用模式
```python
from utils.example_base import ExampleBase

class MyExample(ExampleBase):
    def run_example(self):
        # 示例实现
        pass

example = MyExample("my_example", "演示某功能")
example.run()
```
