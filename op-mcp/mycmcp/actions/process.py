from fastmcp.actions import BaseAction
import subprocess
from mycmcp.cmdb import crud, models
from datetime import datetime

class ProcessAction(BaseAction):
    name = "process"
    description = "进程管理"

    async def handle(self, intent):
        op = intent.data.get("op")  # list/kill
        pid = intent.data.get("pid")
        operator = intent.data.get("operator", "system")
        if op == "list":
            cmd = "ps aux"
        elif op == "kill" and pid:
            cmd = f"kill {pid}"
        else:
            return {"error": "参数错误，op必须为list或kill，kill时需提供pid"}
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
            action="process",
            detail=f"cmd: {cmd}, result: {output}",
            operator=operator,
            created_at=datetime.utcnow()
        )
        crud.create_operation_log(log)
        return output 