---
description: 根据 Facade 架构规范自动生成单元测试代码
---

# Test Generation Skill

此 Skill 用于根据现有的 Python 方法代码，自动生成符合 `openwebui-client` **Facade (门面) 架构**及其隔离测试规范的单元测试代码。

## 测试架构规范 (Testing Guardrails)

在 Facade 架构下，所有的子模块必须**独立测试**。禁止在测试业务流程逻辑时发起真实的 HTTP 请求；禁止跨模块实例化（即测 A 模块时不能实例化 B 模块）。

测试策略按照层级分为：

### 1. HTTP 边界层 (`*_api.py` 模块)

此类模块只负责通信。测试时，应当：

- 使用 `unittest.mock.MagicMock` 对注入的 `BaseClient` 及其内部的 `session.post` / `session.get` 进行模拟 (Mock)。
- 验证：URL 构造是否正确，Payload 是否正确，异常捕获机制是否工作。

### 2. 纯逻辑层 (如 `chat_payloads.py`)

此类模块只负责数据组装，没有 I/O。

- 要求：**必须达到极高的分支覆盖率**。直接输入假数据，测试输出的字典结构是否符合预期。不需要任何 HTTP Mock。

### 3. 工作流或调度层 (`chat_workflow.py` / `chat_tasks.py` 等)

此类模块通过调用其他组件来完成逻辑。

- 应当：将它们赖以生存的外部依赖（如传入的 `ChatAPI` 实例）全部使用 `Mock(spec=ChatAPI)` 替换。
- 验证：验证调度层是否以正确的顺序（序贯）或在特定的条件下正确调用了底层 API 的相关方法。

## 输入格式

提供待测试的模块源文件或具体 Python 方法代码（包括同步和异步版本）。

## 自动生成与输出要求

生成的测试代码架构应符合内置的 `unittest` 规范，具体模板参考：

```python
import unittest
from unittest.mock import Mock, MagicMock
# 根据 Facade 规则导入具体的底层模块，而不是顶层门面
from openwebui_chat_client.modules.chat_api import ChatAPI
from openwebui_chat_client.modules.chat_workflow import ChatWorkflow

class TestChatWorkflow(unittest.TestCase):
    def setUp(self):
        # 1. 模拟依赖组件 (Mock dependencies via dependency injection)
        self.mock_api = Mock(spec=ChatAPI)
        
        # 2. 注入到待测目标
        self.workflow = ChatWorkflow(self.mock_api)

    def test_execute_full_turn_success(self):
        """测试正常的工作流流转，不涉及具体 HTTP"""
        # 设置假数据返回
        self.mock_api.completion.return_value = {"id": "msg1"}
        
        # 执行
        result = self.workflow.execute_full_turn(question="Hello", chat_id="123")
        
        # 验证依赖层的调用次数与参数是否正确
        self.mock_api.completion.assert_called_once()
        self.mock_api.completed.assert_called_once()
        self.assertEqual(result, {"id": "msg1"})
```

## 自动化防腐注意事项

当用户要求您生成测试时，必须同时：

1. 生成成功用例、异常抛出用例。
2. 在输出代码后，口头确认是否由于方法本身的参数推导存在缺陷，导致难以被 Mock（如硬编码了外部网络请求），并建议如何依据倒置原则对其重构。
