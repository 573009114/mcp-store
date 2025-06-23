from fastmcp.actions import BaseAction
import subprocess
from mcp.cmdb import crud, models
from datetime import datetime

class ShellAction(BaseAction):
    name = "shell"
    description = "执行任意shell命令"

    async def handle(self, intent):
        command = intent.data.get("command")
        operator = intent.data.get("operator", "system")
        if not command:
            return {"error": "No command provided"}
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            output = {"error": str(e)}
        # 记录操作日志
        log = models.OperationLog(
            action="shell",
            detail=f"command: {command}, result: {output}",
            operator=operator,
            created_at=datetime.utcnow()
        )
        crud.create_operation_log(log)
        return output 