# Kubernetes MCP Server - 项目总结

## 项目概述

这是一个基于Model Context Protocol (MCP)的Kubernetes集群管理服务器，使用SSE（Server-Sent Events）传输协议实现实时通信。

## 核心文件

### 主要代码文件
- `mcp_server.py` - SSE版本的MCP服务器实现
- `k8s_client.py` - Kubernetes客户端封装
- `config.py` - 配置管理
- `main.py` - 主入口文件（兼容性）

### 部署文件
- `Dockerfile` - Docker镜像构建文件
- `docker-compose.yml` - Docker Compose配置
- `start_server.sh` - 服务器启动脚本
- `.dockerignore` - Docker构建忽略文件

### 测试和文档
- `test_mcp_client.py` - 客户端测试工具
- `README.md` - 项目文档
- `requirements.txt` - Python依赖

## 技术栈

- **后端框架**: FastAPI + SSE-Starlette
- **Kubernetes**: kubernetes Python客户端
- **容器化**: Docker + Docker Compose
- **配置管理**: Pydantic Settings
- **异步处理**: asyncio

## 主要功能

### MCP协议支持
- ✅ Server-Sent Events (SSE) 传输
- ✅ 工具调用 (Tools)
- ✅ 资源管理 (Resources)
- ✅ 实时事件流

### Kubernetes管理
- ✅ 集群信息获取
- ✅ Pod、Service、Deployment管理
- ✅ 资源日志查看
- ✅ kubectl命令执行
- ✅ 资源详情查询

### 部署特性
- ✅ 容器化部署
- ✅ 健康检查
- ✅ 权限管理
- ✅ 配置热加载
- ✅ 日志记录

## 使用方式

### 1. 快速启动
```bash
# 构建并启动
sudo ./start_server.sh

# 或使用docker-compose
sudo docker-compose up -d
```

### 2. 在Cursor中配置
```json
{
  "mcpServers": {
    "kubernetes": {
      "url": "http://localhost:8080/mcp/sse",
      "type": "sse"
    }
  }
}
```

### 3. 测试验证
```bash
python test_mcp_client.py
```

## API端点

- `GET /` - 服务器信息
- `GET /health` - 健康检查
- `GET /mcp/sse` - MCP SSE连接
- `POST /mcp/tools/list` - 列出工具
- `POST /mcp/tools/call` - 调用工具
- `GET /mcp/resources` - 列出资源
- `GET /mcp/resources/{uri}` - 读取资源

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `K8S_KUBECONFIG_PATH` | kubeconfig文件路径 | 自动检测 |
| `K8S_CONTEXT` | Kubernetes上下文 | 默认 |
| `K8S_NAMESPACE` | 默认命名空间 | default |
| `MCP_HOST` | MCP服务器主机 | localhost |
| `MCP_PORT` | MCP服务器端口 | 8080 |
| `MCP_DEBUG` | 调试模式 | false |

## 项目优势

1. **标准化**: 完全遵循MCP协议规范
2. **实时性**: SSE提供实时双向通信
3. **可扩展**: 模块化设计，易于扩展
4. **容器化**: 完整的Docker支持
5. **安全性**: 支持kubeconfig和权限控制
6. **易用性**: 简单的配置和部署流程

## 开发状态

- ✅ 核心功能完成
- ✅ SSE传输协议实现
- ✅ Kubernetes集成
- ✅ 容器化部署
- ✅ 测试工具
- ✅ 文档完善

## 未来规划

- 🔄 WebSocket支持
- �� 更多Kubernetes资源类型
- 🔄 集群监控功能
- �� 权限管理增强
- 🔄 性能优化 