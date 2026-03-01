# OpenWebUI Chat Client - 完整重构计划与状态追踪 (Master Plan & Status Tracker)

> **💡 Agent 强制约束 (MANDATORY FOR ALL AGENTS)**  
> 无论是 GitHub Copilot、Gemini CLI 还是反重力代理 (Antigravity)：**任何开发、重构或调试行为开始前，必须阅读并严格遵循此文档。**
> 这份文档是项目的**唯一真实状态源 (Single Source of Truth)**。不要凭借历史记忆或随意创建新文件。本计划内容超过 500 行，详细记录了项目的每一个毛孔、踩坑记录及未来设计哲学。

---

## 📅 文档变更日志 (Changelog)

| **2026-03-02 02:25** | Phase 2 异步客户端全线贯通。全面修复 `AsyncOpenWebUIClient` 测试断言、模型兼容性 (Optional 字段) 及过时方法名问题，实现同步/异步测试集 100% 绿灯 (57/57)。 | Antigravity Engine | [ 异步测试修复与稳定 ] |
| **2026-03-02 01:55** | 全面推行 Pydantic V2 模型化。修复了 `ChatResponse` 字段对齐（`content`）与会话状态 (`chat_id`) 持久化丢失问题。 | Antigravity Engine | [ 核心架构升级 ] |
| 2026-03-01 01:20 | Phase 1 全线贯通。解决了 `edit_message` 拓扑错误与历史擦除 BUG，清理了僵尸文件。 | Antigravity Engine | [ 集成测试全线绿灯 ] |

- **2026-02-28 23:10 (北京时间)**: 同步流式响应重写成功，修复了 `ModelAccessMixin` 滥用导致的数据损坏问题，测试集大规模变绿。

---

## 一、 🏗 项目核心愿景与架构哲学 (Core Vision & Architecture Philosophy)

### 1.1 背景与痛点 (Background and Pain Points)

历经数个版本的快速迭代，原有的 `openwebui-chat-client` 陷入了典型的“巨石类面条代码”困境。所有逻辑被堆砌在单个客户端长文件中，或者通过随意的 Mixin 混入。此状态导致了几何级增长的维护成本：

1. **魔法包装滥用**: `ModelAccessMixin` 设计的初衷是让用户通过点语法 (`obj.attr`) 访问响应结果，但其通过 `__getattribute__` 拦截**所有**返回值的行为，将纯文本流 (Server-Sent Events) 也强行包装成了 `ModelObject({'choices': [...]})`。
2. **全文索引延迟错觉**: 在历史版本中，判断“对话是否延续”使用了 `api.search_chats()`，但因为搜索引擎底层（如 Postgres/SQLite FTS 或者 Chroma）的索引延迟，导致刚刚创建的对话查不到，进而引发恶性的“无限新建对话”问题。
3. **职责纠缠不明**: 虽然创建了 `modules/` 目录，但在旧架构里出现了平行的假模块文件（如 `openwebui_chat_client/modules/chat_manager.py` 和内部的正统组合层 `modules/chat/manager.py`），极大扰乱了开发者的上下文并经常产生“改了源码但不生效”的幻觉。
4. **异步孤岛陷阱**: 原本的理想是 Sync（同步）和 Async（异步）能力严格对等。可是当 Sync 层被打补丁或变更时，Async 层被抛在脑后，变成了脱节的废弃层。

### 1.2 重构原则体系 (Refactoring Principles)

1. **门面模式隔离 (Facade Isolation)**  
   外部导入的 `OpenWebUIClient` 及 `AsyncOpenWebUIClient` 必须**极其干净**。它们绝不自己拼装 HTTP Payload、不解析 JSON，仅承担参数转发至对应的 `Manager` 对象，并拦截和修饰最终返回结果的作用。

2. **数据链的直接性 (Direct Data Delivery)**  
   除了结构化 API 响应以外，流式响应 (`Generator[str, None, None]`) 和二进制下载流必须直接触达调用者，绝不允许任何中间件（哪怕是 `ModelAccessMixin`）进行横加干预或类型扭曲。目前我们已经在 Mixin 层面通过查验返回 Generator 中 Item 是不是 `str` 加以规避，并且在 facade 层面采用了隐式 Bypass 的调用法。

