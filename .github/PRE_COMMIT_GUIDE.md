# Pre-commit Hooks 使用指南

## 📋 概述

Pre-commit hooks 是在代码提交前自动运行的检查工具，可以在本地捕获问题，避免CI失败。

---

## 🚀 快速开始

### 安装

```bash
# 1. 安装pre-commit
pip install pre-commit

# 2. 安装git hooks
pre-commit install

# 3. (可选) 安装commit-msg hook
pre-commit install --hook-type commit-msg
```

### 验证安装

```bash
# 运行所有hooks
pre-commit run --all-files

# 应该看到类似输出:
# trailing-whitespace.................................................Passed
# end-of-file-fixer...................................................Passed
# check-yaml..........................................................Passed
# black...............................................................Passed
# isort...............................................................Passed
# ruff................................................................Passed
```

---

## 🔧 配置的Hooks

### 1. 通用文件检查

#### trailing-whitespace
- **作用**: 删除行尾空格
- **影响**: 自动修复

#### end-of-file-fixer
- **作用**: 确保文件以换行符结尾
- **影响**: 自动修复

#### check-yaml
- **作用**: 验证YAML文件语法
- **影响**: 只检查，不修复

#### check-added-large-files
- **作用**: 防止提交大文件（>1MB）
- **影响**: 阻止提交

#### check-merge-conflict
- **作用**: 检测合并冲突标记
- **影响**: 阻止提交

### 2. Python代码格式化

#### Black
- **作用**: 自动格式化Python代码
- **配置**: 88字符行宽
- **影响**: 自动修复

```bash
# 手动运行
black openwebui_chat_client/ tests/
```

#### isort
- **作用**: 自动排序import语句
- **配置**: 兼容Black
- **影响**: 自动修复

```bash
# 手动运行
isort openwebui_chat_client/ tests/
```

### 3. Python代码检查

#### Ruff
- **作用**: 快速Python linter
- **配置**: 自动修复可修复的问题
- **影响**: 自动修复 + 报告错误

```bash
# 手动运行
ruff check openwebui_chat_client/ tests/ --fix
```

#### mypy (可选)
- **作用**: 静态类型检查
- **配置**: 忽略缺失的导入
- **影响**: 只检查，不修复
- **注意**: 只检查主代码，跳过tests和examples

```bash
# 手动运行
mypy openwebui_chat_client/ --ignore-missing-imports
```

### 4. 安全检查

#### Bandit
- **作用**: Python安全漏洞扫描
- **配置**: 低严重性级别
- **影响**: 只检查，不修复
- **注意**: 跳过tests和examples

```bash
# 手动运行
bandit -r openwebui_chat_client/ -ll -ii
```

---

## 💡 使用技巧

### 跳过Hooks

#### 临时跳过所有hooks
```bash
git commit --no-verify -m "commit message"
# 或
git commit -n -m "commit message"
```

#### 跳过特定hook
```bash
SKIP=mypy git commit -m "commit message"
```

#### 跳过多个hooks
```bash
SKIP=mypy,bandit git commit -m "commit message"
```

### 只运行特定Hook

```bash
# 只运行black
pre-commit run black --all-files

# 只运行ruff
pre-commit run ruff --all-files
```

### 运行特定文件

```bash
# 只检查特定文件
pre-commit run --files openwebui_chat_client/openwebui_chat_client.py
```

### 更新Hooks

```bash
# 更新所有hooks到最新版本
pre-commit autoupdate

# 查看可用更新
pre-commit autoupdate --freeze
```

---

## 🔄 工作流程

### 正常提交流程

```bash
# 1. 修改代码
vim openwebui_chat_client/some_file.py

# 2. 添加到暂存区
git add openwebui_chat_client/some_file.py

# 3. 提交（自动运行hooks）
git commit -m "feat: add new feature"

# 如果hooks失败:
# - 查看错误信息
# - 修复问题（或让hooks自动修复）
# - 重新添加修改的文件
git add openwebui_chat_client/some_file.py
# - 再次提交
git commit -m "feat: add new feature"
```

### Hooks自动修复后的流程

```bash
# 1. 提交
git commit -m "feat: add new feature"

# 输出:
# black...............................................................Failed
# - hook id: black
# - files were modified by this hook
# 
# reformatted openwebui_chat_client/some_file.py

# 2. 文件已被自动修复，重新添加
git add openwebui_chat_client/some_file.py

# 3. 再次提交
git commit -m "feat: add new feature"

# 输出:
# black...............................................................Passed
# ✅ 提交成功
```

