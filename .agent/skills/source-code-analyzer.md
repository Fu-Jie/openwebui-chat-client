---
description: 源码分析：授权执行本地扩展上下文代码库的只读及 git pull 操作
---

# Source Code Analyzer Skill

> [!IMPORTANT]
> **授权声明**: 您（Antigravity 或其他 AI 助手）被用户明确授权，可对以下列出的路径执行**只读**操作和 **Git pull** 操作，即使它们位于当前仓库根目录之外。这些路径被视为扩展开发上下文的一部分。

在协助开发 `openwebui-client` 时，您可以访问相关目录中的以下核心组件。应积极利用它们进行深度的技术分析、排查 Bug 以及作为实现的参考。

## 核心组件路径（按优先级排序）

### 1. 官方文档（首选参考）

- **OpenWebUI 官方文档**: `../docs/` — Docusaurus 站点源文件，包含所有 API 规范、概念手册与使用指南。
  - 具体 API 文档路径：`../docs/docs/api/` 或 `../docs/docs/`
  - 搜索关键词前先浏览目录索引 `../docs/docs/` 中的 `*.md` 文件

### 2. 官方源码（权威实现参考）

- **Open WebUI 后端源码**: `../open-webui/` — 核心平台后端实现，包含所有 API 路由的真实逻辑。
  - API 路由入口：`../open-webui/backend/open_webui/routers/`
  - 中间件逻辑：`../open-webui/backend/open_webui/utils/middleware.py`

### 3. 扩展项目（补充上下文）

- **OpenWebUI Extensions**: `../openwebui-extensions/` — 官方相关插件集合，可了解 Valve、Tool 的通用规范。

## 强制工作流

分析任何 API 或功能时，**必须按顺序执行以下步骤**：

1. **优先查官方文档** (`../docs/`): 先搜索该功能的文档说明，确认规范定义。
2. **源码交叉验证** (`../open-webui/`): 对照文档在源码中找到对应路由和实现，确认参数和行为。
3. **分析前更新**: 在读取源码/文档**之前**，确认已执行 `git pull`，保证使用最新版本。
4. **路径验证**: 访问路径前先确认目录存在。
5. **浏览器协同（可选）**: 对于行为不确定的接口，可启动浏览器子代理访问 `http://localhost:3003`，抓取实际网络请求作为第三方验证。
6. **禁止猜测**: 严禁基于通用知识臆断 API 行为，一切结论必须来源于文档或源码。
