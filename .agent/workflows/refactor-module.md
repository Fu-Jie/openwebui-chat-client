---
description: 模块重构指南
---

# 模块重构流程

## 1. 重构前评估

### 评估检查清单
- [ ] 明确重构目标和范围
- [ ] 列出受影响的文件
- [ ] 确认现有测试覆盖
- [ ] 评估向后兼容性影响

### 运行现有测试基线
// turbo
```bash
make test
make coverage
```

## 2. 重构原则

### 遵循项目架构
- **Manager 模式**: 每个功能领域有独立的 Manager
- **同步/异步对称**: 同步和异步版本必须同步修改
- **向后兼容**: 公开 API 变更需要 deprecation 警告

### 代码组织
```
openwebui_chat_client/
├── core/
│   ├── base_client.py        # 基础客户端
│   └── async_base_client.py  # 异步基础客户端
├── modules/
│   ├── chat_manager.py       # 同步 Manager
│   └── async_chat_manager.py # 异步 Manager
├── openwebui_chat_client.py  # 主客户端入口
└── async_openwebui_client.py # 异步主客户端入口
```

## 3. 安全重构步骤

### 步骤 1: 添加测试覆盖
如果现有测试不足，先添加测试：
```python
def test_existing_behavior(self):
    """确保重构前行为有测试覆盖"""
    pass
```

### 步骤 2: 小步修改
每次修改后运行测试：
// turbo
```bash
make test
```

### 步骤 3: 保持提交原子化
每个逻辑单元一个提交。

## 4. 常见重构场景

### 提取公共方法
```python
# 重构前
class ManagerA:
    def method_a(self):
        # 重复代码
        pass

class ManagerB:
    def method_b(self):
        # 重复代码
        pass

# 重构后
class BaseManager:
    def _common_method(self):
        # 公共代码
        pass

class ManagerA(BaseManager):
    def method_a(self):
        self._common_method()

class ManagerB(BaseManager):
    def method_b(self):
        self._common_method()
```

### 拆分大型方法
```python
# 重构前
def large_method(self):
    # 100+ 行代码
    pass

# 重构后
def large_method(self):
    self._step_1()
    self._step_2()
    self._step_3()

def _step_1(self):
    pass

def _step_2(self):
    pass

def _step_3(self):
    pass
```

### 移动方法到正确的模块
1. 在新位置创建方法
2. 在旧位置创建委托调用 + deprecation 警告
3. 更新文档
4. 下个版本移除旧方法

## 5. 验证重构

### 运行完整测试
// turbo
```bash
make ci
```

### 检查代码质量
// turbo
```bash
make check
```

### 验证覆盖率
// turbo
```bash
make coverage
```

## 6. 文档更新

### 如果有 API 变更
- 更新 README 示例
- 记录 CHANGELOG
- 添加 deprecation 说明
