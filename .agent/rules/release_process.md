## CI/CD与发布流程

### 1. GitHub Actions工作流

#### 测试工作流 (test.yml)

- **触发条件**: push到main/master分支，PR到main/master
- **Python版本**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **测试命令**: `python -m unittest discover -s tests -p "test_*.py" -v`
- **性能优化**:
  - 增强的pip缓存策略（减少50-70%安装时间）
  - pytest_cache缓存（加速测试运行）
  - 总体CI时间减少20-30%

#### 集成测试 (integration-test.yml)

- **用途**: 更全面的集成测试，采用智能选择性测试
- **环境**: 真实OpenWebUI服务器环境
- **选择性测试**: 根据变更文件自动选择相关测试类别
- **并行执行**: 使用GitHub Actions矩阵策略并行运行测试
- **Chat测试清理**: 自动清理聊天会话，确保测试环境干净
- **性能优化**: 增强的缓存策略，显著加速依赖安装

#### 代码质量工作流 (code-quality.yml)

- **触发条件**: push/PR到main/master，修改Python文件
- **检查项目**:
  - Black代码格式化检查
  - isort导入排序检查
  - Ruff代码规范检查
  - mypy类型检查（非阻断）
  - Bandit安全扫描
  - pip-audit依赖漏洞检查

#### 覆盖率工作流 (coverage.yml)

- **触发条件**: push/PR到main/master，修改代码或测试
- **覆盖率要求**: 最低80%代码覆盖率
- **门控机制**: 覆盖率低于80%时CI失败
- **报告上传**: 自动上传到Codecov
- **配置**: pyproject.toml中设置`fail_under = 80`

#### 发布工作流 (publish.yml)

- **触发条件**: 推送标签 `v*`
- **流程**: 测试 -> 构建 -> 发布到PyPI -> 创建GitHub Release
- **依赖**: PYPI_API_TOKEN密钥

#### 版本号规范

- 遵循语义化版本控制 (Semantic Versioning)
- 格式: `MAJOR.MINOR.PATCH`
- 当前版本: 0.1.24

### 2. 本地开发工具

#### Pre-commit Hooks

项目配置了pre-commit hooks，在代码提交前自动运行检查：

**配置文件**: `.pre-commit-config.yaml`

**包含的Hooks**:

- **文件检查**: trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files
- **代码格式化**: Black (自动修复), isort (自动修复)
- **代码检查**: Ruff (自动修复), mypy (类型检查)
- **安全扫描**: Bandit (安全漏洞检测)

**安装方法**:

```bash
pip install pre-commit
pre-commit install
```

**使用方式**:

```bash
# 自动运行（提交时）
git commit -m "your message"

# 手动运行所有hooks
pre-commit run --all-files

# 跳过hooks（紧急情况）
git commit -n -m "urgent fix"
```

**效果**: 减少60%的CI失败，统一代码风格，提供即时反馈

#### Dependabot自动更新

项目配置了Dependabot自动依赖更新：

**配置文件**: `.github/dependabot.yml`

**更新策略**:

- **Python依赖**: 每周一自动检查更新
  - 开发依赖分组: black, ruff, pytest等
  - 生产依赖分组: requests, httpx等
- **GitHub Actions**: 每周一自动检查更新
  - 所有Actions更新分组在一起

**PR限制**:

- Python依赖: 最多10个PR
- GitHub Actions: 最多5个PR

**自动化**: 自动创建PR、添加标签、分配审查者

### 3. CI/CD性能优化成果

#### 缓存优化效果

- **依赖安装时间**: 减少50-70%
- **总体CI时间**: 减少20-30%
- **缓存内容**: pip缓存、pytest_cache

#### 开发体验提升

- **本地检查**: Pre-commit hooks提供即时反馈
- **CI失败率**: 降低60%（通过本地检查）
- **代码质量**: 统一的代码风格和规范
- **依赖管理**: 自动化更新，及时获取安全补丁

#### 质量保证

- **覆盖率门控**: 强制最低80%测试覆盖率
- **代码规范**: 自动化的格式和规范检查
- **安全扫描**: 自动检测代码和依赖漏洞
- **类型检查**: mypy静态类型验证

---

## 版本管理最佳实践

### 版本号生命周期

项目采用语义化版本控制 (SemVer: X.Y.Z)，每个版本号遵循以下生命周期：

1. **开发阶段**:
   - 版本号设定为目标发布版本（如 `0.1.22`）
   - CHANGELOG 中使用 `[未发布]` / `[Unreleased]` 部分记录更改
   - 不同的新功能、修复不断添加到此部分

2. **发布准备阶段**:
   - CHANGELOG: 将 `[未发布]` 转换为 `[X.Y.Z] - YYYY-MM-DD` 格式
   - 同步更新两个文件: `pyproject.toml` 和 `openwebui_chat_client/__init__.py`
   - **关键**: 完全删除 `[未发布]` / `[Unreleased]` 部分，不留空行

