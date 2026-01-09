# Chat测试清理 - 快速参考

## 🚀 快速开始

### CI/CD（自动）
```yaml
# 在 GitHub Actions 中自动执行
# 无需额外配置，chat测试会自动清理
```

### 本地开发

```bash
# 方法 1: 启用自动清理
export OUI_CLEANUP_BEFORE_TEST=true
python examples/getting_started/basic_chat.py

# 方法 2: 手动清理
python .github/scripts/cleanup_test_chats.py

# 方法 3: 一次性启用
OUI_CLEANUP_BEFORE_TEST=true python examples/getting_started/basic_chat.py
```

---

## 📋 清理触发条件

### 自动清理的测试类别

| 测试类别 | 清理 |
|---------|------|
| `basic_chat` | ✅ |
| `async_basic_chat` | ✅ |
| `model_switching` | ✅ |
| `continuous_conversation` | ✅ |
| `sync_live_stream` | ✅ |
| `async_streaming_chat` | ✅ |
| `connectivity` | ❌ |
| `model_management` | ❌ |
| `notes_api` | ❌ |

---

## 🔧 环境变量

```bash
# 必需
export OUI_BASE_URL="http://localhost:3000"
export OUI_AUTH_TOKEN="your_token_here"

# 可选
export OUI_DEFAULT_MODEL="gpt-4.1"
export OUI_CLEANUP_BEFORE_TEST="true"  # 启用清理
```

---

## 📊 清理流程

```
1. 检测测试类别
   ↓
2. 包含 "chat" 或 "conversation"?
   ├─ 是 → 执行清理
   └─ 否 → 跳过清理
   ↓
3. 运行测试
```

---

## 🐛 常见问题

### 清理失败
```bash
# 检查认证
echo $OUI_AUTH_TOKEN

# 检查连接
curl $OUI_BASE_URL/api/health

# 手动清理
python .github/scripts/cleanup_test_chats.py
```

### 部分聊天未删除
```bash
# 多次运行清理
python .github/scripts/cleanup_test_chats.py
python .github/scripts/cleanup_test_chats.py
```

---

## 📚 相关文档

- [完整清理文档](CHAT_TEST_CLEANUP.md)
- [集成测试指南](SELECTIVE_TESTING_GUIDE.md)
- [清理脚本](.github/scripts/cleanup_test_chats.py)

---

## 💡 最佳实践

### CI/CD
- ✅ 始终启用清理
- ✅ 允许失败继续
- ✅ 记录清理日志

### 本地开发
- ✅ 默认禁用清理
- ✅ 需要时手动清理
- ✅ 使用测试账号

---

**快速帮助**: 
- 清理所有聊天: `python .github/scripts/cleanup_test_chats.py`
- 启用自动清理: `export OUI_CLEANUP_BEFORE_TEST=true`
- 查看完整文档: [CHAT_TEST_CLEANUP.md](CHAT_TEST_CLEANUP.md)