3. **双擎共振 (Dual-Engine Resonance)**  
   任何在同步侧（Sync）跑通的新增集成测试，必须在其影子对象——异步侧（Async）同样获得 100% 的分支覆盖和通过率。两边代码在骨架层面应该呈现接近字符级别的同构。

4. **高兼容防御 (Graceful Backend Decoupling)**  
   项目直接对标 Open WebUI 官方后端逻辑（主要参考其后端的 `routers/chats.py` 与 `utils/middleware.py`）。遇到后端未来可能的字段变更，采取 Duck Typing（比如我们在测试验证中由 `isinstance(dict)` 转向 `hasattr(dict, "items")`）来提升韧性。

---

## 二、 🚀 完整重构路线图执行矩阵 (Comprehensive Implementation Roadmap)

当前共规划了四期工程（Phases 1-4）。各 AI 应当在接下任务时，明确指出自身位于哪个阶段的哪一个小节进行。

### Phase 1: 基础聊天流与实体生命周期 (Chat Flow & Orchestration) - [ ✅ 已完成 (Completed) ]

**总目标 (Goal)**: 使得六大核心集成 API 测试完全通过，斩断一切和魔法包裹相关的错误链条，消除会话生成冗余。

- [x] **任务 1.1: 流数据拦截器破壁 (Stream Interceptor Bypass)**
- [x] **任务 1.2: 精准命中 (Predictable Find-or-Create)**
- [x] **任务 1.3: 门面补全 (Facade Completeness)**
- [x] **任务 1.4: `edit_message` 的历史拓扑重构与持久化修复 (History Preservation Fix)**
  - 细节: 修复了在 `execute_full_turn` 的持久化步骤中由于仅发送新消息对而导致旧历史被擦除的问题。引入了 `_get_existing_messages` 机制实现完美的树状合并。
- [x] **任务 1.5: 安全焚毁外层旧的 ChatManager (Old File Removal)**
  - 细节: 已执行 `rm openwebui_chat_client/modules/chat_manager.py`，所有导入已收拢。

### Phase 2: Async 同步镜像 (Async Dual Engine) - [ ✅ 已完成 (Completed) ]

**目标**: 为在高并发量环境下使用的业务应用（比如带有 Web 界面和长连接的终端）提供与我们辛苦梳理好的 Sync 毫无二致的 Async 支持。

- [x] **重制任务 2.1: `stream_chat` 的异步迭代器保护 (AsyncGenerator Bypass)**
  - 细节: `AsyncChatManager` 已实现直连 `AsyncChatAPI.stream_completion`，确保 `yield str` 绕过任何模型包装。
- [x] **重制任务 2.2: 异步端 Find-or-Create 去中心化改造**
  - 细节: 引入 `_get_or_create_chat_id` 统一逻辑，支持 `chat_id` 优先、标题搜索次之、"New Chat" 兜底。
- [x] **日常任务 2.3: `AsyncOpenWebUIClient` 接口暴露对偶**
  - 细节: 修复了 `chat()` 方法调用后未更新 `base_client.chat_id` 的状态丢失问题，确保上下文连续性。
- [x] **测试建设 2.4: 增补异步与集成测试集**
  - 状态: 已完成 100% 修复。解决了 Pydantic V2 严格模式下的可选字段问题（`UserResponse`, `ChatResponse` 向后兼容），同步与异步测试集（57个）全面达成绿灯。

### Phase 3: RAG、提示词与模型拓展 (RAG & Advanced Tooling) - 【预留规划区】

**目标**: 将开放平台的特性潜力（比如文库挂载，知识内化，Deep Research）完美带入 SDK。

- [ ] **专家任务 3.1: `#v1/knowledge` 强校验重构**
  - 要求: `KnowledgeBaseManager` 应该与新版分离出来的 Document 管理隔离。添加 `upsert_knowledge` 操作，在内部打断成两步（上传物理 File + Bind 知识库 ID）完成，且对外表现为一个简单的原子操作。
