---
description: 新功能开发完整流程
---

# 新功能开发流程

## 1. 规划阶段

1. 确定功能需求和 API 设计
2. 检查是否需要同时实现同步和异步版本
3. 确定目标 Manager 模块

## 2. 代码实现

### 同步版本
// turbo
```bash
# 在对应的 Manager 中添加方法
# 位置: openwebui_chat_client/modules/<manager_name>.py
```

### 异步版本
// turbo
```bash
# 同步添加异步版本
# 位置: openwebui_chat_client/modules/async_<manager_name>.py
```

### 主客户端暴露
// turbo
```bash
# 在主客户端中暴露新方法
# 同步: openwebui_chat_client/openwebui_chat_client.py
# 异步: openwebui_chat_client/async_openwebui_client.py
```

## 3. 代码规范检查

### 类型提示
- 所有参数必须有类型提示
- 返回值必须有类型提示
- 使用 `Optional`, `List`, `Dict`, `Any` 等

### 文档字符串
```python
def new_method(self, param1: str, param2: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    方法描述。

    Args:
        param1: 参数1描述
        param2: 参数2描述 (可选)

    Returns:
        返回值描述，或 None 如果失败
    """
```

## 4. 格式化代码
// turbo
```bash
make format
```

## 5. 运行代码检查
// turbo
```bash
make check
```

## 6. 添加单元测试

1. 在 `tests/` 目录下添加测试文件
2. 使用 `unittest.mock` 模拟外部依赖
3. 运行测试验证:
// turbo
```bash
make test
```

## 7. 更新测试映射

编辑 `.github/test-mapping.yml`:
```yaml
file_mappings:
  - pattern: "openwebui_chat_client/**/your_new_file.py"
    categories: ["your_test_category"]
```

## 8. 添加示例代码

在 `examples/` 目录下添加使用示例。

## 9. 更新 CHANGELOG

在 `CHANGELOG.md` 的 `[Unreleased]` 部分添加变更记录:
```markdown
### Added
- 新增 `new_method` 方法，支持 XXX 功能
```

同步更新 `CHANGELOG.zh-CN.md`。
