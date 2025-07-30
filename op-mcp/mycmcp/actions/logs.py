from fastmcp.actions import BaseAction
import subprocess
from mycmcp.cmdb import crud, models
from datetime import datetime

class LogAction(BaseAction):
    """
    日志查看Action
    
    功能描述：
    查看指定文件的最后几行内容，常用于查看日志文件的最新记录。
    所有日志查看操作都会被记录到数据库中，适用于日志分析和问题排查。
    
    参数说明：
    - path (str): 文件路径，如 "/var/log/nginx/access.log", "/var/log/syslog" 等
    - lines (int): 显示的行数，默认为50行
    - operator (str): 操作者标识，默认为 "system"
    
    返回值：
    - dict: 包含文件内容的字典
        - stdout (str): 文件内容
        - stderr (str): 错误信息
        - returncode (int): 返回码
        - error (str): 执行出错时的错误信息
    
    使用示例：
    - 查看Nginx日志: {"path": "/var/log/nginx/access.log", "lines": 100, "operator": "admin"}
    - 查看系统日志: {"path": "/var/log/syslog", "lines": 20, "operator": "monitor"}
    - 查看应用日志: {"path": "/app/logs/app.log", "lines": 50, "operator": "developer"}
    - 查看错误日志: {"path": "/var/log/mysql/error.log", "lines": 30, "operator": "dba"}
    """
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