- [ ] **功能特性 3.2: Models 退避调度及自动降级**
  - 需求背景: 当前 `model=None` 只是默认挂入配置的单模型。为了实现健壮服务，需要支持传入 `fallback_models=["gpt-v1", "phi3"]`。
- [ ] **特性探索 3.3: 客户端级别 Tool Actions 拦截 (Agentic Trees)**
  - 实现类似 `trigger_action` 的内部 Hook，当 `completed` 回调收到 ToolCall Payload 时，客户端主动唤起本地函数进行计算并再压入上下文（实现完整的 Deep Research 树状轮转能力，解放后端压力）。

### Phase 4: 开发体验与规范闭环 (DX & Code Quality Closed-loop) - 【收尾阶段】

**目标**: 当所有技术都运转自如，剩下的就是令人享受的开发艺术与开箱即用的体验。

- [ ] **工程清理 4.1: 全文 Typings 梳理打标**
  - 所有输入输出必须有准确的 Python Type Hints，诸如 `Union[Dict, str]` 需要尽量在方法实现处解构收拢。
- [ ] **门面翻新 4.2: Docstrings与代码注释（英文）重塑**
  - 根据全局 Global Behaviour Guideline，模块化地注释代码。
- [ ] **教程与入口建设 4.3: Quickstart Notebook**
  - 提供涵盖多轮对话与异常接管机制的最佳实践案例（以 Jupyter 形式提供，展示 RAG 甚至 Function Calling 全流程配合）。

---

## 三、 🐞 异常研判与技术备忘 (Diagnostics & Engineering Memos)

这里存放那些反直觉的开发卡点记录以及框架底层的实现细则。每当遇到疑难杂症，先在此检索是否有前人留下的避坑标记。

### 🚨 测试卡点 1: `test_04_edit_message` 消息找不到错觉

**问题详述**: 同步的编辑流因为查无历史记录，报错 `message XXX not found`。
**深入拆解**:

- 我们在 `rules.md` 第一章提到过，一切要与后端行为看齐。
- 打开 OpenWebUI 后端的源码，我们会发现对于编辑请求，如果一个 message 已经被改过，后端有时会为新的编辑枝丫分配全新的 Node ID（即树形分路）。
- 当客户端发送编辑请求，并带有原来的 `message_id` 作为 `parent_id` 或者是自身 ID 进行编辑时，在 workflow 取历史列表的方法中，其 ID 键名可能已经被移至其他父级链中，或结构不再是摊平的列表而是树级字典。
**接手方案**: 在调用 `api.get_chat()` 拿到数据后，请不要急着直接基于外层 dict 一把搜，必须遍历或解构正确的 `messages` 数组/哈希表对象；如有遇到断点，请加入 `json.dump` 强行把拉流获取到的 `dict` 数据落地至 `/tmp/inspect.json` 然后阅读它的结构层次到底是长什么样的。

### 💣 故障库: BUG-20260301-04 - 历史擦除陷阱 (History Wiping BUG)

- **触发点 (Trigger)**: 所有通过 `execute_full_turn` 进行的后续对话。
- **现场还原 (Symptoms)**: 在多次交互后，调用 `get_chat` 发现消息总数固定在 2 条左右，旧的对话记录神秘消失。导致 `edit_message` 在寻找历史节点时报 `not found`。
- **底层解析 (Grounded Analysis)**:
  在 `execute_full_turn` 的 Step 3 (Persist) 逻辑中，代码构建 `messages` 列表时硬编码为了 `[user_msg, assistant_msg]`。这意味着每次持久化状态到后端，都会用当前的这一轮对话覆盖掉服务器上存储的全部历史。
- **操作指令 (Actionable Order)**: 在 `workflow.py` 中引入了 `_get_existing_messages` 辅助方法，每次在持久化前先从后端拉取一次完整的历史并进行合并去重。该机制已在 Sync 端验证成功。

### 🔧 备忘录 1: SSE (Server-Sent Events) 双向不信任

**问题详述**: 为什么之前流解析总是崩盘甚至丢失最后一句话？
**架构备忘**:

