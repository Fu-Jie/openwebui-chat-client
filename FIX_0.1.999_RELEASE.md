# 0.1.999 错误发布处理方案

**问题**: 意外发布了版本 0.1.999 到 PyPI  
**当前状态**:

- Git 标签: v0.1.999 已存在
- PyPI 包: 0.1.999 已发布
- 本地版本: 0.1.22 (正确)
- CHANGELOG: 已正确更新到 0.1.22

---

## 🚨 问题分析

### 时间线

1. ✅ 0.1.22 版本准备完成（CHANGELOG、版本号都已更新）
2. ❌ 错误：CHANGELOG 或版本号被改成了 0.1.999
3. 💥 发布工作流触发，将 0.1.999 发布到 PyPI
4. ⚠️ 现在需要处理这个错误发布

### 为什么会这样

发布工作流检测到 CHANGELOG.md 中第一行不是 `[Unreleased]`，就认为要发布。如果第一行是 `[0.1.999]`，工作流就会创建标签并发布。

---

## ✅ 解决方案（3 个步骤）

### 步骤 1: 删除错误的 Git 标签

```bash
# 删除本地标签
git tag -d v0.1.999

# 删除远程标签
git push origin --delete v0.1.999
```

**验证**:

```bash
git tag -l | grep v0.1
# 应该看不到 v0.1.999
```

---

### 步骤 2: 从 PyPI 删除或弃用 0.1.999

由于 PyPI 上已发布的包无法直接删除（为了保护依赖），需要采用以下策略之一：

#### 选项 A: 通过 PyPI 网页界面编辑（推荐）

1. 访问 <https://pypi.org/project/openwebui-client/>
2. 登录你的 PyPI 账户
3. 在 0.1.999 版本的发布记录中，点击 "Options"
4. 选择 "Delete"（如果距发布不到 24 小时）或 "Yank"（隐藏但保留）

#### 选项 B: 使用 twine（命令行）

```bash
# 需要 PyPI API token
pip install twine

# 删除包（仅发布 24 小时内可用）
twine delete dist/openwebui_chat_client-0.1.999-py3-none-any.whl -u __token__ -p <your-token>

# 或者使用 Yank（推荐，不会完全删除）
twine yank openwebui-client 0.1.999
```

#### 选项 C: 发布 0.1.22 作为正式版本（立即覆盖）

这是最直接的方法，因为 0.1.22 > 0.1.999 在语义版本中是错的，但在 Python 包管理中，最新版本号会被安装器优先使用。

---

### 步骤 3: 验证 CHANGELOG 和版本号

确保本地文件正确：

```bash
# 检查 CHANGELOG 顶部
head -20 CHANGELOG.md
# 应该看到: [Unreleased] 在最上面

# 检查版本号
grep "version" pyproject.toml
grep "__version__" openwebui_chat_client/__init__.py
# 都应该是 0.1.22
```

---

## 📋 完整修复步骤

### 1. 首先，清理本地环境

```bash
cd /Users/fujie/app/python/openwebui-client

# 删除本地构建文件
rm -rf dist/ build/ *.egg-info

# 删除本地标签
git tag -d v0.1.999

# 确认工作区干净
git status
```

### 2. 删除远程标签

```bash
# 删除远程 Git 标签
git push origin --delete v0.1.999

# 验证
git tag -l | grep v0.1.999  # 应该无结果
```

### 3. 在 PyPI 上处理 0.1.999

**方法 A: 通过网页（推荐，最安全）**

- 访问: <https://pypi.org/project/openwebui-client/0.1.999/>
- 点击右上角 "Options"
- 选择 "Yank this release"（隐藏但保留版本记录）

**方法 B: 使用 twine**

```bash
# 需要设置 PyPI token
twine yank openwebui-client 0.1.999 --comment "Accidental release, use 0.1.22 instead"
```

### 4. 准备正式发布 0.1.22

```bash
# 确认 CHANGELOG 正确
cat CHANGELOG.md | head -20

# 应该显示:
# [Unreleased]
#
# [0.1.22] - 2025-11-18
# ...

# 如果需要调整，编辑 CHANGELOG.md
# 然后提交
git add CHANGELOG.md
git commit -m "fix: correct CHANGELOG for 0.1.22 release"
```

### 5. 验证当前状态

```bash
# 查看最近的版本
git tag -l | sort -V | tail -5
# 应该显示（没有 v0.1.999）:
# v0.1.18
# v0.1.19
# v0.1.20
# v0.1.21
# v0.1.22

# 检查 PyPI
# 访问: https://pypi.org/project/openwebui-client/
# 应该看到最新版本不再是 0.1.999
```

---

## ⚠️ 注意事项

### 如果已经有人安装了 0.1.999

```bash
# 用户需要升级到 0.1.22（或更新版本）
pip install --upgrade openwebui-client

# 他们的 requirements.txt 如果固定了 0.1.999，需要手动修改
pip install openwebui-client==0.1.22
```

### 版本号语义

- `0.1.999` 看起来像是一个临时/占位符版本
- `0.1.22` 是实际的发布版本
- 建议今后使用标准的语义化版本（MAJOR.MINOR.PATCH）

### 防止未来重复

编辑 `.github/copilot-instructions.md` 中的发布流程部分：

**添加检查步骤**:

```markdown
# 发布前检查清单
- [ ] CHANGELOG.md 第一行是否是 `[X.Y.Z] - YYYY-MM-DD` 格式（不是 Unreleased）
- [ ] 版本号是否与 CHANGELOG 中的版本一致
- [ ] 版本号是否比之前的版本高
- [ ] pyproject.toml 和 __init__.py 中的版本号是否同步
```

---

## 🔍 推荐方案总结

**最简单的方案**（立即执行）:

1. 通过 PyPI 网页将 0.1.999 标记为 Yanked（隐藏）
2. 执行本地清理：

   ```bash
   git tag -d v0.1.999
   git push origin --delete v0.1.999
   ```

3. 确保本地版本是 0.1.22 和 [Unreleased]
4. 重新发布 0.1.22（或等待下一个版本）

**预期结果**:

- ✅ 0.1.999 对外隐藏（已 Yanked）
- ✅ Git 仓库恢复正常
- ✅ 用户看到的最新版本是 0.1.22
- ✅ 无需数据清理或回滚

---

## 相关文档

更新项目文档以防止未来的错误：

- `.github/copilot-instructions.md` - 发布流程规范
- `.github/workflows/publish.yml` - 发布工作流
- `CHANGELOG.md` - 版本管理指南
