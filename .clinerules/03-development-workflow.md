# 规则3：开发与发布工作流

## 1. 功能开发

-   **新功能**: 在`openwebui_chat_client/openwebui_chat_client.py`中添加新方法时，请遵循现有的编码规范（见`02-coding-style.md`）。
-   **示例**: 为每个重要的新功能或变更，在`examples/`目录下添加或更新相应的示例代码（`demos.py`）。

## 2. 文档更新

-   **README**: 在添加新功能或进行重大变更后，必须同步更新`README.md`和`README.zh-CN.md`中的功能列表和使用说明。
-   **CHANGELOG**: 每次发布前，必须在`CHANGELOG.md`中记录所有变更。条目应清晰、简洁，并遵循现有的格式。

## 3. 发布流程

-   发布新版本时，请严格遵循`.clinerules/workflows/release.md`中定义的步骤，确保版本号、CHANGELOG、Git标签和PyPI包的一致性。
-   核心步骤包括：更新文档 -> 更新CHANGELOG -> 更新pyproject.toml版本 -> Git提交与打标 -> 构建与发布 -> 创建GitHub Release。

## 4. 未来开发方向

-   **API同步**: 持续关注OpenWebUI的官方更新，当出现新API或API变更时，应优先在客户端中进行适配。
-   **效率提升**: 鼓励并优先开发能显著提高使用和维护效率的自动化、批量化功能。
