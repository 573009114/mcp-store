"""
FastMCP服务器配置

功能描述：
配置和启动FastMCP服务器，注册各种系统管理Action。
提供统一的MCP接口，支持Shell命令执行、服务管理、日志查看、进程管理和系统信息查询等功能。

注册的Action：
- ShellAction: 执行任意Shell命令
- SystemdAction: 管理系统服务（启动、停止、重启等）
- LogAction: 查看日志文件内容
- ProcessAction: 管理进程（查看、终止等）
- SysInfoAction: 查询系统信息（内存、磁盘、负载、网络等）

所有Action都会自动记录操作日志到数据库中，便于审计和追踪。
"""

from fastmcp.server import FastMCPServer
from mycmcp.actions.shell import ShellAction
from mycmcp.actions.systemd import SystemdAction
from mycmcp.actions.logs import LogAction
from mycmcp.actions.process import ProcessAction
from mycmcp.actions.sysinfo import SysInfoAction

app = FastMCPServer()

app.register_action(ShellAction())
app.register_action(SystemdAction())
app.register_action(LogAction())
app.register_action(ProcessAction())
app.register_action(SysInfoAction()) 