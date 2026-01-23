---
description: 自动同步中英文文档
---

# Documentation Sync Skill

此 Skill 用于确保项目的英文文档 (`README.md`, `CHANGELOG.md`) 和中文文档 (`README.zh-CN.md`, `CHANGELOG.zh-CN.md`) 保持内容同步。

## 输入格式

提供英文文档的变更内容或 diff。

## 处理逻辑

1. **识别变更**: 分析英文文档中新增、修改或删除的部分
2. **翻译内容**: 将变更内容翻译成流畅的中文技术文档
3. **保持格式**: 确保 Markdown 格式（标题、代码块、链接）与原文一致
4. **术语一致**: 保持专业术语（如 Manager, Token, RAG）的一致性

## 输出示例

**输入 (README.md)**:
```markdown
### New Feature: Batch Delete
You can now delete multiple chats at once using `delete_chats_batch`.
```

**输出 (README.zh-CN.md)**:
```markdown
### 新功能：批量删除
现在可以使用 `delete_chats_batch` 一次性删除多个聊天。
```

## 使用提示

- 在提交文档变更前使用此 Skill
- 确保翻译准确传达了技术细节
- 注意中英文标点符号的转换
