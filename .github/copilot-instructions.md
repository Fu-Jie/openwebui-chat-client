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

#### 代码结构
- **主要代码**: `openwebui_chat_client/openwebui_chat_client.py`
- **初始化文件**: `openwebui_chat_client/__init__.py`
- **测试代码**: `tests/test_*.py`
- **示例代码**: `examples/demos.py`, `examples/basic_usage.py`等

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

## CI/CD与发布流程

### 1. GitHub Actions工作流

#### 测试工作流 (test.yml)
- **触发条件**: push到main/master分支，PR到main/master
- **Python版本**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **测试命令**: `python -m unittest discover -s tests -p "test_*.py" -v`

#### 集成测试 (integration-test.yml)
- **用途**: 更全面的集成测试
- **环境**: 可能包含OpenWebUI服务器模拟

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

---

这份指南涵盖了openwebui-chat-client项目的完整开发工作流程，为AI助手提供了全面的开发规范和最佳实践。在进行任何开发工作时，请严格遵循这些指导原则，确保代码质量和项目一致性。