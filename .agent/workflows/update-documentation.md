---
description: 文档更新流程
---

# 文档更新流程

## 1. README 更新

### 双语同步要求
- `README.md` (英文)
- `README.zh-CN.md` (中文)

两个文件必须保持内容同步。

### 更新时机
- 新功能发布时
- API 变更时
- 使用示例更新时

## 2. CHANGELOG 管理

### 开发期间
在 `[Unreleased]` / `[未发布]` 部分添加变更:

```markdown
## [Unreleased]

### Added
- 新增 XXX 功能

### Changed
- 修改 YYY 行为

### Fixed
- 修复 ZZZ 问题
```

### 发布准备
1. 将 `[Unreleased]` 转换为版本号:
```markdown
## [0.1.25] - 2026-01-16
```

2. **必须删除空的 `[Unreleased]` 部分**
3. 同步更新 `CHANGELOG.zh-CN.md`

### 版本号同步
确保以下文件版本号一致:
- `pyproject.toml` 中的 `version`
- `openwebui_chat_client/__init__.py` 中的 `__version__`

## 3. API 文档

### 方法文档要求
每个公开方法必须有完整的文档字符串:
```python
def method_name(self, param: str) -> Optional[Dict]:
    """
    简短描述。

    详细描述（如需要）。

    Args:
        param: 参数描述

    Returns:
        返回值描述

    Example:
        ```python
        result = client.method_name("value")
        ```
    """
```

## 4. 示例代码

### 位置
`examples/` 目录下，按功能分类组织：
- `getting_started/` - 入门示例
- `advanced_features/` - 高级功能
- `notes_api/` - 笔记 API
- `model_management/` - 模型管理

### 示例要求
- 可独立运行
- 包含清晰的注释
- 使用环境变量配置

## 5. 发布检查清单

- [ ] CHANGELOG 版本号正确
- [ ] pyproject.toml 版本号更新
- [ ] __init__.py 版本号更新
- [ ] README 功能列表更新
- [ ] 双语文档同步
- [ ] 删除空的 `[Unreleased]` 部分
