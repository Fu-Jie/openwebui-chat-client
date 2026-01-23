---
description: 版本发布完整流程
---

# 版本发布流程

## 1. 发布前检查

### 确认所有测试通过
// turbo
```bash
make ci
```

### 确认代码质量
// turbo
```bash
make check
```

## 2. 更新版本号

### 需要同步更新的文件
1. `pyproject.toml` 中的 `version`
2. `openwebui_chat_client/__init__.py` 中的 `__version__`

## 3. 更新 CHANGELOG

### 将 [Unreleased] 转换为版本号
```markdown
# 修改前
## [Unreleased]
### Added
- ...

# 修改后
## [0.1.25] - 2026-01-16
### Added
- ...
```

### 重要：删除空的 [Unreleased] 部分
发布前必须完全删除 `[Unreleased]` 部分，否则发布工作流不会触发。

### 同步更新中文版
同步更新 `CHANGELOG.zh-CN.md`。

## 4. 更新 README（如需要）

如果有新功能，同步更新：
- `README.md`
- `README.zh-CN.md`

## 5. 提交并推送

// turbo
```bash
git add -A
git commit -m "release: v0.1.25"
git push origin main
```

## 6. 验证发布

### 检查 GitHub Actions
1. 访问仓库的 Actions 页面
2. 确认 `Release` 工作流已触发
3. 等待发布完成

### 验证 PyPI
// turbo
```bash
pip install openwebui-chat-client --upgrade
python -c "import openwebui_chat_client; print(openwebui_chat_client.__version__)"
```

## 7. 发布后操作

### 添加新的 [Unreleased] 部分
在 CHANGELOG 顶部添加：
```markdown
## [Unreleased]

```

同步更新中文版。
