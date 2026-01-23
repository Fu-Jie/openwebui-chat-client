---
description: 测试运行完整指南
---

# 测试运行流程

## 1. 单元测试

### 运行所有单元测试

// turbo

```bash
make test
```

### 运行详细测试输出

// turbo

```bash
make test-verbose
```

### 运行特定测试文件

// turbo

```bash
pytest tests/test_specific.py -v
```

### 运行特定测试方法

// turbo

```bash
pytest tests/test_file.py::TestClass::test_method -v
```

## 2. 集成测试

### 配置环境变量

```bash
export OUI_BASE_URL="http://localhost:3000"
export OUI_AUTH_TOKEN="your-token"
export OUI_DEFAULT_MODEL="your-model"
```

### 运行所有集成测试

// turbo

```bash
python run_integration_tests.py
```

### 运行特定测试类别

// turbo

```bash
python run_integration_tests.py --category basic_chat
```

### 列出可用测试类别

// turbo

```bash
python .github/scripts/run_all_integration_tests.py --list-categories
```

## 3. 覆盖率报告

### 生成覆盖率报告

// turbo

```bash
make coverage
```

### 查看 HTML 报告

// turbo

```bash
open htmlcov/index.html
```

## 4. 本地测试检测

### 检测单元测试范围

// turbo

```bash
python .github/scripts/detect_unit_tests.py HEAD~1 HEAD
```

### 检测集成测试范围

// turbo

```bash
python .github/scripts/detect_required_tests.py HEAD~1 HEAD
```

## 5. 测试类别说明

| 类别 | 描述 |
|------|------|
| `connectivity` | 基础连接测试 |
| `basic_chat` | 基础聊天功能 |
| `notes_api` | 笔记 API |
| `prompts_api` | 提示词 API |
| `rag_integration` | RAG 集成 |
| `model_management` | 模型管理 |
| `model_switching` | 模型切换 |
| `deep_research` | 深度研究 |
