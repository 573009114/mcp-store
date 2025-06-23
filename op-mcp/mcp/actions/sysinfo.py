from fastmcp.actions import BaseAction
import subprocess
from mcp.cmdb import crud, models
from datetime import datetime

class SysInfoAction(BaseAction):
    name = "sysinfo"
    description = "系统信息查询"

    async def handle(self, intent):
        info_type = intent.data.get("type")  # mem/disk/load/net
        operator = intent.data.get("operator", "system")
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
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            output = {"error": str(e)}
        log = models.OperationLog(
            action="sysinfo",
            detail=f"cmd: {cmd}, result: {output}",
            operator=operator,
            created_at=datetime.utcnow()
        )
        crud.create_operation_log(log)
        return output 