## 📝 开发规范

### 1. 代码风格与结构

#### 命名规范

- 遵循PEP 8编码规范
- 内部辅助方法使用单个下划线前缀（如`_ask`、`_upload_file`）
- 常量和配置项在`__init__`方法中初始化为实例属性
- 优先使用f-string进行字符串格式化

#### 类型提示

- **必须**: 所有函数和方法的参数及返回值都必须有明确的类型提示
- **使用**: `typing`模块中的`Optional`, `List`, `Dict`, `Tuple`, `Union`, `Generator`等
- **示例**:

```python
def chat(self, question: str, chat_title: Optional[str] = None,
         model_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    pass
```

#### 日志记录

- **关键操作**: 在所有API请求、文件操作、状态变更前后记录日志
- **日志级别**:
  - `logger.info()`: 正常操作流程
  - `logger.warning()`: 警告信息
  - `logger.error()`: 错误信息
  - `logger.debug()`: 详细调试信息（如请求载荷）
- **日志内容**: 必须包含关键上下文信息（如`chat_id`、`model_id`、`file_path`等）

#### 异常处理

- **必须**: 对所有可能失败的操作使用`try...except`块
- **优先**: 捕获具体的异常类型（如`requests.exceptions.RequestException`, `json.JSONDecodeError`, `KeyError`）
- **避免**: 宽泛的`except Exception`
- **要求**: 在`except`块中使用`logger.error()`记录详细错误信息

### 2. 架构原则

#### 状态持久化

- 客户端的所有操作都应与Open WebUI后端同步
- 通过API所做的更改必须能够持久化并反映在UI上
- 维护聊天会话状态的一致性

#### 原子化与批量化

- 提供原子化的API操作方法
- 在原子操作基础上构建批量处理方法
- 满足不同层次的自动化需求

#### 用户友好与健壮性

- 提供清晰的日志记录和精细的异常处理
- 所有与外部交互的方法都必须有明确的成功/失败返回
- 方便用户进行调试和集成

---

## 🚀 开发工作流

### 1. 新功能开发流程

#### 功能开发

1. **需求分析**: 确保新功能符合项目核心目标
2. **API设计**: 在相应管理器中添加新方法
3. **编码规范**: 严格遵循上述编码规范
4. **示例代码**: 在`examples/`目录下添加相应示例
5. **单元测试**: 在`tests/`目录下添加对应测试
6. **集成测试映射**: 更新`.github/test-mapping.yml`以包含新功能的测试映射

#### 代码结构

- **主要代码**: `openwebui_chat_client/openwebui_chat_client.py`
- **核心模块**: `openwebui_chat_client/core/base_client.py`
- **功能管理器**: `openwebui_chat_client/modules/` 目录
- **测试代码**: `tests/test_*.py`
- **示例代码**: `examples/` 目录下按功能分类组织

### 2. 测试要求

#### 测试覆盖

- **单元测试**: 每个新功能都必须有对应的单元测试
- **集成测试**: 关键功能需要集成测试
- **测试命令**: `python -m unittest discover -s tests -p "test_*.py" -v`

#### 测试分类

- `test_openwebui_chat_client.py`: 主要客户端功能测试
- `test_chat_functionality.py`: 聊天功能测试
- `test_knowledge_base.py`: 知识库功能测试
- `test_notes_functionality.py`: 笔记功能测试
- `test_error_handling.py`: 错误处理测试

#### 测试编写原则

- 使用`unittest.mock`模拟外部依赖
- 测试应该独立且可重复
- 包含正常情况和异常情况的测试

### 3. 文档维护

#### 必须更新的文档

- **README.md**: 英文版本功能说明和使用指南
- **README.zh-CN.md**: 中文版本功能说明和使用指南
- **CHANGELOG.md**: 版本变更记录
- **CHANGELOG.zh-CN.md**: 中文版本变更记录

#### 文档更新要求

- 新功能必须在README中添加使用示例
- API变更必须在CHANGELOG中记录
- 文档应与代码保持同步
- 示例代码必须可执行且有效

#### CHANGELOG 管理规范

- **每次功能修改都必须更新 CHANGELOG**: 无论修改大小，任何与**模型功能**相关的增加、修改或修复都必须在 CHANGELOG 中记录。
- **未发布更改标记**: 在没有版本发布要求时，所有更改都应添加到 `[未发布]` / `[Unreleased]` 部分。
- **版本发布时转换**: 只有在正式版本发布时，才将 `[未发布]` 部分转换为具体版本号（如 `[0.1.14]`）。
- **README 更新时机**: README 文件只在版本发布时才进行更新，平时的功能修改不更新 README。
- **双语同步**: CHANGELOG.md 和 CHANGELOG.zh-CN.md 必须同时更新，保持内容一致。
- **变更分类**: 使用标准分类：`Added`/`新增`、`Changed`/`变更`、`Fixed`/`修复`、`Removed`/`移除`。
- **详细描述**: 每个变更项都应包含清晰的**模型功能**描述和影响范围。

