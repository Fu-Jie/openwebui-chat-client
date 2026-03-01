---
description: 根据 Facade 模式规范，快速生成子模块与其同步/异步门面绑定代码
---

# Facade Module Generator Skill

> [!IMPORTANT]
> 此技能旨在为 `openwebui-client` 项目强制实行并保护其 **Facade (门面) 架构**。任何添加新功能或业务模块的请求，都必须使用此技能来生成符合单一职责和依赖倒置原则的代码结构。

当用户请求新增业务模块（如“添加一个新功能”、“支持新的 API”）时，您必须按照以下架构规范自动生成所有相关代码层：

## 1. 核心业务模块 (The Sub-module)

- **位置**: `openwebui_chat_client/modules/`
- **命名规范**: 使用全小写及下划线，例如 `[module_name].py` (若是聊天系统的拓展则为 `chat_[module_name].py`)
- **设计规则**:
  - 必须是纯执行逻辑或专有 HTTP 通信层，禁止反向导入门面类 `ChatManager`。
  - 需要依赖隔离（例如通过 `__init__` 注入依赖对象）。
  - 函数签名必需包含完整的类型提示（Type Hints）和异常处理。
  - **示例生成模板**：

    ```python
    import logging
    from typing import Optional, Dict, Any
    # 不要导入任何基类Manager以防止循环依赖

    logger = logging.getLogger(__name__)

    class [ModuleName]Ops:
        def __init__(self, api_client_or_manager) -> None:
            self._impl = api_client_or_manager
        
        # ...业务方法实现...
    ```

## 2. 门面注册与委托 (The Facade Delegation)

生成底层实现后，您必须**同时**提供代码修改，将新模块注册到对外暴露的同步和异步管理器 (Manager) 中。

### 同步版本门面

- **位置**: `openwebui_chat_client/modules/chat_manager.py` (或其他对应的功能级 Manager)
- **规则**: 在 `__init__` 中实例化底层业务模块，并在主类中只暴露一到两行**委托调用**代码。
  - **禁止在 Facade 中写任何核心业务逻辑**。

### 异步版本门面

- **位置**: 同层级的 `async_` 前缀文件，例如 `async_chat_manager.py`
- **规则**: 必须提供与同步版本对等的 `async/await` 委托入口。

## 3. 架构防腐输出要求

当你应用本技能生成模块时，最终回复给用户的必须包含：

1. **[NEW] 业务模块源文件内容**（`openwebui_chat_client/modules/[module_name].py`）
2. **[MODIFY] 同步门面文件的依赖注入及委托方法改动块**
3. **[MODIFY] 异步门面文件的依赖注入及委托方法改动块**
4. **[MODIFY] STRUCTURE.txt 结构文档更新说明**（必须更新文档以维持架构图表准确性）。

## ⚠️ 严禁行为

- 绝对禁止在 `[X]_manager.py` (Facade) 中添加任何 `requests` 或数据清洗逻辑。
- 绝对禁止使用 Mixin 多重继承架构，这在该项目中已被弃用！
