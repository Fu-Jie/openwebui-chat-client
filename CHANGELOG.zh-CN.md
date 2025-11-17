# 更新日志

本项目的所有显著更改都将记录在此文件中。

## [0.1.22] - 2025-11-18

### 新增

- **自主任务处理**：引入了 `process_task` 和 `stream_process_task` 方法，使客户端能够以工具和知识库支持执行多步骤、迭代式问题解决。
- **单元测试**：为新的自主任务处理功能添加了完整的测试套件。

### 修复

- **CI 测试执行**：通过优化测试执行策略解决了多个 CI 失败问题。此修复确保在 CI 中仅运行单元测试（排除集成测试），并正确处理所有 Python 版本的测试模块发现。

## [0.1.21] - 2025-10-03

### 修复

- 单元测试：更新 `list_custom_models` 测试，使端点改为 `/api/v1/models`。
- CI 选择性测试：改进 `.github/test-mapping.yml`，将核心客户端变更映射到 `model_management`，并确保 `tests/test_openwebui_chat_client.py` 会触发相应测试类别。
- CI 工作流：在 `integration-test.yml` 的手动全量运行覆盖中补全 `prompts_api` 与 `deep_research`，与测试映射保持一致。

## [0.1.20] - 2025-10-02

### 修复

- **模型列表方法文档和API端点**：改进了 `list_models`、`list_base_models` 和 `list_custom_models` 方法的文档，以澄清其行为和对应的UI元素。将 `list_custom_models` API端点从 `/api/v1/models/custom` 更新为 `/api/v1/models`，以提高一致性。

## [0.1.19] - 2025-09-23

### 修复

- **工具ID参数格式**：修复 `ChatManager._get_model_completion` 正确地将 `tool_ids` 作为直接列表传递，而不是转换为OpenAI风格的 `tools` 格式，确保与 Open WebUI API 的正确工具集成。

## [0.1.18] - 2025-09-14

### 修复

- **模型更新：tags 字段处理**：修复 `ModelManager.update_model` 在更新模型时对 `meta.tags` 字段的处理，正确将 tag 字符串列表转换为 API 期望的 [{"name": tag}] 格式，避免意外覆盖已有标签。
- **模型更新：base_model_id 处理**：修复 `ModelManager.update_model` 对 `base_model_id` 的处理，确保在提供时更新该字段，未提供时保留原值，防止被意外清空或错误赋值。
- **模型列表：强制刷新**：修复 `ModelManager.list_models` 在API请求中包含 `refresh=true` 参数，强制从服务器刷新模型列表，确保获取最新的可用模型。

## [0.1.17] - 2025-08-23

### 新增

- **深度研究代理**: 新增 `deep_research` 方法，这是一个自主代理，能对指定主题进行多步骤研究，并能在通用模型和搜索模型之间进行智能路由选择。
- **HTTP重试机制**: 在底层客户端中实现了稳健的API调用重试策略，在遇到瞬时的服务端错误（5xx）时自动重试，以提高稳定性。

### 修复

- **`create_model`有效载荷**: 修复了 `create_model` 方法，使其能发送完整、准确的请求体，包括含有`capabilities`、`tags`等信息的`meta`对象，并修正了错误的API端点为 `/api/v1/models/create`。

## [0.1.16] - 2025-08-10

### 新增

- **提示词管理系统**: 完整实现提示词功能
  - `PromptsManager` 模块用于管理带变量替换的自定义提示词
  - 完整的 CRUD 操作：`get_prompts()`、`create_prompt()`、`update_prompt_by_command()`、`delete_prompt_by_command()`
  - 高级变量提取和替换功能：`extract_variables()` 和 `substitute_variables()`
  - 系统变量支持：`CURRENT_DATE`、`CURRENT_TIME`、`CURRENT_DATETIME`、`CURRENT_WEEKDAY`、`CURRENT_TIMEZONE`
  - 交互式提示词表单，支持类型化变量（text、textarea、select、number、date、checkbox 等）
  - 搜索功能：`search_prompts()` 支持按命令、标题或内容过滤
  - 批量操作：`batch_create_prompts()` 和 `batch_delete_prompts()` 用于高效批量管理
  - 在 `examples/prompts_api/` 中提供全面示例，包含基础和高级使用模式
  - 在 `tests/test_prompts_functionality.py` 中提供完整测试覆盖
  - 集成 CI 测试映射以实现自动化测试

