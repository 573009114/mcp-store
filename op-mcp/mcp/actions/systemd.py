from fastmcp.actions import BaseAction
import subprocess
from mcp.cmdb import crud, models
from datetime import datetime

class SystemdAction(BaseAction):
    name = "systemd"
    description = "systemd服务管理"

    async def handle(self, intent):
        action = intent.data.get("action")  # start/stop/restart/status
        service = intent.data.get("service")
        operator = intent.data.get("operator", "system")
        if not action or not service:
            return {"error": "action和service参数必填"}
        cmd = f"systemctl {action} {service}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            output = {"error": str(e)}
        log = models.OperationLog(
            action="systemd",
            detail=f"cmd: {cmd}, result: {output}",
            operator=operator,
            created_at=datetime.utcnow()
        )
        crud.create_operation_log(log)
        return output 