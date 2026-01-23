---
description: 自动化版本管理和发布准备
---

# Version Management Skill

此 Skill 用于自动化版本号更新和发布准备工作，确保所有相关文件的版本号一致。

## 输入格式

提供目标版本号（如 `0.1.25`）。

## 处理逻辑

1. **验证版本号**: 检查是否符合语义化版本规范 (SemVer)
2. **更新 pyproject.toml**: 修改 `version = "x.x.x"`
3. **更新 __init__.py**: 修改 `__version__ = "x.x.x"`
4. **处理 CHANGELOG**: 
   - 将 `[Unreleased]` 替换为新版本号和日期
   - 移除空的 `[Unreleased]` 块
   - 同步处理中文 CHANGELOG

## 输出示例

**操作清单**:
- [x] 更新 `pyproject.toml`: `0.1.24` -> `0.1.25`
- [x] 更新 `openwebui_chat_client/__init__.py`: `0.1.24` -> `0.1.25`
- [x] 更新 `CHANGELOG.md`: `[Unreleased]` -> `[0.1.25] - 2026-01-16`
- [x] 更新 `CHANGELOG.zh-CN.md`: `[未发布]` -> `[0.1.25] - 2026-01-16`

## 使用提示

- 在执行 `/publish-release` 工作流时使用
- 确保没有未记录的变更
