import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from functools import wraps
import inspect
import logging

logger = logging.getLogger("mcp_server")

class FastMCP:
    def __init__(self, name="FastMCP Server"):
        self.name = name
        self.tools = {}
        self.router = APIRouter()
        self._register_routes()

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            logger.info(f"工具註冊: {func.__name__}")
            return func  # 返回原始函數，避免wrapper導致inspect失效
        return decorator

    def _register_routes(self):
        @self.router.get("/tools")
        async def list_tools():
            """列出所有可用工具及参数信息"""
            tool_list = []
            for name, func in self.tools.items():
                sig = inspect.signature(func)
                params = {k: str(v.annotation) for k, v in sig.parameters.items()}
                doc = func.__doc__ or ""
                tool_list.append({
                    "name": name,
                    "description": doc.strip(),
                    "params": params
                })
            return {"tools": tool_list}

        @self.router.post("/invoke/{tool_name}")
        async def invoke_tool(tool_name: str, request: Request):
            """调用指定工具"""
            if tool_name not in self.tools:
                return {"error": f"Tool {tool_name} not found"}
            params = await request.json()
            func = self.tools[tool_name]
            if asyncio.iscoroutinefunction(func):
                result = await func(**params)
            else:
                result = func(**params)
            return result

        @self.router.get("/sse")
        async def sse():
            async def event_gen():
                while True:
                    await asyncio.sleep(10)
                    yield {"data": "heartbeat"}
            return EventSourceResponse(event_gen())

    def sse_app(self):
        return self.router 