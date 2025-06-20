import asyncio
import logging
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from mcp.actions import shell, sysinfo, process, logs, node, group
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# ========== MCP工具注册 ========== #
mcp = FastMCP("OP-MCP Server")

# 工具注册（可按需拆分到 plugins 目录或 actions 子模块，支持插件化）
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

# ========== FastAPI 主应用 ========== #
app = FastAPI(title="OP-MCP Server", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(mcp.sse_app(), prefix="/mcp")

# 兼容部分平台 POST /mcp/sse 误用，返回友好提示
router = APIRouter()

@router.post("/sse")
async def sse_post():
    return {"message": "请使用 GET 方式访问 /mcp/sse 以建立 SSE 连接"}

app.include_router(router, prefix="/mcp")

@app.get("/")
async def root():
    """服务根路由"""
    return {"message": "OP-MCP Server (FastMCP)", "version": "1.0.0"}

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}

@app.get("/mcp/")
async def mcp_root():
    """返回所有已注册工具，兼容自动化平台"""
    return {"tools": list(mcp.tools.keys())}

@app.post("/mcp/")
async def mcp_root_post():
    return {"tools": list(mcp.tools.keys())}

# ========== RESTful API 兼容 ========== #
@app.post("/node/register")
async def node_register(request: Request):
    params = await request.json()
    return node.register_node(params)

@app.get("/node/list")
async def node_list():
    return node.list_nodes()

@app.post("/group/create")
async def group_create(request: Request):
    params = await request.json()
    return group.create_group(params)

@app.get("/group/list")
async def group_list():
    return group.list_groups()

@app.post("/group/add_node")
async def group_add_node(request: Request):
    params = await request.json()
    return group.add_node_to_group(params)

@app.post("/group/remove_node")
async def group_remove_node(request: Request):
    params = await request.json()
    return group.remove_node_from_group(params)

@app.post("/node/exec")
async def node_exec(request: Request):
    params = await request.json()
    async for event in node.exec_on_node(params):
        yield event

@app.post("/group/exec")
async def group_exec(request: Request):
    params = await request.json()
    async for event in group.exec_on_group(params):
        yield event

@app.get("/sys/info")
async def sys_info():
    return sysinfo.get_sysinfo()

@app.get("/process/list")
async def process_list():
    return process.list_process()

@app.post("/process/kill")
async def process_kill(request: Request):
    params = await request.json()
    return process.kill_process(params)

@app.post("/logs/tail")
async def logs_tail(request: Request):
    params = await request.json()
    async for event in logs.get_logs(params):
        yield event

@app.get("/sse")
async def sse():
    from sse_starlette.sse import EventSourceResponse
    async def event_gen():
        while True:
            await asyncio.sleep(10)
            yield {"data": "heartbeat"}
    return EventSourceResponse(event_gen())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 