---
description: 自动化验证重构代码的完整规范与健康度
---

# Refactor Validator Skill

此技能用于在完成 `openwebui-client` 的重构、模块拆分或新增子业务结构后，对所修改/新增代码的健康度和重构质量进行“终极验证”。

不论是 AI（在此技能激活时）还是开发者手动触发，在合并重构性质的 Pull Request 之前，必须执行以下标准化验证管线。

## 验证流程与管线 (Validation Pipeline)

请依序执行以下步骤。如果任何一个步骤失败，您必须停下来，并尝试通过代码修改来解决该问题，直到验证通过。

### 1. 静态代码分析与格式化检查 (Format & Lint)

执行命令：

```bash
pre-commit run --all-files
```

或者手动执行：

```bash
black openwebui_chat_client/
isort openwebui_chat_client/
ruff check openwebui_chat_client/ --fix
```

> **要求**：清除所有因为依赖重组或删减引起的无用导入、双空格等影响格式的问题，确保符合项目采用的 Black + isort 规范。

### 2. 强类型检查 (Type Constraints)

执行命令：

```bash
mypy openwebui_chat_client/
```

> **要求**：重构非常容易丢失类型信息（比如将巨石类拆分后返回 `Any`）。确保新增的模块方法的返回类型都是 `Optional[Dict[str, Any]]` 或者符合业务定义的强类型。不允许存在新的类型推导报错。

### 3. 命名与依赖规则扫描 (Dependency Rule)

人工与自动化兼并检查以下“重构防腐”规则：

- **入口测试**：由于拆散了 Mixin，务必在终端测试：

  ```bash
  python -c "from openwebui_chat_client import OpenWebUIClient"
  ```

  如果抛出 `ImportError`（通常是循环导入引起），说明重构过程导致了环状依赖，必须立即修复。

- **禁止非法实例化**：检查除 `__init__.py` 或专门的依赖注入层以外的地方，是否出现了 `ChatManager()` 等顶层门面的相互实例化。这是明令禁止的。

### 4. 自动化依赖项防腐 (CI/CD Rules Reflection)

如果您正在添加新的 Manager 或 API `模块.py`，必须确认相关变更是否影响了以下两个文件，并按需建议更新：

1. `.github/test-mapping.yml`（是否需要把这个新文件加入某种行为的测试触发列表）
2. `openwebui_chat_client/modules/STRUCTURE.txt`（是否已经在架构图中将其补充并说明了职责）

## 自动化判定 (Decision Making)

在所有 4 步验证都得到绿色 `✅` 确认之后，才能向用户回复重构验证完毕。
任何红色的 `❌` 失败信息必须作为拦截理由，并根据日志自动开始针对性修复。