---

## 🐛 故障排除

### 问题 1: Pre-commit未安装

**症状**: `pre-commit: command not found`

**解决方案**:
```bash
pip install pre-commit
pre-commit install
```

### 问题 2: Hooks未运行

**症状**: 提交时没有看到hooks运行

**解决方案**:
```bash
# 重新安装hooks
pre-commit uninstall
pre-commit install

# 验证
pre-commit run --all-files
```

### 问题 3: mypy太慢

**症状**: mypy检查时间过长

**解决方案**:
```bash
# 方法1: 临时跳过mypy
SKIP=mypy git commit -m "commit message"

# 方法2: 禁用mypy hook
# 编辑 .pre-commit-config.yaml，注释掉mypy部分
```

### 问题 4: 某个Hook总是失败

**症状**: 特定hook无法通过

**解决方案**:
```bash
# 1. 手动运行该hook查看详细错误
pre-commit run <hook-name> --all-files --verbose

# 2. 修复问题或临时跳过
SKIP=<hook-name> git commit -m "commit message"

# 3. 如果是配置问题，更新 .pre-commit-config.yaml
```

### 问题 5: 大量文件需要修复

**症状**: 首次运行时大量文件被修改

**解决方案**:
```bash
# 1. 运行所有hooks修复所有文件
pre-commit run --all-files

# 2. 查看修改
git diff

# 3. 如果修改合理，提交
git add -A
git commit -m "chore: apply pre-commit hooks to all files"
```

---

## ⚙️ 自定义配置

### 修改Hook配置

编辑 `.pre-commit-config.yaml`:

```yaml
# 示例: 修改black的行宽
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
    - id: black
      args: ['--line-length=100']  # 改为100

# 示例: 禁用某个hook
# - repo: https://github.com/pre-commit/mirrors-mypy
#   rev: v1.8.0
#   hooks:
#     - id: mypy
```

### 添加新Hook

```yaml
# 在 .pre-commit-config.yaml 中添加
- repo: https://github.com/pycqa/flake8
  rev: 6.1.0
  hooks:
    - id: flake8
```

### 排除文件

```yaml
# 在 .pre-commit-config.yaml 中配置
exclude: |
  (?x)^(
      \.git/|
      \.venv/|
      build/|
      dist/|
      your_excluded_file\.py
  )$
```

---

## 📊 性能优化

### 加速Hooks运行

#### 1. 只检查暂存的文件（默认行为）
```bash
# Pre-commit默认只检查git add的文件
git add specific_file.py
git commit -m "message"  # 只检查specific_file.py
```

#### 2. 禁用慢速Hooks
```yaml
# 在 .pre-commit-config.yaml 中
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.8.0
  hooks:
    - id: mypy
      stages: [manual]  # 只在手动运行时执行
```

#### 3. 使用并行执行
```bash
# Pre-commit默认并行运行hooks
# 可以在配置中调整
```

---

## 🎯 最佳实践

### 1. 团队协作

```bash
# 确保所有团队成员安装pre-commit
echo "pre-commit" >> requirements-dev.txt

# 在README中添加安装说明
```

### 2. CI集成

```yaml
# 在 .github/workflows/test.yml 中
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

### 3. 渐进式采用

```bash
# 第一步: 只启用格式化工具
# - black
# - isort

# 第二步: 添加linter
# - ruff

# 第三步: 添加类型检查
# - mypy

# 第四步: 添加安全检查
# - bandit
```

### 4. 定期更新

```bash
# 每月更新一次hooks
pre-commit autoupdate

# 提交更新
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

---

## 📚 相关资源

- [Pre-commit官方文档](https://pre-commit.com/)
- [支持的Hooks列表](https://pre-commit.com/hooks.html)
- [Black文档](https://black.readthedocs.io/)
- [Ruff文档](https://docs.astral.sh/ruff/)
- [isort文档](https://pycqa.github.io/isort/)

---

## 🎉 预期效果

安装pre-commit hooks后，你将获得：

- ✅ **减少60%的CI失败** - 本地捕获问题
- ✅ **统一代码风格** - 自动格式化
- ✅ **更快的反馈** - 提交前就知道问题
- ✅ **更好的代码质量** - 自动检查和修复
- ✅ **节省时间** - 避免来回修改

---

**最后更新**: 2025-01-09  
**维护者**: openwebui-chat-client 团队
