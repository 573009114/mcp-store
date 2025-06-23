import subprocess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from fastapi.responses import JSONResponse
import uvicorn
import sqlite3
import os

# MCP工具化服务器
mcp = FastMCP("Linux MCP Server")

# shell命令
@mcp.tool()
def shell(command: str) -> dict:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

# systemd服务管理
@mcp.tool()
def systemd(action: str, service: str) -> dict:
    cmd = f"systemctl {action} {service}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

# 日志tail
@mcp.tool()
def logs(path: str, lines: int = 50) -> dict:
    cmd = f"tail -n {lines} {path}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

# 进程管理
@mcp.tool()
def process(op: str, pid: int = None) -> dict:
    if op == "list":
        cmd = "ps aux"
    elif op == "kill" and pid:
        cmd = f"kill {pid}"
    else:
        return {"error": "参数错误，op必须为list或kill，kill时需提供pid"}
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

# 系统信息
@mcp.tool()
def sysinfo(info_type: str) -> dict:
    if info_type == "mem":
        cmd = "free -h"
    elif info_type == "disk":
        cmd = "df -h"
    elif info_type == "load":
        cmd = "uptime"
    elif info_type == "net":
        cmd = "ifconfig || ip addr"
    else:
        return {"error": "type参数必须为mem/disk/load/net"}
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

# 简单CMDB（sqlite实现）
DB_PATH = os.path.join(os.path.dirname(__file__), 'cmdb.db')
def get_conn():
    return sqlite3.connect(DB_PATH)

@mcp.tool()
def create_host(hostname: str, ip: str, os: str, group: str = None) -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS hosts (id INTEGER PRIMARY KEY, hostname TEXT, ip TEXT, os TEXT, groupname TEXT)')
    c.execute('INSERT INTO hosts (hostname, ip, os, groupname) VALUES (?, ?, ?, ?)', (hostname, ip, os, group))
    conn.commit()
    conn.close()
    return {"msg": "ok"}

@mcp.tool()
def list_hosts() -> list:
    conn = get_conn()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS hosts (id INTEGER PRIMARY KEY, hostname TEXT, ip TEXT, os TEXT, groupname TEXT)')
    rows = c.execute('SELECT id, hostname, ip, os, groupname FROM hosts').fetchall()
    conn.close()
    return [{"id": r[0], "hostname": r[1], "ip": r[2], "os": r[3], "group": r[4]} for r in rows]

# FastAPI主应用
app = FastAPI(title="Linux MCP Server", version="1.0.0")
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
    return {"message": "Linux MCP Server (FastMCP)", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 