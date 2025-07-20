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

---

> 使用方法：在Cline聊天窗口输入 `/release.md` 即可触发本工作流，按步骤操作即可完成标准发布流程。
