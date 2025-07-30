from fastmcp.actions import BaseAction
import subprocess
from mycmcp.cmdb import crud, models
from datetime import datetime

class ShellAction(BaseAction):
    """
    Shell命令执行Action
    
    功能描述：
    执行任意Shell命令并记录操作日志，支持系统管理、文件操作、网络诊断等场景。
    所有操作都会被记录到数据库中，便于审计和追踪。
    
    参数说明：
    - command (str): 要执行的Shell命令，如 "ls -la", "ps aux", "netstat -tuln" 等
    - operator (str): 操作者标识，默认为 "system"
    
    返回值：
    - dict: 包含执行结果的字典
        - stdout (str): 标准输出内容
        - stderr (str): 标准错误输出内容
        - returncode (int): 命令返回码，0表示成功
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 查看文件列表: {"command": "ls -la", "operator": "admin"}
    - 查看进程: {"command": "ps aux", "operator": "system"}
    - 网络诊断: {"command": "ping -c 3 google.com", "operator": "user"}
    """
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