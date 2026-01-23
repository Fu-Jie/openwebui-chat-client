# GitHub Actions 工作流说明

本目录包含完整的CI/CD工作流，采用**按需测试**策略和**代码质量检查**，确保高效且可靠的开发流程。

## 工作流概览

| 工作流 | 用途 | 触发条件 |
|--------|------|----------|
| `test.yml` | 单元测试 | Push/PR到main分支 |
| `integration-test.yml` | 集成测试 | Test工作流完成后 |
| `code-quality.yml` | 代码质量检查 | Python文件变更 |
| `coverage.yml` | 代码覆盖率 | 源码/测试变更 |
| `dependency-review.yml` | 依赖安全审查 | PR中依赖变更 |
| `pr-automation.yml` | PR自动化 | PR创建/更新 |
| `publish.yml` | 发布到PyPI | CHANGELOG更新 |
| `deploy.yml` | 文档部署 | 文档变更 |

---

## 1. test.yml - 单元测试工作流

**触发条件:**

- Push到main/master分支
- Pull Request到main/master分支
- 手动触发

**跳过条件（paths-ignore）:**

- `docs/**`, `*.md`, `mkdocs.yml`, `LICENSE`, `.gitignore`

**特性:**

- ✅ 智能测试选择：只运行与变更相关的测试
- ✅ 多Python版本矩阵：3.8-3.13
- ✅ pip缓存加速
- ✅ 并发控制：取消重复运行

**工作流程:**

```
检测变更文件 → 确定测试范围 → 并行运行测试 → 生成总结
```

---

## 2. integration-test.yml - 集成测试工作流

**触发条件:**

- Test工作流成功完成后
- Push/PR到main分支
- 手动触发（支持运行所有测试）

**特性:**

- ✅ 基于`test-mapping.yml`的智能测试选择
- ✅ 矩阵策略并行运行测试类别
- ✅ 支持手动覆盖运行所有测试
- ✅ 环境变量灵活配置

**测试类别:**

- connectivity, basic_chat, notes_api, prompts_api
- rag_integration, model_management, model_switching
- comprehensive_demos, deep_research
- async_basic_chat, async_streaming_chat, async_model_operations

---

## 3. code-quality.yml - 代码质量检查 🆕

**触发条件:**

- Python文件变更
- pyproject.toml变更

**检查项目:**

| 工具 | 用途 | 阻断性 |
|------|------|--------|
| Black | 代码格式化 | ✅ 阻断 |
| isort | 导入排序 | ✅ 阻断 |
| Ruff | 代码检查 | ✅ 阻断 |
| mypy | 类型检查 | ⚠️ 非阻断 |
| Bandit | 安全扫描 | ⚠️ 非阻断 |
| pip-audit | 依赖漏洞 | ⚠️ 非阻断 |

**本地运行:**

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 格式化代码
black openwebui_chat_client/ tests/
isort openwebui_chat_client/ tests/

# 检查代码
ruff check openwebui_chat_client/ tests/
mypy openwebui_chat_client/