3. **发布阶段**:
   - 推送 CHANGELOG 更改到 GitHub
   - 发布工作流自动检测第一个版本条目是否为有效版本号
   - 如果是有效版本号，自动创建 Git 标签并推送到 PyPI

4. **发布后阶段** (可选):
   - 为下一个开发周期添加新的 `[未发布]` 部分
   - 这样准备接收下一个版本的更改记录

### 常见版本管理问题

#### 问题：意外发布了错误的版本号

**现象**: 发布了 0.1.999 这样的高版本号，导致无法发布更低版本

**原因**:

- pip 使用数字比较选择最新版本（0.1.999 > 0.1.22）
- 用户无法通过正常升级安装 0.1.22 版本

**解决方案**:

1. 删除错误版本的 Git 标签: `git tag -d v0.1.999 && git push origin --delete v0.1.999`
2. 在 PyPI 上 **Yank** 该版本（标记为已撤销，用户无法安装但历史记录保留）
3. 发布正确的版本号

#### 问题：[未发布] 部分阻止了发布

**现象**: 提交了 CHANGELOG 更改但发布工作流没有触发

**原因**:

- 发布工作流检查第一个版本条目
- 如果首个条目是 `[Unreleased]` 或 `[未发布]`，工作流认为没有版本准备好发布

**解决方案**:

- 在发布前，完全删除 `[未发布]` 部分（不只是标题，要删除整个块）
- 确保新版本号是第一个条目

#### 问题：版本号不一致导致混淆

**现象**: CHANGELOG 显示 0.1.22，但 PyPI 上不是这个版本

**原因**:

- pyproject.toml 和 **init**.py 中的版本号未同步更新
- Git 标签和 CHANGELOG 中的版本号不匹配

**解决方案**:

- 始终同时更新三个地方: CHANGELOG, pyproject.toml, **init**.py
- 在发布前验证: `grep "0.1.22" CHANGELOG.md pyproject.toml openwebui_chat_client/__init__.py`
- 确保三者的版本号完全一致

### 版本发布清单

发布新版本前，执行以下完整检查：

```bash
#!/bin/bash
# 版本发布前检查脚本

VERSION="0.1.22"
echo "🔍 开始发布前检查，版本: $VERSION"

# 1. 检查版本号一致性
echo ""
echo "1️⃣  检查版本号一致性..."
grep "$VERSION" CHANGELOG.md > /dev/null && echo "  ✅ CHANGELOG.md" || echo "  ❌ CHANGELOG.md"
grep "$VERSION" CHANGELOG.zh-CN.md > /dev/null && echo "  ✅ CHANGELOG.zh-CN.md" || echo "  ❌ CHANGELOG.zh-CN.md"
grep "$VERSION" pyproject.toml > /dev/null && echo "  ✅ pyproject.toml" || echo "  ❌ pyproject.toml"
grep "$VERSION" openwebui_chat_client/__init__.py > /dev/null && echo "  ✅ __init__.py" || echo "  ❌ __init__.py"

# 2. 检查 CHANGELOG 格式
echo ""
echo "2️⃣  检查 CHANGELOG 格式..."
FIRST_VERSION=$(grep -m 1 '^## \[' CHANGELOG.md | sed -n 's/^## \[\(.*\)\].*/\1/p')
if [ "$FIRST_VERSION" = "$VERSION" ]; then
  echo "  ✅ 首个版本条目正确: $FIRST_VERSION"
else
  echo "  ❌ 首个版本条目不是 $VERSION: $FIRST_VERSION"
fi

# 3. 检查是否存在 [Unreleased]
echo ""
echo "3️⃣  检查是否存在 [Unreleased]..."
if grep -q "^\## \[Unreleased\]" CHANGELOG.md; then
  echo "  ❌ 存在 [Unreleased] 部分"
else
  echo "  ✅ 不存在 [Unreleased]"
fi

if grep -q "^\## \[未发布\]" CHANGELOG.zh-CN.md; then
  echo "  ❌ 存在 [未发布] 部分"
else
  echo "  ✅ 不存在 [未发布]"
fi

# 4. 检查是否存在高于目标版本的标签
echo ""
echo "4️⃣  检查 Git 标签..."
git fetch --tags
TAGS=$(git tag | grep "^v" | sort -V)
echo "  现有标签: $TAGS"
echo "  目标版本: v$VERSION"

echo ""
echo "✅ 检查完成！如果上述所有项都通过，准备发布。"
```

### 发布流程步骤

