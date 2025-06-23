from fastmcp.actions import BaseAction
import subprocess
from mycmcp.cmdb import crud, models
from datetime import datetime

class LogAction(BaseAction):
    name = "logs"
    description = "日志片段拉取"

    async def handle(self, intent):
        path = intent.data.get("path")
        lines = intent.data.get("lines", 50)
        operator = intent.data.get("operator", "system")
        if not path:
            return {"error": "path参数必填"}
        cmd = f"tail -n {lines} {path}"
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
            action="logs",
            detail=f"cmd: {cmd}, result: {output}",
            operator=operator,
            created_at=datetime.utcnow()
        )
        crud.create_operation_log(log)
        return output 