# 本地CI/CD脚本使用指南

本目录包含用于在本地运行CI/CD检查的脚本，模拟GitHub Actions工作流。

## 📋 脚本列表

| 脚本 | 用途 |
|------|------|
| `setup_local_ci.sh` | 创建虚拟环境并安装所有依赖 |
| `local_ci_check.sh` | 运行完整的CI检查（代码质量+测试） |
| `fix_code_quality.sh` | 自动修复代码格式问题 |
| `run_tests_with_coverage.sh` | 运行测试并生成覆盖率报告 |

## 🚀 快速开始

### 方法1: 使用Makefile（推荐）

```bash
# 1. 设置环境
make setup

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 运行CI检查
make ci

# 4. 查看所有可用命令
make help
```

### 方法2: 直接使用脚本

```bash
# 1. 设置环境
bash scripts/setup_local_ci.sh

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 运行CI检查
bash scripts/local_ci_check.sh
```

## 📖 详细说明

### 1. setup_local_ci.sh - 环境设置

**功能:**
- 创建Python虚拟环境
- 安装项目核心依赖
- 安装测试依赖
- 安装开发工具（black, isort, ruff, mypy, bandit等）
- 验证安装

**使用:**
```bash
bash scripts/setup_local_ci.sh
```

**输出:**
- 创建 `venv/` 目录
- 安装所有必需的包
- 显示使用说明

### 2. local_ci_check.sh - 完整CI检查

**功能:**
模拟GitHub Actions的完整检查流程：

1. ✅ 检查依赖安装
2. ✅ Black代码格式化检查
3. ✅ isort导入排序检查
4. ✅ Ruff代码质量检查
5. ⚠️ mypy类型检查（非阻断）
6. ⚠️ Bandit安全扫描（非阻断）
7. ✅ 单元测试

**使用:**
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 运行检查
bash scripts/local_ci_check.sh
```

**退出码:**
- `0`: 所有检查通过
- `1`: 有检查失败

### 3. fix_code_quality.sh - 自动修复

**功能:**
自动修复可修复的代码质量问题：
- Black格式化
- isort导入排序
- Ruff自动修复

**使用:**
```bash
source venv/bin/activate
bash scripts/fix_code_quality.sh
```

**注意:** 此脚本会修改你的代码文件！

### 4. run_tests_with_coverage.sh - 覆盖率测试

**功能:**
- 运行所有单元测试
- 生成覆盖率报告（HTML + XML + 终端）
- 显示覆盖率摘要

**使用:**
```bash
source venv/bin/activate
bash scripts/run_tests_with_coverage.sh
```

**输出:**
- `htmlcov/index.html` - HTML覆盖率报告
- `coverage.xml` - XML覆盖率报告
- 终端显示覆盖率摘要

## 🎯 常见工作流

### 提交代码前的检查

```bash
# 1. 激活环境
source venv/bin/activate

# 2. 自动修复格式问题
make fix

# 3. 运行完整CI检查
make ci

# 4. 如果通过，提交代码
git add .
git commit -m "your message"
git push
```

### 开发新功能

```bash
# 1. 激活环境
source venv/bin/activate

# 2. 编写代码...

# 3. 运行测试
make test

# 4. 检查代码质量
make check

# 5. 自动修复
make fix

# 6. 再次测试
make ci
```

### 查看测试覆盖率

```bash
# 1. 运行覆盖率测试
make coverage

# 2. 在浏览器中打开报告
open htmlcov/index.html  # macOS
```

## 🔧 Makefile命令参考

### 环境管理
```bash
make setup          # 创建虚拟环境并安装依赖
make install        # 安装项目依赖
make dev            # 安装开发依赖
```

### 代码质量
```bash
make format         # 格式化代码
make lint           # 代码检查
make typecheck      # 类型检查
make security       # 安全扫描
make check          # 运行所有检查
make fix            # 自动修复问题
```

### 测试
```bash
make test           # 运行测试
make test-verbose   # 详细测试输出
make coverage       # 覆盖率测试
```

### CI/CD
```bash
make ci             # 完整CI检查
```

### 清理
```bash
make clean          # 清理生成文件
make clean-all      # 清理所有（包括venv）
```

## 🐛 故障排除

### 问题: 脚本没有执行权限

```bash
chmod +x scripts/*.sh
```

### 问题: 虚拟环境未激活

```bash
source venv/bin/activate
```

### 问题: 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 重新安装
pip install -e ".[dev,test]"
```

### 问题: Black/isort检查失败

```bash
# 自动修复
make fix

# 或手动修复
black openwebui_chat_client/ tests/
isort openwebui_chat_client/ tests/
```

### 问题: 测试失败

```bash
# 查看详细输出
make test-verbose

# 运行特定测试
pytest tests/test_specific.py -v
```

## 📊 CI检查对应关系

| 本地命令 | GitHub Actions工作流 |
|---------|---------------------|
| `make ci` | 完整CI流程 |
| `make format && make check` | `code-quality.yml` |
| `make test` | `test.yml` |
| `make coverage` | `coverage.yml` |
| `make security` | `code-quality.yml` (安全部分) |

## 💡 最佳实践

1. **提交前必做:**
   ```bash
   make fix && make ci
   ```

2. **定期检查覆盖率:**
   ```bash
   make coverage
   ```

3. **保持依赖更新:**
   ```bash
   pip list --outdated
   ```

4. **使用pre-commit hook:**
   可以创建 `.git/hooks/pre-commit` 自动运行检查

## 🔗 相关文档

- [GitHub Actions工作流说明](../.github/workflows/README.md)
- [测试映射配置](../.github/test-mapping.yml)
- [项目配置](../pyproject.toml)
