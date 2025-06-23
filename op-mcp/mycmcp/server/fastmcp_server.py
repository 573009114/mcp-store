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