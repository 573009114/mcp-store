# MCP Server & Agent 多主机远程运维平台（升级版）

## 项目简介
本项目基于 FastAPI，采用插件化、自动发现的 MCP 工具注册机制，支持多主机远程运维、节点分组、批量命令、系统信息、进程管理、日志拉取等。所有功能均以工具形式暴露，便于自动化平台集成和二次开发。

---

## 目录结构
```
op-mcp/
├── main.py           # MCP Server 入口（插件化、自动发现工具）
├── Dockerfile        # Server 容器化部署
├── requirements.txt  # 依赖
├── mcp/              # 业务逻辑模块
│   ├── actions/      # 各类运维工具实现
│   └── server/       # FastMCP 核心
└── agent_main.py     # MCP Agent（需单独部署在被控主机）
```

---

## 一、MCP Server 使用说明

### 1. 启动 Server

```bash
git clone <本项目>
cd op-mcp
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. 主要接口

- **工具自动发现**：`GET /mcp/` 返回所有已注册工具
- **工具详细信息**：`GET /mcp/tools`
- **工具调用**：`POST /mcp/invoke/{tool_name}`
- **节点注册/列表**：`POST /node/register`、`GET /node/list`
- **分组管理**：`POST /group/create`、`GET /group/list`、`POST /group/add_node`、`POST /group/remove_node`
- **命令下发**：`POST /node/exec`、`POST /group/exec`
- **系统信息**：`GET /sys/info`
- **进程管理**：`GET /process/list`、`POST /process/kill`
- **日志拉取**：`POST /logs/tail`
- **SSE心跳**：`GET /sse`
- **健康检查**：`GET /health`

> 详细API可访问 `http://<server>:8000/docs` 查看Swagger文档。

---

## 二、插件化与扩展

- 所有工具均以 `@mcp.tool()` 装饰器注册，自动暴露，无需手动维护工具列表。
- 新增工具只需在 `main.py` 或 `mcp/actions/` 下实现函数并加装饰器。
- 支持异步/同步工具，参数自动解析。
- 可按需拆分为 plugins 目录，支持热插拔。

---

## 三、Agent 使用说明

详见 `agent_main.py`，部署在被控主机，自动注册到 Server。

---

## 四、常见问题

- 工具未被发现：请确认注册代码在全局作用域，且无循环依赖。
- 前端自动化平台无法识别：请用 `/mcp/` 路由，返回格式为 `{ "tools": [...] }`。
- 依赖缺失：请用 `pip install -r requirements.txt` 安装依赖。

---

## 五、扩展建议
- 支持命令超时、失败重试
- 支持 Agent 认证、加密通信
- 支持 WebSocket 实时推送
- 支持节点/分组删除、更多运维模块

---

如有问题欢迎提 issue 或联系作者。 