## [0.1.15] - 2025-08-04

### 新增

- **连续对话功能**: 新的高级对话自动化功能
  - `continuous_chat()`: 使用追问建议进行单模型自动多轮对话
  - `continuous_parallel_chat()`: 并行多模型自动多轮对话
  - `continuous_stream_chat()`: 实时流式响应的自动多轮对话
  - 自动追问生成和随机选择，实现自然对话流程
  - 当无追问可用时提供通用回退问题，确保对话连续性
  - 支持所有现有聊天参数：模型选择、文件夹、标签、RAG文件/集合、工具等
  - 全面的对话历史跟踪和元数据收集
  - 在 `tests/test_continuous_conversation.py` 中提供专门的单元测试，覆盖率完整
  - 在 `examples/advanced_features/continuous_conversation.py` 中提供演示示例

## [0.1.14] - 2025-08-02

### 0.1.14 中新增

- **模块化架构重构**: 将代码库完全重构为模块化组件：
  - `openwebui_chat_client/core/base_client.py`: 核心客户端功能基类
  - `openwebui_chat_client/modules/chat_manager.py`: 专用聊天管理模块
  - `openwebui_chat_client/modules/file_manager.py`: 文件操作管理
  - `openwebui_chat_client/modules/knowledge_base_manager.py`: 知识库操作
  - `openwebui_chat_client/modules/model_manager.py`: 模型管理功能
  - `openwebui_chat_client/modules/notes_manager.py`: 笔记 API 管理
- **扩展的示例套件**: 新的全面示例和工具：
  - `examples/advanced_features/archive_chats.py`: 聊天归档功能演示
  - `examples/chat_features/model_switching.py`: 模型切换示例
  - `examples/config/`: 配置和环境设置示例
  - `examples/utils/`: 示例脚本的共享工具
  - 增强的 `examples/README.md` 文档
- **全面的测试套件**: 使用新测试文件扩展测试覆盖：
  - `tests/test_archive_functionality.py`: 归档功能测试
  - `tests/test_changelog_extraction.py`: 更新日志处理测试
  - `tests/test_documentation_structure.py`: 文档验证测试
  - `tests/test_model_permissions.py`: 模型权限测试
- **聊天归档功能**: 添加了聊天归档功能，并附带全面的测试和示例。
- **批量模型权限更新**: 实现了批量模型权限更新功能。

### 0.1.14 中的变更

- **代码组织**: 从单体结构迁移到模块化架构，同时保持向后兼容性。
- **API 响应验证**: 修复了 API 响应验证和数据格式不匹配的关键问题。
- **状态同步**: 解决了客户端和服务器之间的状态同步问题。
- **测试基础设施**: 改进了测试可靠性和集成测试连接性。
- **文档**: 全面更新所有文档文件，提高清晰度和完整性。
- **模型切换示例**: 更新了 `model_switching.py`。
- **列出聊天页面参数**: 将 `list_chats` 方法的 `page` 参数改回可选。

### 0.1.14 中的修复

- **关键测试失败**: 解决了与模块化重构、API 端点、响应验证、聊天对象同步以及模拟方法委托相关的多个测试失败。
- **API 数据格式问题**: 修复了 API 响应中的数据格式不匹配。
- **状态管理**: 纠正了状态同步问题。
- **模型配置**: 修复了任务模型配置问题。
- **集成连接性**: 解决了集成测试连接性问题以及通过在客户端初始化期间阻止 HTTP 请求来解决关键测试连接性问题。
- **知识库删除操作**: 完成了知识库删除操作的修复，并进行了适当的 `ThreadPoolExecutor` 委托。
- **API 端点和返回值问题**: 修复了笔记和知识库操作中关键的 API 端点和返回值问题。
- **追问测试失败**: 实现了从配置 API 正确获取任务模型以修复追问测试失败。
- **缺失的关键方法**: 实现了缺失的关键方法：`archive_chats_by_age`、`_get_chat_details`、`_cleanup_unused_placeholder_messages`。
- **方法签名和返回类型**: 修复了向后兼容的方法签名和返回类型。
- **API 兼容性问题**: 修复了重构后的模块化客户端中的 API 兼容性问题。

