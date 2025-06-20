# MCP Server & Agent 多主机远程运维平台

## 项目简介
本项目实现了基于中心-代理（Server-Agent）架构的多主机远程运维平台。支持节点注册、分组管理、批量/单节点命令下发、系统信息查询、进程管理、日志拉取等功能。所有节点和分组信息持久化存储于SQLite数据库。

---

## 目录结构
```
op-mcp/
├── main.py           # MCP Server 入口
├── Dockerfile        # Server 容器化部署
├── requirements.txt  # 依赖
├── mcp/              # 业务逻辑模块
└── agent_main.py     # MCP Agent（需单独部署在被控主机）
```

---

## 一、MCP Server 使用说明

### 1. 启动 Server

```bash
git clone <本项目>
cd op-mcp
docker build -t op-mcp .
docker run -d -p 8000:8000 --name op-mcp op-mcp
```
或本地运行：
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. 主要接口

- **节点注册**：`POST /node/register`  
- **节点列表**：`GET /node/list`
- **分组管理**：`POST /group/create`、`GET /group/list`、`POST /group/add_node`、`POST /group/remove_node`
- **单节点命令执行**：`POST /node/exec`（SSE）
- **分组批量命令执行**：`POST /group/exec`（SSE）
- **系统信息**：`GET /sys/info`
- **进程管理**：`GET /process/list`、`POST /process/kill`
- **日志拉取**：`POST /logs/tail`（SSE）
- **通用SSE心跳**：`GET /sse`

> 详细API可访问 `http://<server>:8000/docs` 查看Swagger文档。

---

## 二、MCP Agent 使用说明

### 1. agent_main.py 示例
将 `agent_main.py` 部署在每台被控主机，内容如下：

```python
# 见上文 agent_main.py 示例
```

### 2. 启动 Agent

```bash
pip install fastapi uvicorn requests
export MCP_SERVER_URL="http://<server_ip>:8000"
python agent_main.py
```

Agent 启动后会自动注册到 MCP Server，并监听 9000 端口（可通过 `MCP_AGENT_PORT` 环境变量修改）。

---

## 三、典型使用流程

1. **部署 MCP Server**，启动服务
2. **在每台主机部署 MCP Agent**，自动注册到 Server
3. **通过 Server API 创建分组、管理节点**
4. **通过 `/node/exec` 或 `/group/exec` 下发命令**，Server 自动转发到对应 Agent，Agent 执行并回传结果
5. **通过 SSE 实时获取命令执行结果**

---

## 四、常见问题

- **命令实际在 Agent 主机执行，Server 只负责转发和收集结果**
- **所有节点和分组信息持久化在 SQLite（mcp.db）**
- **接口无鉴权，生产环境请加认证机制**
- **Agent 与 Server 网络需互通，端口默认 8000（Server）和 9000（Agent）**

---

## 五、扩展建议
- 支持命令超时、失败重试
- 支持 Agent 认证、加密通信
- 支持 WebSocket 实时推送
- 支持节点/分组删除、更多运维模块

---

如有问题欢迎提 issue 或联系作者。 