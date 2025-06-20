# Kubernetes MCP Server (基于FastMCP)

本项目实现了一个**基于Kubernetes的MCP服务器**，通过标准MCP协议（SSE）对外暴露Kubernetes集群的常用操作工具，支持与[Cursor](https://www.cursor.so/)等MCP客户端无缝集成。

---

## 目录
- [功能简介](#功能简介)
- [依赖安装](#依赖安装)
- [快速启动](#快速启动)
- [MCP工具列表](#mcp工具列表)
- [Cursor集成指南](#cursor集成指南)
- [常见问题与排查](#常见问题与排查)
- [示例curl命令](#示例curl命令)
- [其他说明](#其他说明)

---

## 功能简介

- 通过MCP协议（SSE）暴露Kubernetes集群的常用操作：
  - 获取集群信息
  - 列出Pods/Services/Deployments
  - 获取Pod日志
  - 执行kubectl命令
  - 获取资源详细信息
- 完全兼容Cursor等MCP客户端，支持SSE事件流
- 支持本地运行与Docker容器化部署

---

## 依赖安装

建议使用Python 3.9+，推荐在虚拟环境中操作：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install fastapi uvicorn fastmcp kubernetes
```

> **注意：**
> - `fastmcp` 为MCP协议官方/社区实现库，如无此库请联系维护者或替换为你实际用到的MCP库。
> - 需提前配置好Kubernetes集群访问权限（如`~/.kube/config`）。

---

## 快速启动

### 1. 本地启动

```bash
uvicorn mcp_server:app --host 0.0.0.0 --port 8080
```

### 2. Docker启动

建议自定义Dockerfile，示例：
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -U pip \
    && pip install fastapi uvicorn fastmcp kubernetes
EXPOSE 8080
CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

构建并运行：
```bash
docker build -t k8s-mcp .
docker run -d -p 8080:8080 -v ~/.kube:/root/.kube k8s-mcp
```

---

## MCP工具列表

所有工具均以MCP标准形式暴露，可在Cursor等客户端自动发现和调用：

- `get_cluster_info()` 获取Kubernetes集群信息
- `list_pods(namespace: str = None)` 列出指定命名空间的Pod
- `list_services(namespace: str = None)` 列出指定命名空间的Service
- `list_deployments(namespace: str = None)` 列出指定命名空间的Deployment
- `get_pod_logs(pod_name: str, namespace: str = None, tail_lines: int = 100)` 获取Pod日志
- `execute_kubectl(command: str)` 执行kubectl命令（不含kubectl前缀）
- `get_resource_details(resource_type: str, resource_name: str, namespace: str = None)` 获取资源详细信息

---

## Cursor集成指南

1. 启动本服务，确保`/mcp/sse`端点可访问。
2. 在Cursor中添加MCP服务器，配置如下：
   - **URL**: `http://<你的服务器IP>:8080/mcp/sse`
   - 选择SSE协议（如有选项）
3. 保存后，Cursor会自动加载工具列表并可直接调用。

> **注意：**
> - 若Cursor端"Loading Tools"卡住，请确认服务端日志有`[SSE] 新建SSE连接...`和`[LIST] 收到list_tools请求...`等日志。
> - 若用HTTP方式配置，URL应为`http://<你的服务器IP>:8080/mcp/tools/list`，但推荐SSE方式。

---

## 常见问题与排查

- **Q: Cursor端一直"Loading Tools"？**
  - 检查服务端日志，确认有SSE连接和list_tools请求。
  - 确认Cursor配置为SSE端点（`/mcp/sse`）。
  - 检查依赖库（`fastmcp`、`fastapi`等）是否安装。
  - 检查Kubernetes集群访问权限。

- **Q: 工具调用无响应？**
  - 检查服务端日志有无call_tool相关日志。
  - 检查参数是否填写正确。

- **Q: Docker容器无法访问Kubernetes？**
  - 挂载本地kubeconfig到容器（如`-v ~/.kube:/root/.kube`）。
  - 检查容器内kubectl权限。

---

## 示例curl命令

1. **SSE事件流测试**
   ```bash
   curl -N http://localhost:8080/mcp/sse
   ```
2. **获取工具列表**
   ```bash
   curl -X POST http://localhost:8080/mcp/tools/list \
     -H "Content-Type: application/json" \
     -d '{"id": "test-1", "session_id": "<你的session_id>"}'
   ```
3. **调用工具示例**
   ```bash
   curl -X POST http://localhost:8080/mcp/tools/call \
     -H "Content-Type: application/json" \
     -d '{"id": "test-2", "session_id": "<你的session_id>", "name": "get_cluster_info", "arguments": {}}'
   ```

---

## 其他说明

- 如需扩展自定义MCP工具，只需用`@mcp.tool()`装饰器声明新函数即可。
- 如需暴露资源型API，可用`@mcp.resource()`。
- 如遇到协议兼容性问题，建议优先升级`fastmcp`和Cursor到最新版。

---

如有更多问题或定制需求，欢迎提Issue或联系维护者！ 