## [0.1.13] - 2025-07-28

### 0.1.13 中新增

- **笔记管理 API**: 完整实现笔记管理功能，提供全面的 CRUD 操作：
  - `get_notes()`: 获取当前用户的所有笔记及详细信息
  - `get_notes_list()`: 获取简化的笔记列表，仅包含 id、标题和时间戳
  - `create_note()`: 创建新笔记，支持标题、数据、元数据和访问控制
  - `get_note_by_id()`: 通过 ID 获取特定笔记
  - `update_note_by_id()`: 更新现有笔记的内容和元数据
  - `delete_note_by_id()`: 通过 ID 删除笔记
- **笔记 API 示例**: 添加了完整的示例脚本 `examples/notes_api/basic_notes.py`，演示所有笔记功能
- **笔记单元测试**: 在 `tests/test_notes_functionality.py` 中添加了完整的测试覆盖，包含 118 个测试用例

### 0.1.13 中的变更

- **精简发布流程**: 简化和优化了发布流程文档，移除了冗余步骤，提高了清晰度。
- **增强开发基础设施**: 改进了 GitHub 工作流、CI/CD 设置和开发工具，以提高可维护性。
- **更新项目组织**: 优化了项目结构和文档组织，以提供更好的开发者体验。

## [0.1.12] - 2025-07-27

### 0.1.12 中新增

- **自动元数据生成**: 为 `chat`、`parallel_chat` 和 `stream_chat` 方法增加了 `enable_auto_tagging` 和 `enable_auto_titling` 参数，用于自动为对话生成并应用标签和标题。
- **手动元数据更新**: 引入了新的公共方法 `update_chat_metadata`，允许用户通过提供 `chat_id` 来为现有对话重新生成和更新标签和/或标题。
- **增强的返回值**: 当相应功能启用时，`chat`、`parallel_chat` 和 `stream_chat` 方法现在会在其响应字典中返回 `suggested_tags` 和 `suggested_title`。
- **单元测试和演示**: 添加了 `tests/test_metadata_features.py` 以测试新的元数据功能，并在 `examples/demos.py` 中增加了一个新的演示来展示其用法。

## [0.1.12] - 2025-07-27

### 0.1.12 中新增

- **自动元数据生成**: 为 `chat`、`parallel_chat` 和 `stream_chat` 方法增加了 `enable_auto_tagging` 和 `enable_auto_titling` 参数，用于自动为对话生成并应用标签和标题。
- **手动元数据更新**: 引入了新的公共方法 `update_chat_metadata`，允许用户通过提供 `chat_id` 来为现有对话重新生成和更新标签和/或标题。
- **增强的返回值**: 当相应功能启用时，`chat`、`parallel_chat` 和 `stream_chat` 方法现在会在其响应字典中返回 `suggested_tags` 和 `suggested_title`。
- **单元测试和演示**: 添加了 `tests/test_metadata_features.py` 以测试新的元数据功能，并在 `examples/demos.py` 中增加了一个新的演示来展示其用法。

## [0.1.11] - 2025-07-26

### 0.1.11 中新增

- **流式聊天实时更新优化**: 在 `stream_chat` 方法中增加了实时增量内容推送功能。通过调用 `/api/v1/chats/{chat_id}/messages/{message_id}/event` 接口，在流式生成内容的同时将每个内容块实时推送到 Open WebUI 前端，实现打字机效果的实时更新体验。
- 增加了 `_stream_delta_update` 私有方法，用于流式聊天期间的实时增量内容更新。
- 增加了 `examples/stream_chat_demo.py` 演示脚本，用于增强的流式功能。
- **聊天追问生成选项**: 增加了对聊天方法中追问生成选项的支持。
- 在 OpenWebUIClient 初始化期间自动加载可用的模型 ID。
- 增强了 `get_model` 方法，使其在模型不存在且 API 返回 401 时自动尝试创建模型并重试获取。

