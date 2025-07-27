# Cline Release Workflow

## 1. 更新tests、examples和文档

- 更新tests、示例（如`examples/demos.py`）、文档（`README.md`/`README.zh-CN.md`）

## 2. 更新CHANGELOG.md和更新CHANGELOG.zh-CN.md

- 在`CHANGELOG.md`和`CHANGELOG.zh-CN.md`中添加本次版本的变更记录。


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
---

> 使用方法：在Cline聊天窗口输入 `/release.md` 即可触发本工作流，按步骤操作即可完成标准发布流程。
