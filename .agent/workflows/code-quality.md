---
description: 代码质量检查流程
---

# 代码质量检查流程

## 1. 快速格式化

### 自动格式化所有代码
// turbo
```bash
make format
```

这会运行:
- Black (代码格式化)
- isort (导入排序)

## 2. 代码检查

### 运行所有检查 (不修复)
// turbo
```bash
make check
```

### 运行 Ruff 检查
// turbo
```bash
make lint
```

### 运行类型检查
// turbo
```bash
make typecheck
```

### 运行安全扫描
// turbo
```bash
make security
```

## 3. 自动修复

### 修复所有可修复的问题
// turbo
```bash
make fix
```

## 4. 完整 CI 检查

### 模拟 GitHub Actions CI
// turbo
```bash
make ci
```

## 5. Pre-commit Hooks

### 安装 pre-commit
// turbo
```bash
pip install pre-commit
pre-commit install
```

### 手动运行所有 hooks
// turbo
```bash
pre-commit run --all-files
```

### 跳过 hooks (紧急情况)
```bash
git commit -n -m "urgent fix"
```

## 6. 工具配置说明

所有工具配置在 `pyproject.toml`:

| 工具 | 用途 | 配置节 |
|------|------|--------|
| Black | 代码格式化 | `[tool.black]` |
| isort | 导入排序 | `[tool.isort]` |
| Ruff | 代码检查 | `[tool.ruff]` |
| mypy | 类型检查 | `[tool.mypy]` |
| Bandit | 安全扫描 | `[tool.bandit]` |
