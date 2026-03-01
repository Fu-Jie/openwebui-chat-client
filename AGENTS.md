# OpenWebUI Chat Client - Copilot 开发指南

欢迎来到 `openwebui-chat-client` 的开发指南中心。为了避免大模型上下文污染，我们将超过 1600 行的规范拆分为了针对性更强的模块化规则。

## 一、 质量确认四柱体系（Quality Confirmation 4 Pillars 🌟）

> [!IMPORTANT]
> 实现任何接口、修复任何 Bug、或完成任何重构后，**必须综合运用以下四种手段**对质量进行确认，任何一个环节的截断都视为验证不充分。

#### 柱一：源码分析（Source Code Analysis）

结合 `.agent/skills/source-code-analyzer.md` 的优先级框架进行：

1. **官方文档优先** (`../docs/`): 从官方 Docusaurus 文档理解接口的规范定义
2. **源码交叉验证** (`../open-webui/backend/open_webui/routers/`): 在真实路由实现中核实参数和行为
3. **拉取先行**: 分析前在相关目录执行 `git pull`，避免基于过期代码做判断

#### 柱二：浏览器子代理（Browser Subagent）

对于行为不确定或文档缺失的 API，必须启动浏览器子代理进行实况验证：

- **目标**: `http://localhost:3003`（或用户指定的测试环境）
- **操作**: 通过 UI 触发目标功能，抓取实际网络请求（请求 URL、Headers、Payload、Response）
- **记录标准**: 将发现的实际 API 行为写入知识库（见柱三），双语记录

#### 柱三：知识积累（Knowledge Accumulation）

所有发现的 API 行为、架构决策、调试结论都必须归档到 `.agent/knowledge/` 目录：

- **结构**: 按功能分类（如 `api/chats.md`, `api/models.md`, `patterns/auth.md`）
- **双语要求**: 每份文档必须包含中文说明和英文标识（方法名、参数名、URL 均用英文）
- **更新时机**: 每次发现新 API、纠正误解、或解决疑难 Bug 后立即更新

#### 柱四：Python 脚本测试（Python Script Testing）

所有实现必须通过至少一种脚本测试验证功能正确性：

- **单元测试**: 使用 `unittest.mock` 隔离子模块的纯逻辑测试（参见 `.agent/skills/test-generation.md`）
- **集成测试**: 在真实后端环境下运行 `.github/scripts/run_all_integration_tests.py`
- **成功标准**: 核心接口集成测试通过率 **≥ 90%**，纯逻辑模块单元覆盖率 **≥ 80%**

---

## 二、 核心规则库索引 (Rule Indexes)

当您在进行特定领域的开发时，请主动参阅以下详细规则文档：

📄 **[.agent/rules/architecture.md](./.agent/rules/architecture.md)**

- 涵盖：项目的 Facade 门面模式、单一职责模块拆分、状态同步模式机制。

📄 **[.agent/rules/coding_standards.md](./.agent/rules/coding_standards.md)**

- 涵盖：命名规范、类型提示要求、错误处理机制、日志门控，以及双端（同步/异步）开发流。

📄 **[.agent/rules/api_design.md](./.agent/rules/api_design.md)**

- 涵盖：如何设计符合项目风格的 API 方法名、入参出参结构、并发处理 `ThreadPoolExecutor`。

📄 **[.agent/rules/testing_workflow.md](./.agent/rules/testing_workflow.md)**

- 涵盖：智能选择性集成测试机制、`.github/test-mapping.yml` 的维护及本地脚本测试指南。

📄 **[.agent/rules/release_process.md](./.agent/rules/release_process.md)**

- 涵盖：GitHub Actions 流水线、版本号维护、语义化发布，以及通过 `CHANGELOG.md` 触发自动发布的硬性要求。

📄 **[.agent/rules/docs_maintenance.md](./.agent/rules/docs_maintenance.md)**

- 涵盖：向后兼容文档维护原则、双语（中英）文档的同步机制。

📄 **[.agent/rules/examples_guide.md](./.agent/rules/examples_guide.md)**

- 涵盖：`examples/` 目录下示例代码的编写排版规范及环境变量管理。

📄 **[.agent/rules/troubleshooting_docs.md](./.agent/rules/troubleshooting_docs.md)**

- 涵盖：常见环境与运行时故障的排查指南编写规范。

---

## 🚀 故障排查与 AI 技能 (Skills)

如遇到疑难杂症，请随时参考我们的 `.agent/skills/`:

- 源码分析越界：`source-code-analyzer.md`
- 一键生成模块：`facade-module-generator.md`
- 重构验证跑流：`refactor-validator.md`
- Mock 测试生成：`test-generation.md`
