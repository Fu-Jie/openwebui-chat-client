# Agent 规则和工作流使用指南

本文档介绍如何有效利用 `.agent/` 目录中的规则和工作流来提升开发效率。

---

## 📚 概述

`.agent/` 目录包含两类配置：

| 类型 | 文件 | 作用 |
|------|------|------|
| **规则** | `rules.md` | 项目规范，Agent 自动读取 |
| **工作流** | `workflows/*.md` | 开发流程，通过斜杠命令调用 |

---

## 🎯 工作流使用场景

### 场景 1: 开发新功能

**使用命令**: `/add-new-feature`

**适用情况**:

- 添加新的 API 方法
- 扩展现有功能
- 需要同时实现同步和异步版本

**示例对话**:

```text
用户: /add-new-feature 我想添加一个批量删除聊天的方法

Agent: [自动读取 workflow] 好的，按照流程我将：
1. 在 ChatManager 中添加 delete_chats_batch 方法
2. 在 AsyncChatManager 中添加异步版本
3. 在主客户端中暴露接口
...
```

---

### 场景 2: 新增 API 端点

**使用命令**: `/add-api-endpoint`

**适用情况**:

- Open WebUI 有新的 API 需要封装
- 需要完整的同步/异步实现指导
- 包含类型提示和文档字符串模板

**示例对话**:

```text
用户: /add-api-endpoint 我需要封装 /api/v1/chats/archive 端点

Agent: [自动读取 workflow] 我将按照 API 端点流程：
1. 确认 HTTP 方法和参数
2. 在 ChatManager 添加 archive_chat 方法
3. 添加异步版本
...
```

---

### 场景 3: 调试问题

**使用命令**: `/debug-issue`

**适用情况**:

- 遇到 API 调用失败
- 需要排查连接问题
- 认证或授权问题

**示例对话**:

```text
用户: /debug-issue client.chat() 返回 None，不知道什么原因

Agent: [自动读取 workflow] 让我们按调试流程排查：
1. 首先启用调试日志
2. 检查网络连接
3. 验证 token 有效性
...
```

---

### 场景 4: 运行测试

**使用命令**: `/run-tests`

**适用情况**:

- 需要运行单元测试或集成测试
- 生成覆盖率报告
- 检查特定测试类别

**示例对话**:

```text
用户: /run-tests 我想只运行笔记相关的测试

Agent: [自动读取 workflow] 运行特定测试类别：

pytest tests/test_notes_functionality.py -v
```

---

### 场景 5: 代码质量检查

**使用命令**: `/code-quality`

**适用情况**:

- 提交代码前检查
- 格式化代码
- 运行静态分析

**示例对话**:

```text
用户: /code-quality 帮我检查并修复代码格式问题

Agent: [自动读取 workflow] 执行：
1. make format (自动格式化)
2. make check (检查结果)
```

---

### 场景 6: 模块重构

**使用命令**: `/refactor-module`

**适用情况**:

- 需要安全地重构代码
- 提取公共方法
- 拆分大型函数

**示例对话**:

```text
用户: /refactor-module ChatManager 太大了，想拆分一些方法

Agent: [自动读取 workflow] 按重构流程：
1. 先运行测试建立基线
2. 小步修改，每步验证
3. 保持向后兼容
...
```

---

### 场景 7: 更新文档

**使用命令**: `/update-documentation`

**适用情况**:

- 添加新功能后更新 README
- 更新 CHANGELOG
- 版本发布前的文档同步

---

### 场景 8: 发布版本

**使用命令**: `/publish-release`

**适用情况**:

- 准备发布新版本
- 需要完整的发布检查清单
- 版本号同步验证

---

## 📋 规则自动应用

`rules.md` 文件中的规则会被 Agent **自动读取**，无需手动调用。

### 规则涵盖内容

1. **架构模式** - Manager 模式、同步/异步对称
2. **编码规范** - 类型提示、日志记录、异常处理
3. **测试映射** - 文件变更对应的测试类别
4. **错误处理模式** - 同步/异步错误处理模板

### 规则生效方式

当你进行开发时，Agent 会自动参考这些规则：

```text
用户: 帮我添加一个获取用户信息的方法

Agent: [自动参考 rules.md]
- 使用类型提示
- 添加文档字符串
- 实现错误处理
- 同时实现异步版本
```

---

## 💡 最佳实践

### 1. 复杂任务使用工作流

```text
✅ /add-new-feature 添加批量归档功能
❌ 直接说: 帮我写个批量归档的代码
```

### 2. 简单问题直接提问

```text
✅ 这个方法的返回值类型应该是什么？
❌ /add-new-feature 确认返回值类型
```

### 3. 调试时使用调试工作流

```text
✅ /debug-issue 连接超时问题
❌ 为什么连接不上？
```

### 4. 发布前完整检查

```text
✅ /publish-release 准备发布 0.1.25
❌ 直接提交并推送
```

---

## 🔧 工作流命令速查表

| 命令 | 用途 | 适用场景 |
|------|------|----------|
| `/add-new-feature` | 新功能开发 | 添加方法、扩展功能 |
| `/add-api-endpoint` | API 封装 | 封装新的 REST API |
| `/debug-issue` | 问题调试 | 排查错误、调试 |
| `/run-tests` | 运行测试 | 单元/集成测试 |
| `/code-quality` | 代码质量 | 格式化、静态检查 |
| `/refactor-module` | 模块重构 | 安全重构代码 |
| `/update-documentation` | 文档更新 | README、CHANGELOG |
| `/publish-release` | 版本发布 | 发布新版本 |
