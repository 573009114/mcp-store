# Linux MCP Server（工具化重构版）

## 项目简介
本项目是基于 FastAPI + FastMCP 的 Linux 运维自动化平台核心模块。所有运维能力均以 MCP 工具（@mcp.tool 装饰器）方式暴露，支持通过 MCP 协议和 HTTP API 实现主机控制、资源管理和自动化运维。

## 主要特性
- 所有运维能力（shell、systemd、日志、进程、系统信息、CMDB）均以工具形式暴露
- 支持 SSE/MCP 协议与 Cursor/Agent 等客户端集成
- FastAPI 提供健康检查与基础 HTTP 路由
- 结构极简，易于扩展和二次开发

## 快速启动

### 1. 本地运行
```bash
pip install -r requirements.txt
python server.py
# 或
uvicorn server:app --host 0.0.0.0 --port 8000
```

### 2. Docker 一键部署
```bash
./deploy.sh build
./deploy.sh start
```

## API 用法

### MCP 协议（SSE/意图下发）
- 通过 `/mcp/` 路由对接 MCP Client（如 Cursor/Agent），支持意图下发与结果回传。
- 工具示例：
```json
{
  "tool": "shell",
  "args": {"command": "df -h"}
}
```

### FastAPI 基础接口
- `GET /`         服务器欢迎页
- `GET /health`   健康检查

## 支持的MCP工具
- `shell(command: str)`         执行任意 shell 命令
- `systemd(action, service)`    systemd 服务管理（start/stop/restart/status）
- `logs(path, lines=50)`        拉取日志片段
- `process(op, pid=None)`       进程管理（op=list/kill）
- `sysinfo(info_type)`          系统信息（mem/disk/load/net）
- `create_host(...)`            新增主机（CMDB）
- `list_hosts()`                查询主机列表（CMDB）

## CMDB 说明
- 内置 sqlite3 数据库，文件为 `cmdb.db`
- 支持主机信息的增删查
- 可按需扩展更多资源类型

## 扩展方式
- 直接在 `server.py` 内新增 `@mcp.tool()` 装饰器函数即可扩展新运维能力
- 支持同步和异步函数

## 许可证
MIT

## 目录结构
```
op-mcp/
├── Dockerfile        # 服务端容器化部署
├── deploy.sh         # 一键构建/启动/停止脚本
├── server.py         # fastmcp 服务端入口（可选/可自定义）
├── agent_main.py     # MCP Agent 示例
├── requirements.txt  # agent 端依赖
└── README.md
```

## 一、MCP Server 使用说明
### 1. 启动 Server
- 推荐方式：
  - 在本地准备好 server.py（见下方示例），然后：
  ```bash
  ./deploy.sh build
  ./deploy.sh start
  ```
- 也可直接用 fastmcp 官方demo：
  ```python
  # server.py 示例
  from fastmcp import FastMCP
  mcp = FastMCP("Demo Server")
  @mcp.tool
def hello(name: str) -> str:
      return f"Hello, {name}!"
  if __name__ == "__main__":
      mcp.run()
  ```
- 访问 http://<server>:8000/mcp 进行交互。

### 2. 主要脚本说明
- `deploy.sh build`  构建镜像
- `deploy.sh start`  启动容器（自动挂载 server.py）
- `deploy.sh stop`   停止并删除容器
- `deploy.sh rmimg`  删除镜像
- `deploy.sh logs`   查看容器日志

## 二、MCP Agent 使用说明
- 进入 agent_main.py 所在目录，安装依赖：
  ```bash
  pip install -r requirements.txt
  export MCP_SERVER_URL="http://<server_ip>:8000"
  python agent_main.py
  ```
- agent 启动后会自动注册到 MCP Server。

## 其他说明
- 服务端所有API、工具、资源均可通过自定义 server.py 进行扩展，详见 fastmcp 官方文档：https://github.com/jlowin/fastmcp
- agent_main.py 可根据实际需求扩展。 