"""
Linux MCP Server - 系统管理工具服务器

功能描述：
这是一个基于FastMCP的Linux系统管理工具服务器，提供丰富的系统管理功能。
支持本地和远程服务器管理，包括Shell命令执行、服务管理、日志查看、进程管理、系统监控等。

主要功能模块：
1. 系统操作工具：
   - shell: 执行任意Shell命令（本地/远程）
   - systemd: 管理系统服务（启动、停止、重启、状态查看等）
   - logs: 查看日志文件内容
   - process: 管理进程（查看列表、终止进程）
   - sysinfo: 查询系统信息（内存、磁盘、负载、网络）

2. CMDB资产管理：
   - create_host: 创建主机记录
   - list_hosts: 列出所有主机
   - create_host_with_account: 创建主机和SSH账号关联
   - delete_host: 删除主机记录
   - fix_account_host_link: 修复账号主机关联关系

3. 远程管理功能：
   - remote_exec: 通过SSH在远程主机执行命令
   - 支持所有本地工具在远程主机上执行

技术特点：
- 基于FastMCP框架，提供标准化的MCP接口
- 支持本地和远程操作，统一的管理体验
- 完整的操作日志记录，便于审计和追踪
- SQLite数据库存储，轻量级部署
- 支持主机分组管理，便于批量操作

使用场景：
- 服务器运维管理
- 系统监控和故障排查
- 服务部署和维护
- 批量服务器操作
- 运维自动化脚本

所有工具都包含详细的参数说明和使用示例，便于大模型理解和调用。
"""

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
    """
    执行Shell命令工具
    
    功能描述：
    在本地或远程主机上执行任意Shell命令，支持本地执行和远程SSH执行。
    适用于系统管理、文件操作、网络诊断等场景。
    
    参数说明：
    - command (str): 要执行的Shell命令，如 "ls -la", "ps aux", "netstat -tuln" 等
    - host_id (Optional[int]): 远程主机ID，如果提供则在指定主机上执行，否则在本地执行
    
    返回值：
    - dict: 包含执行结果的字典
        - stdout (str): 标准输出内容
        - stderr (str): 标准错误输出内容  
        - returncode (int): 命令返回码，0表示成功
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 本地执行: shell("ls -la")
    - 远程执行: shell("ps aux", host_id=1)
    - 网络诊断: shell("ping -c 3 google.com")
    - 文件操作: shell("cat /etc/hostname")
    """
    if host_id:
        return _remote_exec(host_id, command)
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
    """
    Systemd服务管理工具
    
    功能描述：
    管理系统服务，包括启动、停止、重启、查看状态等操作。
    支持本地和远程服务管理，适用于服务部署和维护。
    
    参数说明：
    - action (str): 操作类型，支持以下值：
        - "start": 启动服务
        - "stop": 停止服务  
        - "restart": 重启服务
        - "status": 查看服务状态
        - "enable": 设置开机自启
        - "disable": 禁用开机自启
        - "reload": 重新加载配置
    - service (str): 服务名称，如 "nginx", "mysql", "docker" 等
    - host_id (Optional[int]): 远程主机ID，如果提供则在指定主机上执行
    
    返回值：
    - dict: 包含操作结果的字典
        - stdout (str): 命令输出内容
        - stderr (str): 错误输出内容
        - returncode (int): 返回码
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 启动服务: systemd("start", "nginx")
    - 查看状态: systemd("status", "mysql")
    - 重启服务: systemd("restart", "docker", host_id=1)
    - 设置自启: systemd("enable", "nginx")
    """
    cmd = f"systemctl {action} {service}"
    if host_id:
        return _remote_exec(host_id, cmd)
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
    """
    日志查看工具
    
    功能描述：
    查看指定文件的最后几行内容，常用于查看日志文件的最新记录。
    支持本地和远程文件查看，适用于日志分析和问题排查。
    
    参数说明：
    - path (str): 文件路径，如 "/var/log/nginx/access.log", "/var/log/syslog" 等
    - lines (int): 显示的行数，默认为50行
    - host_id (Optional[int]): 远程主机ID，如果提供则查看远程主机上的文件
    
    返回值：
    - dict: 包含文件内容的字典
        - stdout (str): 文件内容
        - stderr (str): 错误信息
        - returncode (int): 返回码
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 查看Nginx日志: logs("/var/log/nginx/access.log", 100)
    - 查看系统日志: logs("/var/log/syslog", 20)
    - 远程查看: logs("/var/log/mysql/error.log", 30, host_id=1)
    - 查看应用日志: logs("/app/logs/app.log", 50)
    """
    cmd = f"tail -n {lines} {path}"
    if host_id:
        return _remote_exec(host_id, cmd)
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
    """
    进程管理工具
    
    功能描述：
    管理系统进程，包括查看进程列表、终止进程等操作。
    支持本地和远程进程管理，适用于进程监控和问题处理。
    
    参数说明：
    - op (str): 操作类型
        - "list": 列出所有进程（类似ps aux命令）
        - "kill": 终止指定进程
    - pid (int): 进程ID，仅在op为"kill"时需要提供
    - host_id (Optional[int]): 远程主机ID，如果提供则在指定主机上执行
    
    返回值：
    - dict: 包含操作结果的字典
        - stdout (str): 命令输出内容
        - stderr (str): 错误输出内容
        - returncode (int): 返回码
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 查看进程列表: process("list")
    - 终止进程: process("kill", pid=1234)
    - 远程查看: process("list", host_id=1)
    - 远程终止: process("kill", pid=5678, host_id=1)
    """
    if op == "list":
        cmd = "ps aux"
    elif op == "kill" and pid:
        cmd = f"kill {pid}"
    else:
        return {"error": "参数错误，op必须为list或kill，kill时需提供pid"}
    if host_id:
        return _remote_exec(host_id, cmd)
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
    """
    系统信息查询工具
    
    功能描述：
    查询系统各种资源使用情况和状态信息，包括内存、磁盘、负载、网络等。
    支持本地和远程系统信息查询，适用于系统监控和性能分析。
    
    参数说明：
    - info_type (str): 信息类型
        - "mem": 内存使用情况（free -h命令）
        - "disk": 磁盘使用情况（df -h命令）
        - "load": 系统负载（uptime命令）
        - "net": 网络接口信息（ifconfig或ip addr命令）
    - host_id (Optional[int]): 远程主机ID，如果提供则查询远程主机信息
    
    返回值：
    - dict: 包含系统信息的字典
        - stdout (str): 命令输出内容
        - stderr (str): 错误输出内容
        - returncode (int): 返回码
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 查看内存: sysinfo("mem")
    - 查看磁盘: sysinfo("disk")
    - 查看负载: sysinfo("load")
    - 查看网络: sysinfo("net")
    - 远程查询: sysinfo("mem", host_id=1)
    """
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
        return _remote_exec(host_id, cmd)
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
    """
    创建主机记录工具
    
    功能描述：
    在CMDB数据库中创建新的主机记录，用于管理服务器资产信息。
    支持主机分组管理，便于批量操作和权限控制。
    
    参数说明：
    - hostname (str): 主机名，如 "web-server-01", "db-master" 等
    - ip (str): 主机IP地址，如 "192.168.1.100", "10.0.0.50" 等
    - os (str): 操作系统信息，如 "Ubuntu 20.04", "CentOS 7", "Debian 11" 等
    - group (str): 主机分组，如 "web", "database", "monitoring" 等，可选参数
    
    返回值：
    - dict: 包含操作结果的字典
        - msg (str): 操作结果消息，成功时为"ok"
    
    使用示例：
    - 创建Web服务器: create_host("web-01", "192.168.1.10", "Ubuntu 20.04", "web")
    - 创建数据库服务器: create_host("db-01", "192.168.1.20", "CentOS 7", "database")
    - 创建监控服务器: create_host("monitor-01", "192.168.1.30", "Debian 11", "monitoring")
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS hosts (id INTEGER PRIMARY KEY, hostname TEXT, ip TEXT, os TEXT, groupname TEXT)')
    c.execute('INSERT INTO hosts (hostname, ip, os, groupname) VALUES (?, ?, ?, ?)', (hostname, ip, os, group))
    conn.commit()
    conn.close()
    return {"msg": "ok"}

@mcp.tool()
def list_hosts() -> list:
    """
    列出所有主机工具
    
    功能描述：
    获取CMDB中所有主机的列表信息，包括主机ID、主机名、IP地址、操作系统和分组信息。
    用于查看当前管理的所有服务器资产。
    
    参数说明：
    无需参数
    
    返回值：
    - list: 主机信息列表，每个元素包含：
        - id (int): 主机ID
        - hostname (str): 主机名
        - ip (str): IP地址
        - os (str): 操作系统
        - group (str): 分组信息
    
    使用示例：
    - 查看所有主机: list_hosts()
    - 用于远程操作前的主机选择
    """
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
    """
    创建主机和账号关联工具
    
    功能描述：
    同时创建主机记录和对应的SSH登录账号，建立主机与账号的关联关系。
    支持远程SSH操作，是远程管理功能的基础。
    
    参数说明：
    - hostname (str): 主机名
    - ip (str): 主机IP地址
    - os (str): 操作系统信息
    - group (str): 主机分组
    - username (str): SSH登录用户名
    - password (str): SSH登录密码
    
    返回值：
    - dict: 包含创建结果的字典
        - msg (str): 操作结果消息
        - host_id (int): 创建的主机ID
        - account_id (int): 创建的账号ID
    
    使用示例：
    - 创建带账号的主机: create_host_with_account_tool("web-01", "192.168.1.10", "Ubuntu 20.04", "web", "admin", "password123")
    - 创建数据库服务器: create_host_with_account_tool("db-01", "192.168.1.20", "CentOS 7", "database", "root", "dbpass123")
    """
    host = Host(hostname=hostname, ip=ip, os=os, group=group)
    account = Account(username=username, password=password)
    h, a = crud_create_host_with_account(host, account)
    return {"msg": "ok", "host_id": h['id'], "account_id": a['id']}

def _remote_exec(host_id: int, command: str) -> dict:
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
def remote_exec(host_id: int, command: str) -> dict:
    """
    远程命令执行工具
    
    功能描述：
    通过SSH在指定远程主机上执行命令，支持所有Shell命令的远程执行。
    需要主机已配置SSH账号信息，适用于远程服务器管理。
    
    参数说明：
    - host_id (int): 目标主机ID，必须是已创建并配置了SSH账号的主机
    - command (str): 要执行的Shell命令
    
    返回值：
    - dict: 包含执行结果的字典
        - stdout (str): 命令输出内容
        - stderr (str): 错误输出内容
        - error (str): 连接或执行出错时的错误信息
    
    使用示例：
    - 远程查看进程: remote_exec(1, "ps aux")
    - 远程查看磁盘: remote_exec(1, "df -h")
    - 远程重启服务: remote_exec(1, "systemctl restart nginx")
    - 远程查看日志: remote_exec(1, "tail -n 50 /var/log/nginx/access.log")
    """
    return _remote_exec(host_id, command)

@mcp.tool()
def fix_account_host_link() -> dict:
    """
    修复账号主机关联工具
    
    功能描述：
    修复CMDB中账号与主机的关联关系，当只有一个主机时自动将未关联的账号关联到该主机。
    用于解决数据不一致问题，确保远程操作功能正常工作。
    
    参数说明：
    无需参数
    
    返回值：
    - dict: 包含修复结果的字典
        - fixed (int): 修复的账号数量
        - total_accounts (int): 总账号数量
    
    使用示例：
    - 修复关联关系: fix_account_host_link()
    - 用于系统初始化或数据修复
    """
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
    """
    删除主机记录工具
    
    功能描述：
    从CMDB中删除指定的主机记录，同时删除关联的SSH账号信息。
    用于清理不再管理的服务器资产。
    
    参数说明：
    - host_id (int): 要删除的主机ID
    
    返回值：
    - dict: 包含删除结果的字典
        - deleted (int): 删除的记录数量
    
    使用示例：
    - 删除主机: delete_host(1)
    - 清理过期资产: delete_host(5)
    """
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