# 规则3：开发与发布工作流

## 1. 功能开发

-   **新功能**: 在`openwebui_chat_client/`中添加新方法时，请遵循现有的编码规范（见`02-coding-style.md`）。
-   **测试映射**: 新功能开发时，必须同步更新`.github/test-mapping.yml`，添加相应的文件模式映射和测试类别，确保CI/CD工作流能正确检测和运行相关集成测试。


## 2. 文档更新

-   **README**: 在添加新功能或进行重大变更后，必须同步更新`README.md`和`README.zh-CN.md`中的功能列表和使用说明。
-   **CHANGELOG**: 每次发布前，必须在`CHANGELOG.md`中记录所有变更。条目应清晰、简洁，并遵循现有的格式。

## 3. 发布流程

-   **CHANGELOG驱动发布**: 发布流程通过检测CHANGELOG.md的更新自动触发。当CHANGELOG.md中出现新的版本条目（格式如`[0.1.14] - 2025-08-10`）时，会自动创建Git标签并触发发布工作流。
-   **版本号管理**: 版本号必须遵循语义化版本规范（X.Y.Z或X.Y.Z-suffix）。发布前确保`pyproject.toml`和`openwebui_chat_client/__init__.py`中的版本号与CHANGELOG一致。
-   **GitHub Actions工作流**:
  - `test.yml`: 在push和PR时运行单元测试，支持Python 3.8-3.13多版本测试
  - `integration-test.yml`: 基于文件变更的智能选择性集成测试，使用`.github/test-mapping.yml`映射配置
  - `publish.yml`: 自动构建、测试、发布到PyPI并创建GitHub Release
-   **PyPI发布要求**: 需要配置`PYPI_API_TOKEN`仓库密钥，用于自动发布到PyPI。
-   **CHANGELOG管理规范**:
  - 开发期间：所有变更记录在`[Unreleased]`部分
  - 发布准备：将`[Unreleased]`转换为具体版本号（如`[0.1.14]`）
  - 发布后：在CHANGELOG顶部添加新的`[Unreleased]`部分
  - 必须同时更新`CHANGELOG.md`和`CHANGELOG.zh-CN.md`

## 4. 集成测试系统

-   **选择性测试**: 项目采用智能选择性集成测试系统，根据文件变更自动选择相关测试类别，显著提升CI效率。
-   **测试映射配置**: 使用`.github/test-mapping.yml`定义文件模式到测试类别的映射关系。
-   **测试类别**: 包括connectivity、basic_chat、notes_api、prompts_api、rag_integration、model_management、model_switching、comprehensive_demos、continuous_conversation、deep_research等。
-   **环境变量**: 集成测试需要配置OUI_BASE_URL、OUI_AUTH_TOKEN、OUI_DEFAULT_MODEL等环境变量或GitHub Secrets。
-   **本地测试**: 可以使用`run_integration_tests.py`或`.github/scripts/run_all_integration_tests.py`进行本地集成测试。

## 5. 未来开发方向

-   **API同步**: 持续关注OpenWebUI的官方更新，当出现新API或API变更时，应优先在客户端中进行适配。
-   **效率提升**: 鼓励并优先开发能显著提高使用和维护效率的自动化、批量化功能。