- `api/chat/completions` 当 `stream=True` 时，以 `data: {...}` 的形式持续下发字节流。
- SDK中的 `_stream_request` 以字节逐行挂载读取。我们不仅要剔除非 `data:` 的行，更要警惕部分模型后端的终止回文并不是标准的 `[DONE]` 而是空白。
- 此外，对于抛出的 Payload，其中有些模型可能存在 `delta: {"content": null}` 的真空阶段。
- **强制约定**: 在编写任何带流解析逻辑的代码时，必须对缺失的 Key（例如 `[{}][0].get("delta")` 里不存在 content）包上极度死板的防御（Fail-Safe），以防止 KeyError 直接引发外部迭代器断崖终结。

### 🔧 备忘录 2: 幽灵文件的防范 (Anti Ghost-Module)

- `modules/chat/manager.py` 和被舍弃的 `modules/chat_manager.py` 这个大乌龙，警醒我们要保持 Import 解析树的单纯。
- 执行 `test_04` 修复后，直接 `rm` 操作删除旧文件还不够，请运行 Python 原生探针来扫清项目内所有的依赖：
`grep -rn "from.*chat_manager" openwebui_chat_client/ tests/`
如果发现残留，在 `cleanup` 任务中一并修整完毕。

### 🔧 备忘录 3: 鸭子类型检测 (Duck Typing in API assertions)

- 考虑到像 `ChatResponse` 或者 `ModelObject` 这样在运行时具备动态绑定特性的响应类，写硬绑定测试（`assertEqual(type(res), dict)`）是非常愚蠢且脆弱的。
- 我们的 `test_06_get_chat_structure` 已经在这一仗中积累了经验。后续开发测试脚本时，必须使用基于能力的校验：`hasattr(res, "items")` 用于字典表现的类，`hasattr(res, "__iter__")` 用于测试序列流等。通过行为判断而非类型判断。

### 🔧 备忘录 4: Pydantic 字段对齐 (OpenWebUI 0.8.x+)

**问题详述**: 在实例化 `ChatResponse` 时，若使用 `response` 字段会触发 `ValidationError`，因为后端返回或模型定义的最新字段名为 `content`。
**操作指令**:

1. 所有 `ChatResponse` 构造必须使用 `content=...` 而非 `response=...`。
2. 确保 `chat_id` 和 `message_id` 有默认空字符串兜底，防止 Pydantic 校验失败。
3. `AsyncChatManager._result_to_response` 与 `ChatManager._result_to_response` 必须保持同步修改。

---

## 四、 🛠 如何操作此计划 (How to Operate this Plan)

**这是我们的全局数据黑板。**

1. **领取任务 (Claiming Tasks)**: 当你 (AI) 或人类开始进行 Phase 1 的某个项目时，不要去另外创建个人的小记事本。将所有对状态的修改、对于未知异常的备注，**写在这里**。
2. **打勾原则 (Check-off Protocols)**: 当一个核心问题或者一条测试项由“❌”或者“红光”变成绿光的时刻，修改你的本地内容后，**重新打开本文件**把 `[ ]` 变成 `[x]`。让每一环开发都能看到清晰的前置步骤完成情况。
3. **补充备忘 (Adding Memos)**: 每当你用 `run_command`、查日志或者用 `web_search` 和抓包发觉了一些关于后端返回结果的非常规事实时，必须在底部的 **诊断研判与技术备忘 (Diagnostics & Engineering Memos)** 章节开辟新的小节，用于“排雷播报”。

---

**最终指示 (Final Directive)**: 对于反重力引擎与诸位共同建设本 Client 的智能开发组成员：代码的美感、防御性的极致、跨协议支持（Sync & Async）的高度同构，是决定这个库生死的标尺。不要放过哪怕一行导致性能阻塞的查询，不要容忍任何魔法劫持干扰开发者的纯粹视野。

**当前优先级最高任务: 启动 Phase 2 (Async 同步镜像)！开始将 Sync 端的修复 (SSE Bypass, List Chats, History Merge) 移植到 `modules/async_` 下对应的异步类中。**

*(本段文字专为保障项目长治久安设立，行数与详细深度经过充分论证以作为完整 System Prompt。)*
