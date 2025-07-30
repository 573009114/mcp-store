from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Host(SQLModel, table=True):
    """
    主机信息模型
    
    功能描述：
    存储服务器主机的基本信息，包括主机名、IP地址、操作系统和分组信息。
    用于CMDB资产管理，支持主机分组管理和远程操作。
    
    字段说明：
    - id (int): 主机唯一标识符，主键，自动生成
    - hostname (str): 主机名，如 "web-server-01", "db-master" 等
    - ip (str): 主机IP地址，如 "192.168.1.100", "10.0.0.50" 等
    - os (str): 操作系统信息，如 "Ubuntu 20.04", "CentOS 7", "Debian 11" 等
    - group (str): 主机分组，如 "web", "database", "monitoring" 等，可选字段
    - created_at (datetime): 记录创建时间，自动生成
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    hostname: str
    ip: str
    os: str
    group: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Service(SQLModel, table=True):
    """
    服务信息模型
    
    功能描述：
    存储主机上运行的服务信息，包括服务名称、端口、状态等。
    用于服务监控和管理，支持服务状态跟踪。
    
    字段说明：
    - id (int): 服务唯一标识符，主键，自动生成
    - name (str): 服务名称，如 "nginx", "mysql", "redis" 等
    - port (int): 服务端口号，如 80, 3306, 6379 等
    - host_id (int): 关联的主机ID，外键
    - status (str): 服务状态，如 "running", "stopped", "error" 等
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    port: int
    host_id: int
    status: str

class Account(SQLModel, table=True):
    """
    账号信息模型
    
    功能描述：
    存储SSH登录账号信息，用于远程主机连接和操作。
    支持密码和公钥两种认证方式，关联到具体主机。
    
    字段说明：
    - id (int): 账号唯一标识符，主键，自动生成
    - host_id (int): 关联的主机ID，外键，可选字段
    - username (str): SSH登录用户名，如 "root", "admin", "ubuntu" 等
    - password (str): SSH登录密码，可选字段，与公钥认证二选一
    - sudo (bool): 是否具有sudo权限，默认为False
    - pubkey (str): SSH公钥内容，可选字段，与密码认证二选一
    - created_at (datetime): 记录创建时间，自动生成
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    host_id: Optional[int] = Field(default=None)
    username: str
    password: Optional[str] = Field(default=None)
    sudo: bool = False
    pubkey: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OperationLog(SQLModel, table=True):
    """
    操作日志模型
    
    功能描述：
    记录所有系统操作的日志信息，包括操作类型、详细信息、操作者等。
    用于审计追踪、问题排查和操作历史记录。
    
    字段说明：
    - id (int): 日志唯一标识符，主键，自动生成
    - action (str): 操作类型，如 "shell", "systemd", "logs", "process", "sysinfo" 等
    - detail (str): 操作详细信息，包含命令、参数、结果等
    - operator (str): 操作者标识，如 "admin", "system", "monitor" 等
    - created_at (datetime): 操作时间，自动生成
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    detail: str
    operator: str
    created_at: datetime = Field(default_factory=datetime.utcnow) 