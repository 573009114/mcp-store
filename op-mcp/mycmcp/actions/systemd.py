from fastmcp.actions import BaseAction
import subprocess
from mycmcp.cmdb import crud, models
from datetime import datetime

class SystemdAction(BaseAction):
    """
    Systemd服务管理Action
    
    功能描述：
    管理系统服务，包括启动、停止、重启、查看状态等操作。
    所有服务管理操作都会被记录到数据库中，便于服务部署和维护。
    
    参数说明：
    - action (str): 操作类型，支持以下值：
        - "start": 启动服务
        - "stop": 停止服务
        - "restart": 重启服务
        - "status": 查看服务状态
        - "enable": 设置开机自启
        - "disable": 禁用开机自启
        - "reload": 重新加载配置
    - service (str): 服务名称，如 "nginx", "mysql", "docker" 等
    - operator (str): 操作者标识，默认为 "system"
    
    返回值：
    - dict: 包含操作结果的字典
        - stdout (str): 命令输出内容
        - stderr (str): 错误输出内容
        - returncode (int): 返回码
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 启动服务: {"action": "start", "service": "nginx", "operator": "admin"}
    - 查看状态: {"action": "status", "service": "mysql", "operator": "monitor"}
    - 重启服务: {"action": "restart", "service": "docker", "operator": "system"}
    - 设置自启: {"action": "enable", "service": "nginx", "operator": "admin"}
    """
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