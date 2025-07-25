# Cline Release Workflow

## 1. 同步修改

- 更新代码、示例（如`examples/demos.py`）、文档（`README.md`/`README.zh-CN.md`）。

## 2. 更新CHANGELOG.md

- 用英文记录本次变更内容。

## 3. 更新pyproject.toml

- 提升`version`字段，保持与CHANGELOG一致。

## 4. Git提交与打tag

```bash
git add .
git commit -m "release: vX.Y.Z 本次变更说明"
git tag vX.Y.Z
git push
git push origin vX.Y.Z
```

## 5. 构建与发布PyPI

```bash
rm -rf ./dist/ && rm -rf ./openwebui_chat_client.egg-info/
python -m build
python -m twine upload --repository pypi dist/*
```

## 6. PyPI官网确认新版本发布成功

## 7. GitHub发布Release

- 推荐用GitHub CLI命令一键发布（需已安装并登录gh）：

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes "主要变更内容"
```

- `vX.Y.Z`需与tag一致。
- `主要变更内容`应完整复制`CHANGELOG.md`中对应版本（如`[vX.Y.Z]`）的完整Markdown片段，包括版本号、日期、新增/变更/修复等内容。
- 命令示例中的`--notes`参数建议用单引号`'`包裹，以避免内容中的特殊字符（如反引号`` ` ``）被shell错误解析。

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes '
## [0.1.10] - 2025-07-20

### Added in 0.1.10

- Added `stream_chat` method for single-model streaming chat functionality.
- Added `delete_all_knowledge_bases` method to delete all knowledge bases.
- Added `delete_knowledge_bases_by_keyword` method to delete knowledge bases by name keyword.
- Added `create_knowledge_bases_with_files` method to batch create knowledge bases and add files.
'
```

- 发布后可在GitHub Releases页面确认。

---

> 使用方法：在Cline聊天窗口输入 `/release.md` 即可触发本工作流，按步骤操作即可完成标准发布流程。