#### 版本发布流程中的文档更新

1. **功能开发阶段**: 只更新 CHANGELOG 的 `[未发布]` 部分，不更新 README。
2. **版本发布准备**:
   - 将 `[未发布]` / `[Unreleased]` 更改为具体版本号和发布日期（如 `[0.1.16] - 2025-08-10`）
   - **关键**: 必须完全移除空的 `[未发布]` / `[Unreleased]` 部分，否则发布工作流不会触发
   - 确保新版本条目位于 CHANGELOG 文件的最顶部
   - 同时更新英文和中文版本的 CHANGELOG
   - **同步更新版本号**: 确保 `pyproject.toml` 和 `openwebui_chat_client/__init__.py` 文件中的版本号与发布版本一致。
3. **版本发布时**: 同时更新 README 文件以反映新功能和 API 变更。
4. **发布完成后**: 在 CHANGELOG 顶部添加新的 `[未发布]` 部分，准备下一轮开发。

#### 发布工作流触发机制

发布工作流通过检测 CHANGELOG.md 的更改来自动触发。关键要求：

- **工作流检查**: 提取 CHANGELOG.md 中第一个版本条目（使用 `grep -m 1 '^## \['`）
- **阻止条件**: 如果第一个版本是 "Unreleased" 或 "未发布"，工作流将**不会**触发发布
- **触发条件**: 只有当第一个版本是有效的语义化版本号（如 `0.1.22`）时，才会创建标签并触发发布流程
- **格式验证**: 版本号必须符合语义化版本规范（X.Y.Z 或 X.Y.Z-suffix）
- **文件顺序**：CHANGELOG 应该按照版本从新到旧的顺序排列，发布版本始终应该在最顶部（在标题之后）

#### 发布工作流故障排除

当发布工作流未能正确触发时，检查以下常见问题：

1. **CHANGELOG 格式检查**:

   ```bash
   # 检查第一个版本条目提取是否正确
   grep -m 1 '^## \[' CHANGELOG.md
   # 应该返回类似: ## [0.1.22] - 2025-11-18
   ```

2. **常见问题及解决方案**:
   - ❌ **问题**: CHANGELOG 第一行是 `[Unreleased]`，工作流不触发
     - ✅ **解决**: 删除 `## [Unreleased]` 或 `## [未发布]` 行，让版本号成为第一个版本条目
   - ❌ **问题**: 版本号格式不正确
     - ✅ **解决**: 确保格式为 `[X.Y.Z] - YYYY-MM-DD`，例如 `[0.1.22] - 2025-11-18`
   - ❌ **问题**: 新版本不在最顶部
     - ✅ **解决**: 将新版本移至文件开头（标题后第一个版本条目）
   - ❌ **问题**: `[Unreleased]` 部分仍在文件中
     - ✅ **解决**: 发布时完全删除此部分，待发布完成后再添加新的 `[Unreleased]`

3. **验证发布准备**:

   ```bash
   # 验证版本提取和格式
   VERSION=$(grep -m 1 '^## \[' CHANGELOG.md | sed -n 's/^## \[\(.*\)\].*/\1/p')
   echo "提取的版本: $VERSION"
   
   # 检查是否为发布版本（不应该是 Unreleased）
   if [ "$VERSION" = "Unreleased" ] || [ "$VERSION" = "未发布" ]; then
     echo "❌ 仍然是 Unreleased 状态，工作流不会触发"
   else
     echo "✅ 准备就绪，版本: $VERSION"
   fi
   ```

#### 正确的发布准备检查清单

准备发布时，必须确保：

- [ ] 将 `[未发布]` 转换为 `[X.Y.Z] - YYYY-MM-DD` 格式
- [ ] 完全移除任何空的 `[未发布]` / `[Unreleased]` 部分
- [ ] 新版本条目位于文件最顶部（在标题和介绍之后）
- [ ] 版本号遵循语义化版本规范
- [ ] 英文和中文 CHANGELOG 同步更新
- [ ] **不要在发布前添加新的 `[未发布]` 部分**（这应该在发布后进行，准备下一个开发周期）
- [ ] 版本号更新了 `pyproject.toml` 和 `openwebui_chat_client/__init__.py`
- [ ] 检查是否存在比新版本更高的版本号标签（会影响版本升级）

---
