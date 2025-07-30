from fastmcp.actions import BaseAction
import subprocess
from mycmcp.cmdb import crud, models
from datetime import datetime

class ProcessAction(BaseAction):
    """
    进程管理Action
    
    功能描述：
    管理系统进程，包括查看进程列表、终止进程等操作。
    所有进程管理操作都会被记录到数据库中，适用于进程监控和问题处理。
    
    参数说明：
    - op (str): 操作类型
        - "list": 列出所有进程（类似ps aux命令）
        - "kill": 终止指定进程
    - pid (int): 进程ID，仅在op为"kill"时需要提供
    - operator (str): 操作者标识，默认为 "system"
    
    返回值：
    - dict: 包含操作结果的字典
        - stdout (str): 命令输出内容
        - stderr (str): 错误输出内容
        - returncode (int): 返回码
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 查看进程列表: {"op": "list", "operator": "monitor"}
    - 终止进程: {"op": "kill", "pid": 1234, "operator": "admin"}
    - 查看所有进程: {"op": "list", "operator": "system"}
    - 强制终止进程: {"op": "kill", "pid": 5678, "operator": "admin"}
    """
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