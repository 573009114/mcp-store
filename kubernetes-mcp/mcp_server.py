"""
Kubernetes MCP服务器 - 工具化重构版
所有核心功能均以MCP工具暴露
"""
import asyncio
import json
import uuid
from typing import Dict, Any
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from k8s_client import KubernetesClient
from config import config
import uvicorn
from sse_starlette.sse import EventSourceResponse
import logging
from mcp.server.fastmcp import FastMCP
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# 创建MCP服务器实例
mcp = FastMCP("Kubernetes MCP Server")
k8s_client = KubernetesClient()

# 工具暴露
@mcp.tool()
async def get_cluster_info() -> dict:
    return await k8s_client.get_cluster_info()

@mcp.tool()
async def list_pods(namespace: str = None) -> dict:
    return await k8s_client.list_pods(namespace)

@mcp.tool()
async def list_services(namespace: str = None) -> dict:
    return await k8s_client.list_services(namespace)

@mcp.tool()
async def list_deployments(namespace: str = None) -> dict:
    return await k8s_client.list_deployments(namespace)

@mcp.tool()
async def get_pod_logs(pod_name: str, namespace: str = None, tail_lines: int = 100) -> dict:
    return await k8s_client.get_pod_logs(pod_name, namespace, tail_lines)

@mcp.tool()
async def execute_kubectl(command: str) -> dict:
    return await k8s_client.execute_kubectl(command)

@mcp.tool()
async def get_resource_details(resource_type: str, resource_name: str, namespace: str = None) -> dict:
    return await k8s_client.get_resource_details(resource_type, resource_name, namespace)

# FastAPI主应用
app = FastAPI(title="Kubernetes MCP Server", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/mcp/", mcp.sse_app())

@app.get("/")
async def root():
    return {"message": "Kubernetes MCP Server (FastMCP)", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/cluster/info", response_class=JSONResponse)
async def cluster_info():
    """获取当前MCP连接的集群关键信息"""
    result = await get_cluster_info()
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host=config.mcp.host, port=config.mcp.port) 