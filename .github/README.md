# GitHub Actions 配置

## 📋 目录

- [工作流概述](#工作流概述)
- [选择性集成测试](#选择性集成测试)
- [快速开始](#快速开始)
- [文档资源](#文档资源)

---

## 工作流概述

### 核心工作流

| 工作流 | 触发条件 | 用途 |
|--------|---------|------|
| `test.yml` | Push/PR | 单元测试（Python 3.8-3.13） |
| `integration-test.yml` | Test完成后 | **选择性集成测试** |
| `code-quality.yml` | Push/PR | 代码质量检查 |
| `coverage.yml` | Push/PR | 代码覆盖率报告 |
| `publish.yml` | 标签推送 | 发布到PyPI |
| `pr-automation.yml` | PR创建 | PR自动化 |
| `dependency-review.yml` | PR | 依赖安全审查 |

---

## 选择性集成测试

### 🎯 核心特性

本项目采用**精确的选择性集成测试系统**：

- ✅ **51个精确映射规则** - 每个核心文件都有明确的测试映射
- ✅ **70-85%测试减少** - 只运行相关测试
- ✅ **70-80%时间节省** - CI从15分钟减少到3-6分钟
- ✅ **详细日志输出** - 清楚了解测试选择过程
- ✅ **完善工具链** - 验证、测试、调试工具齐全

### 📊 效率对比

```
修改聊天管理器示例:
┌─────────────────────────────────────┐
│ 优化前: 9个测试 (15分钟)            │
│ ├─ connectivity                     │
│ ├─ basic_chat                       │
│ ├─ model_management                 │
│ ├─ model_switching                  │
│ ├─ comprehensive_demos              │
│ ├─ deep_research                    │
│ ├─ process_task                     │
│ ├─ stream_process_task              │
│ └─ decision_model                   │
└─────────────────────────────────────┘
              ↓ 优化
┌─────────────────────────────────────┐
│ 优化后: 3个测试 (4分钟)             │
│ ├─ basic_chat                       │
│ ├─ model_switching                  │
│ └─ continuous_conversation          │
└─────────────────────────────────────┘
效率提升: 67% ⚡
```

### 🔧 工作原理

1. **文件变更检测** - 自动分析Git diff
2. **精确模式匹配** - 精确路径优先于通配符
3. **测试类别选择** - 只选择相关的测试类别
4. **并行执行** - 使用GitHub Actions矩阵策略

---

## 快速开始

### 验证测试映射

```bash
# 验证配置文件
python .github/scripts/validate_test_mapping.py

# 测试特定文件
python .github/scripts/validate_test_mapping.py \
  --test-file "openwebui_chat_client/modules/chat_manager.py"

# 查看所有映射
python .github/scripts/validate_test_mapping.py --show-all
```

### 本地模拟CI检测

```bash
# 查看当前变更会触发哪些测试
export VERBOSE=true
python .github/scripts/detect_required_tests.py
```

### 添加新功能映射

1. 编辑 `test-mapping.yml`:
```yaml
test_categories:
  your_test:
    name: "Your Test"
    command: "python examples/your_feature/test.py"
    description: "Tests your feature"

file_mappings:
  - pattern: "openwebui_chat_client/modules/your_manager.py"
    categories: ["your_test"]
    description: "Your manager - triggers your test"
```

2. 验证配置:
```bash
python .github/scripts/validate_test_mapping.py
```

---

## 文档资源

### 📚 完整文档

- **[选择性测试完整指南](SELECTIVE_TESTING_GUIDE.md)** - 详细的使用指南和最佳实践
- **[快速参考手册](TESTING_QUICK_REFERENCE.md)** - 常用命令和映射表
- **[使用示例](EXAMPLES.md)** - 8个实际使用案例
- **[优化总结](../INTEGRATION_TEST_OPTIMIZATION_SUMMARY.md)** - 优化成果和性能数据

### 🔧 配置文件

- **[test-mapping.yml](test-mapping.yml)** - 核心配置文件（51个映射规则）
- **[工作流说明](workflows/README.md)** - 所有工作流的详细说明

### 🛠️ 工具脚本

- **[validate_test_mapping.py](scripts/validate_test_mapping.py)** - 配置验证工具
- **[detect_required_tests.py](scripts/detect_required_tests.py)** - 测试检测脚本
- **[run_all_integration_tests.py](scripts/run_all_integration_tests.py)** - 测试运行器

---

## 核心文件映射速查

### 同步客户端
```
openwebui_chat_client/
├── openwebui_chat_client.py     → 5个测试
├── core/base_client.py          → 3个测试
└── modules/
    ├── chat_manager.py          → 3个测试
    ├── model_manager.py         → 2个测试
    ├── notes_manager.py         → 1个测试
    ├── prompts_manager.py       → 1个测试
    └── knowledge_base_manager.py → 1个测试
```

### 异步客户端
```
openwebui_chat_client/
├── async_openwebui_client.py    → 7个测试
├── core/async_base_client.py    → 3个测试
└── modules/
    ├── async_chat_manager.py    → 2个测试
    ├── async_model_manager.py   → 1个测试
    └── async_notes_manager.py   → 1个测试
```

---

## 🎯 最佳实践

1. ✅ **提交前验证** - 使用工具检查测试映射
2. ✅ **精确映射** - 优先使用精确路径而非通配符
3. ✅ **同步更新** - 新功能同步更新映射配置
4. ✅ **定期审查** - 每月检查配置健康度
5. ✅ **监控效果** - 关注CI运行时间和测试触发情况

---

## 📊 性能指标

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 平均触发测试数 | 8-12个 | 1-3个 | **70-85%↓** |
| CI运行时间 | 15-20分钟 | 3-6分钟 | **70-80%↓** |
| 资源使用 | 高 | 低 | **60-75%↓** |
| 测试精确度 | 低 | 高 | **显著提升** |

---

## 🆘 获取帮助

### 常见问题

1. **测试没有触发?**
   ```bash
   python .github/scripts/validate_test_mapping.py --test-file "your_file.py"
   ```

2. **触发了错误的测试?**
   - 检查 `test-mapping.yml` 中的映射规则
   - 使用验证工具确认映射

3. **配置验证失败?**
   ```bash
   python .github/scripts/validate_test_mapping.py
   # 查看详细错误信息
   ```

### 调试技巧

```bash
# 启用详细日志
export VERBOSE=true

# 查看文件匹配过程
python .github/scripts/detect_required_tests.py

# 查看所有映射规则
python .github/scripts/validate_test_mapping.py --show-all
```

---

## 🔗 相关链接

- [主项目README](../README.md)
- [CI/CD设置总结](../CI_CD_SETUP_SUMMARY.md)
- [开发指南](../docs/DEVELOPMENT.md)
- [贡献指南](../CONTRIBUTING.md)

---

**最后更新**: 2025-01-09  
**维护者**: openwebui-chat-client 团队
