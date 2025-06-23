from fastmcp.server import FastMCPServer
from mcp.actions.shell import ShellAction
from mcp.actions.systemd import SystemdAction
from mcp.actions.logs import LogAction
from mcp.actions.process import ProcessAction
from mcp.actions.sysinfo import SysInfoAction

app = FastMCPServer()

app.register_action(ShellAction())
app.register_action(SystemdAction())
app.register_action(LogAction())
app.register_action(ProcessAction())
app.register_action(SysInfoAction()) 