# 安全扫描
bandit -r openwebui_chat_client/
pip-audit
```

---

## 4. coverage.yml - 代码覆盖率 🆕

**触发条件:**

- 源码或测试文件变更

**特性:**

- ✅ 生成覆盖率报告
- ✅ 上传到Codecov（需配置CODECOV_TOKEN）
- ✅ 在PR中显示覆盖率摘要

---

## 5. dependency-review.yml - 依赖安全审查 🆕

**触发条件:**

- PR中依赖文件变更（pyproject.toml, setup.py, requirements*.txt）

**特性:**

- ✅ 检测新增依赖的安全漏洞
- ✅ 检查许可证合规性
- ✅ 在PR中添加评论摘要
- ✅ 检查过时依赖

---

## 6. pr-automation.yml - PR自动化 🆕

**触发条件:**

- PR创建、更新、标签变更

**特性:**

- ✅ 自动标签：根据变更文件添加标签
- ✅ 大小标签：XS/S/M/L/XL
- ✅ PR检查清单：描述、标题格式
- ✅ 欢迎首次贡献者

**标签配置:** `.github/labeler.yml`

---

## 7. publish.yml - 发布工作流

**触发条件:**

- CHANGELOG.md更新且包含有效版本号

**发布流程:**

```
检测版本 → 创建Git标签 → 运行测试 → 构建包 → 发布PyPI → 创建GitHub Release
```

**版本格式要求:**

- `[X.Y.Z]` - 正式版本
- `[X.Y.Z-beta.1]` - 预发布版本
- `[Unreleased]` - 不触发发布

---

## 8. deploy.yml - 文档部署

**触发条件:**

- docs/目录变更
- mkdocs.yml变更

**部署目标:** GitHub Pages

---

## 配置说明

### 必需的仓库密钥

| 密钥 | 用途 | 必需 |
|------|------|------|
| `OUI_BASE_URL` | OpenWebUI实例URL | 集成测试 |
| `OUI_AUTH_TOKEN` | API认证令牌 | 集成测试 |
| `PYPI_API_TOKEN` | PyPI发布令牌 | 发布 |
| `CODECOV_TOKEN` | Codecov上传令牌 | 覆盖率（可选） |

### 可选密钥

| 密钥 | 用途 | 默认值 |
|------|------|--------|
| `OUI_DEFAULT_MODEL` | 默认模型ID | gpt-4.1 |
| `OUI_PARALLEL_MODELS` | 并行模型列表 | gpt-4.1,gpt-4o |

---

## 本地开发指南

### 安装开发依赖

```bash
pip install -e ".[dev,test]"
```

### 运行代码质量检查

```bash
# 格式化
black openwebui_chat_client/ tests/
isort openwebui_chat_client/ tests/

# 检查
ruff check openwebui_chat_client/ tests/
mypy openwebui_chat_client/
```

### 运行测试

```bash
# 单元测试
python -m pytest tests/ -v

# 带覆盖率
python -m pytest tests/ -v --cov=openwebui_chat_client --cov-report=html

# 集成测试
python .github/scripts/run_all_integration_tests.py --category basic_chat
```

### 检测测试范围

```bash
# 单元测试范围
python .github/scripts/detect_unit_tests.py HEAD~1 HEAD

# 集成测试范围
python .github/scripts/detect_required_tests.py HEAD~1 HEAD
```

---

## 最佳实践

### 提交前检查

1. 运行格式化：`black . && isort .`
2. 运行检查：`ruff check .`
3. 运行测试：`pytest tests/ -v`

### 添加新功能

1. 创建源代码和测试文件
2. 更新`detect_unit_tests.py`中的映射
3. 更新`test-mapping.yml`中的集成测试映射
4. 更新CHANGELOG的`[Unreleased]`部分

### 发布新版本

1. 将`[Unreleased]`改为`[X.Y.Z] - YYYY-MM-DD`
2. 同步更新`pyproject.toml`和`__init__.py`中的版本号
3. 推送到main分支，工作流自动发布

---

## 故障排除

### 代码质量检查失败

```bash
# 查看具体问题
black --check --diff openwebui_chat_client/
ruff check openwebui_chat_client/ --show-fixes
```

### 测试未运行

- 检查文件是否在paths-ignore列表中
- 验证文件模式是否在映射配置中
- 查看工作流日志中的检测步骤

### 发布未触发

- 确保CHANGELOG第一个版本不是`[Unreleased]`
- 验证版本号格式正确
- 检查Git标签是否已存在

---

## 相关文档

- [INTEGRATION_TESTING.md](../INTEGRATION_TESTING.md) - 集成测试详细说明
- [test-mapping.yml](../test-mapping.yml) - 测试映射配置
- [labeler.yml](../labeler.yml) - PR标签配置
