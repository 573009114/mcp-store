from fastmcp.actions import BaseAction
import subprocess
from mycmcp.cmdb import crud, models
from datetime import datetime

class SysInfoAction(BaseAction):
    """
    系统信息查询Action
    
    功能描述：
    查询系统各种资源使用情况和状态信息，包括内存、磁盘、负载、网络等。
    所有查询操作都会被记录到数据库中，便于系统监控和性能分析。
    
    参数说明：
    - type (str): 信息类型，支持以下值：
        - "mem": 内存使用情况（free -h命令）
        - "disk": 磁盘使用情况（df -h命令）
        - "load": 系统负载（uptime命令）
        - "net": 网络接口信息（ifconfig或ip addr命令）
    - operator (str): 操作者标识，默认为 "system"
    
    返回值：
    - dict: 包含系统信息的字典
        - stdout (str): 命令输出内容
        - stderr (str): 错误输出内容
        - returncode (int): 返回码
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 查看内存: {"type": "mem", "operator": "monitor"}
    - 查看磁盘: {"type": "disk", "operator": "admin"}
    - 查看负载: {"type": "load", "operator": "system"}
    - 查看网络: {"type": "net", "operator": "network"}
    """
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