from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from mcp.actions import shell, sysinfo, process, logs, node, group
import uvicorn

# 创建 MCP 服务器实例
mcp = FastMCP("OP-MCP Server")

# 工具暴露
@mcp.tool()
async def run_shell(cmd: str) -> dict:
    """在本地或远程节点执行 shell 命令"""
    gen = shell.run_shell({"cmd": cmd})
    try:
        event = await gen.__anext__()
        return event
    except StopAsyncIteration:
        return {"error": "No output"}

@mcp.tool()
def get_sysinfo() -> dict:
    """获取系统信息"""
    return sysinfo.get_sysinfo()

@mcp.tool()
def list_process() -> dict:
    """列出进程"""
    return process.list_process()

@mcp.tool()
def kill_process(pid: int) -> dict:
    """结束进程"""
    return process.kill_process({"pid": pid})

@mcp.tool()
async def get_logs(path: str, lines: int = 100) -> dict:
    """拉取日志文件内容"""
    gen = logs.get_logs({"path": path, "lines": lines})
    try:
        event = await gen.__anext__()
        return event
    except StopAsyncIteration:
        return {"error": "No output"}

@mcp.tool()
async def exec_on_node(ip: str, cmd: str) -> dict:
    """在指定节点远程执行命令"""
    gen = node.exec_on_node({"ip": ip, "cmd": cmd})
    try:
        event = await gen.__anext__()
        return event
    except StopAsyncIteration:
        return {"error": "No output"}

@mcp.tool()
async def exec_on_group(group: str, cmd: str) -> dict:
    """在分组内所有节点批量执行命令"""
    gen = group.exec_on_group({"group": group, "cmd": cmd})
    try:
        event = await gen.__anext__()
        return event
    except StopAsyncIteration:
        return {"error": "No output"}

@mcp.tool()
def list_nodes() -> dict:
    """查询所有节点"""
    return node.list_nodes()

@mcp.tool()
def list_groups() -> dict:
    """查询所有分组"""
    return group.list_groups()

# FastAPI 主应用
app = FastAPI(title="OP-MCP Server", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(mcp.sse_app(), prefix="/mcp")

@app.get("/")
async def root():
    return {"message": "OP-MCP Server (FastMCP)", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# 关键：为 /mcp/ 路径添加 GET 和 POST 路由，兼容 MCP Tools
@app.get("/mcp/")
async def mcp_root():
    return {"message": "MCP Server Root", "tools": list(mcp.tools.keys())}

@app.post("/mcp/")
async def mcp_root_post():
    return {"message": "MCP Server Root POST", "tools": list(mcp.tools.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 