```bash
# 1. 确保所有代码已提交
git status

# 2. 更新 CHANGELOG 和版本号
# - 将 [未发布] 改为 [X.Y.Z] - YYYY-MM-DD
# - 更新 pyproject.toml 和 __init__.py

# 3. 提交更改 (这会触发发布工作流)
git add CHANGELOG.md CHANGELOG.zh-CN.md pyproject.toml openwebui_chat_client/__init__.py
git commit -m "chore(release): prepare version 0.1.22 for release"
git push origin main

# 4. 监控发布工作流
# 访问 GitHub Actions 查看 publish.yml 工作流
# https://github.com/your-repo/actions

# 5. 验证 PyPI 上的版本
# https://pypi.org/project/openwebui-client/

# 6. (可选) 为下一个周期添加 [Unreleased]
# - 在 CHANGELOG 顶部添加 ## [Unreleased]
# - 在 CHANGELOG.zh-CN.md 顶部添加 ## [未发布]
```

---

## 特定功能开发指南

### 1. 聊天功能

#### 核心方法实现要点

- **状态管理**: 维护`self.chat_id`和`self.chat_object_from_server`
- **模型切换**: 支持在同一聊天中切换模型
- **流式响应**: 实现实时内容更新
- **错误恢复**: 处理网络中断和API错误

#### 重要实现细节

- 自动生成聊天标题和标签
- 支持文件上传和多模态输入
- RAG集成（文件和知识库）
- 工具调用支持

### 2. 知识库管理

#### 设计原则

- **CRUD操作**: 完整的创建、读取、更新、删除功能
- **批量处理**: 支持批量创建和删除
- **文件管理**: 支持向知识库添加文件
- **搜索功能**: 按名称搜索和过滤

#### 实现要点

- 异步文件上传处理
- 知识库状态监控
- 错误重试机制

### 4. 用户管理

#### 功能范围

- **用户查询**: 分页列出用户，获取单个用户详情
- **角色管理**: 修改用户角色（Admin/User）
- **用户删除**: 删除用户账号

#### 设计要点

- **权限检查**: 这些操作通常需要 Admin 权限 token
- **安全性**: 不处理密码等敏感信息（除非 API 要求）

### 5. 异步客户端支持

#### 设计目标

- **高并发**: 支持 Python 异步应用（FastAPI, etc.）
- **非阻塞**: 所有 I/O 操作必须 awaitable

#### 实现架构

- **`AsyncOpenWebUIClient`**: 异步客户端主类
- **`AsyncBaseClient`**: 基于 `httpx.AsyncClient` 的核心网络层
- **异步管理器**: 所有同步管理器（ChatManager 等）都有对应的 Async 版本

### 6. 模型管理

#### 功能覆盖

- **列表操作**: `list_models()`, `get_model()`, `create_model()`, `update_model()`, `delete_model()`
- **详情获取**: `get_model()`带自动重试
- **创建更新**: `create_model()`, `update_model()`
- **删除操作**: `delete_model()`

#### 特殊处理

- 自动创建重试机制
- 模型ID验证
- 配置参数验证

---

## 调试与故障排除

### 1. 常见问题

#### 认证错误

- 检查Bearer token有效性
- 验证API密钥配置
- 确认权限设置

#### 模型未找到

- 验证模型ID正确性（如`"gpt-4.1"`, `"gemini-2.5-flash"`）
- 确认模型在Open WebUI实例中可用
- 检查模型配置

#### 工具未找到

- 确认`tool_ids`匹配Open WebUI设置中配置的工具ID
- 验证工具权限和可用性

#### 文件上传问题

- 检查文件路径正确性
- 验证应用程序文件读取权限
- 确认文件格式支持

### 2. 日志调试

#### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

#### 日志级别说明

- `INFO`: 正常操作流程
- `WARNING`: 可恢复的问题
- `ERROR`: 需要注意的错误
- `DEBUG`: 详细的调试信息

---

## 📚 Copilot使用指南

### 1. 代码生成原则

- 严格遵循现有代码风格
- 保持类型提示完整性
- 添加适当的日志记录
- 包含异常处理

### 2. 功能扩展建议

- 基于现有管理器模式实现新功能
- 优先考虑用户体验和API一致性
- 充分测试边界情况
- 更新相关文档

### 3. 问题解决策略

- 查看现有类似实现
- 参考测试用例了解预期行为
- 检查日志输出定位问题
- 参考Open WebUI API文档

### 4. 最佳实践

- 小步迭代，频繁测试
- 保持代码简洁易读
- 充分利用现有工具和方法
- 注重向后兼容性

### 5. 选择性集成测试使用

- **测试映射维护**: 新功能开发时同步更新`.github/test-mapping.yml`
- **本地测试验证**: 使用`run_integration_tests.py`在本地验证测试
- **CI优化意识**: 避免不必要的测试触发，提高CI效率
- **配置文件理解**: 熟悉测试类别和文件映射规则
