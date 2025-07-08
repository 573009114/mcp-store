import subprocess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from fastapi.responses import JSONResponse
import uvicorn
import sqlite3
import os
from mycmcp.cmdb.models import Host, Account
from mycmcp.cmdb.crud import create_host_with_account as crud_create_host_with_account, get_hosts, get_accounts, get_session
import paramiko
from mycmcp.cmdb.database import init_db
from typing import Optional

# MCP工具化服务器
mcp = FastMCP("Linux MCP Server")

# shell命令
@mcp.tool()
def shell(command: str, host_id: Optional[int] = None) -> dict:
    if host_id:
        return remote_exec(host_id, command)
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
def systemd(action: str, service: str, host_id: Optional[int] = None) -> dict:
    cmd = f"systemctl {action} {service}"
    if host_id:
        return remote_exec(host_id, cmd)
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
def logs(path: str, lines: int = 50, host_id: Optional[int] = None) -> dict:
    cmd = f"tail -n {lines} {path}"
    if host_id:
        return remote_exec(host_id, cmd)
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
def process(op: str, pid: int = None, host_id: Optional[int] = None) -> dict:
    if op == "list":
        cmd = "ps aux"
    elif op == "kill" and pid:
        cmd = f"kill {pid}"
    else:
        return {"error": "参数错误，op必须为list或kill，kill时需提供pid"}
    if host_id:
        return remote_exec(host_id, cmd)
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
def sysinfo(info_type: str, host_id: Optional[int] = None) -> dict:
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
    if host_id:
        return remote_exec(host_id, cmd)
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
    hosts = get_hosts()
    return [
        {
            "id": h.id,
            "hostname": h.hostname,
            "ip": h.ip,
            "os": h.os,
            "group": h.group
        }
        for h in hosts
    ]

@mcp.tool("create_host_with_account")
def create_host_with_account_tool(hostname: str, ip: str, os: str, group: str, username: str, password: str) -> dict:
    host = Host(hostname=hostname, ip=ip, os=os, group=group)
    account = Account(username=username, password=password)
    h, a = crud_create_host_with_account(host, account)
    return {"msg": "ok", "host_id": h['id'], "account_id": a['id']}

@mcp.tool()
def remote_exec(host_id: int, command: str) -> dict:
    hosts = get_hosts()
    accounts = get_accounts()
    host = next((h for h in hosts if h.id == host_id), None)
    account = next((a for a in accounts if a.host_id == host_id), None)
    if not host or not account:
        return {"error": "未找到主机或账号"}
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host.ip, username=account.username, password=account.password)
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode()
        err = stderr.read().decode()
        ssh.close()
        return {"stdout": result, "stderr": err}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def fix_account_host_link() -> dict:
    hosts = get_hosts()
    accounts = get_accounts()
    fixed = 0
    if len(hosts) == 1:
        host_id = hosts[0].id
        for a in accounts:
            if not a.host_id:
                a.host_id = host_id
                a.save() if hasattr(a, 'save') else None
                fixed += 1
    else:
        # 多主机时可按用户名/主机名等策略补充
        pass
    return {"fixed": fixed, "total_accounts": len(accounts)}

@mcp.tool()
def delete_host(host_id: int) -> dict:
    with get_session() as session:
        # 删除关联账号
        session.query(Account).filter(Account.host_id == host_id).delete()
        # 删除主机
        deleted = session.query(Host).filter(Host.id == host_id).delete()
        session.commit()
    return {"deleted": deleted}

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
    init_db()  # 自动初始化数据库表结构，已存在则不会重复创建
    uvicorn.run(app, host="0.0.0.0", port=8000) 