### 0.1.11 中变更

- 在 `get_model` 方法中增加了对空 `model_id` 和本地可用模型列表的检查。
- 增强了 `_ask_stream` 方法，使其包含实时增量更新，同时保持向后兼容性。

## [0.1.10] - 2025-07-20

### 0.1.10 中新增

- 增加了 `stream_chat` 方法，用于单模型流式聊天功能。
- 增加了 `delete_all_knowledge_bases` 方法，用于删除所有知识库。
- 增加了 `delete_knowledge_bases_by_keyword` 方法，用于按名称关键词删除知识库。
- 增加了 `create_knowledge_bases_with_files` 方法，用于批量创建知识库并添加文件。

---

## [0.1.9] - 2025-07-13

### 0.1.9 中新增

- 增加了 `list_custom_models` 方法，用于列出用户创建的自定义模型。
- 增加了 `switch_chat_model` 方法，用于支持在现有聊天中切换模型。

### 0.1.9 中变更

- 重构了 `list_models` 和 `list_base_models` 方法，以改进日志记录和健壮的响应处理。

### 0.1.9 中修复

- 纠正了 `list_models` 和 `list_base_models` 可能因意外的 API 响应格式而返回不正确数据的问题。

---

## [0.1.8] - 2025-07-08

### 0.1.8 中变更

- 统一了 `chat` 和 `parallel_chat` 的返回格式，以始终提供详细的响应对象，包括 `chat_id` 和消息标识符。
- 改进了日志记录和错误处理，以实现更健壮的 API 交互。

### 0.1.8 中修复

- 纠正了 `tool_ids` 参数格式，以确保在 API 请求中正确使用工具。

---

## [0.1.7] - 2025-06-27

### 0.1.7 中新增

- 改进并重构了 README 文档。
- 增加了对 `chat`/`parallel_chat` 中 `tool_ids` 和 `image_paths` 参数的支持。
- 增强了 API 参考和使用示例。

### 0.1.7 中变更

- 各种文档和可用性改进。

---

## [0.1.6] - 2025-06-25

### 0.1.6 中新增

- 模型管理：列出、创建、更新、删除自定义模型。
- 知识库管理：创建、添加文件、查询。
- 聊天组织：文件夹、标签、重命名、移动。
- RAG（检索增强生成）支持。
- 基本错误处理和日志记录。

### 0.1.6 中变更

- 改进了错误消息和日志记录。
- 次要错误修复。

---

## [0.1.5] - 2025-06-24

### 0.1.5 中新增

- 支持聊天文件夹和在文件夹之间移动聊天。
- 标记和重命名聊天。

### 0.1.5 中变更

- 改进了聊天会话缓存。

---

## [0.1.4] - 2025-06-23

### 0.1.4 中新增

- 并行模型聊天（一次对话中的多模型 A/B 测试）。
- 更健壮的会话和文件上传缓存。

### 0.1.4 中变更

- 重构了聊天和模型 API 以实现可扩展性。

---

## [0.1.3] - 2025-06-22

### 0.1.3 中新增

- 知识库 CRUD 和文件上传支持。
- 聊天中的 RAG 集成。

### 0.1.3 中变更

- 改进了 API 错误处理。

---

## [0.1.2] - 2025-06-21

### 0.1.2 中新增

- 自定义模型创建和更新的初步支持。
- 基本日志记录和调试输出。

### 0.1.2 中变更

- 聊天 API 的次要改进。

---

## [0.1.1] - 2025-06-20

### 0.1.1 中新增

- 单模型聊天和聊天历史记录。
- 基本项目结构和打包。

---

## [0.1.0] - 2025-06-20

### 0.1.0 中新增

- PyPI 上的首次公开发布。
- 核心 OpenWebUI 聊天客户端实现。
