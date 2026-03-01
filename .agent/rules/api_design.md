## API设计标准

### 1. 方法命名规范

#### 核心方法类型

- **聊天相关**: `chat()`, `stream_chat()`, `parallel_chat()`
- **管理相关**: `list_*()`, `get_*()`, `create_*()`, `update_*()`, `delete_*()`
- **批量操作**: `*_all()`, `*_by_keyword()`
- **状态管理**: `rename_*()`, `set_*()`, `switch_*()`

#### 参数设计原则

- **必需参数**: 放在前面，类型明确
- **可选参数**: 使用默认值，支持None
- **批量参数**: 使用List类型，支持空列表
- **标识参数**: 使用字符串ID，支持验证

### 2. 返回值标准

#### 成功返回

- **单一对象**: 返回Dict包含核心数据和元数据
- **列表对象**: 返回List[Dict]或空列表
- **操作结果**: 返回包含状态和相关ID的Dict

#### 失败处理

- **返回None**: 当操作失败且可恢复时
- **抛出异常**: 当遇到不可恢复的错误时
- **记录日志**: 所有失败情况都必须记录详细日志

### 3. 并发处理

#### ThreadPoolExecutor使用

- 用于并行API请求
- 提升批量操作效率
- 合理控制并发数量

#### 示例模式

```python
def parallel_operation(self, items: List[str]) -> Dict[str, Any]:
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_item = {
            executor.submit(self._single_operation, item): item 
            for item in items
        }
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                results[item] = future.result()
            except Exception as e:
                logger.error(f"Failed to process {item}: {e}")
                results[item] = None
    return results
```

---

---
