"""
CMDB数据库操作模块

功能描述：
提供CMDB（配置管理数据库）的增删改查操作，包括主机、服务、账号和操作日志的管理。
基于SQLModel ORM框架，支持SQLite数据库操作。

主要功能：
- 主机管理：创建、查询主机信息
- 服务管理：创建、查询服务信息
- 账号管理：创建、查询SSH账号信息
- 日志管理：创建、查询操作日志
- 关联操作：创建主机和账号的关联关系
"""

from .models import Host, Service, Account, OperationLog
from .database import get_session
from sqlmodel import select

def create_host(host: Host):
    """
    创建主机记录
    
    功能描述：
    在数据库中创建新的主机记录，存储主机的基本信息。
    
    参数说明：
    - host (Host): 主机对象，包含hostname、ip、os、group等信息
    
    返回值：
    - Host: 创建成功的主机对象，包含自动生成的ID
    """
    with get_session() as session:
        session.add(host)
        session.commit()
        session.refresh(host)
        return host

def get_hosts():
    """
    获取所有主机列表
    
    功能描述：
    查询数据库中所有的主机记录，用于主机管理和远程操作。
    
    参数说明：
    无需参数
    
    返回值：
    - list[Host]: 所有主机对象的列表
    """
    with get_session() as session:
        return session.exec(select(Host)).all()

def create_service(service: Service):
    """
    创建服务记录
    
    功能描述：
    在数据库中创建新的服务记录，存储服务的基本信息。
    
    参数说明：
    - service (Service): 服务对象，包含name、port、host_id、status等信息
    
    返回值：
    - Service: 创建成功的服务对象，包含自动生成的ID
    """
    with get_session() as session:
        session.add(service)
        session.commit()
        session.refresh(service)
        return service

def get_services():
    """
    获取所有服务列表
    
    功能描述：
    查询数据库中所有的服务记录，用于服务监控和管理。
    
    参数说明：
    无需参数
    
    返回值：
    - list[Service]: 所有服务对象的列表
    """
    with get_session() as session:
        return session.exec(select(Service)).all()

def create_account(account: Account):
    """
    创建账号记录
    
    功能描述：
    在数据库中创建新的SSH账号记录，存储登录认证信息。
    
    参数说明：
    - account (Account): 账号对象，包含username、password、host_id等信息
    
    返回值：
    - Account: 创建成功的账号对象，包含自动生成的ID
    """
    with get_session() as session:
        session.add(account)
        session.commit()
        session.refresh(account)
        return account

def get_accounts():
    """
    获取所有账号列表
    
    功能描述：
    查询数据库中所有的SSH账号记录，用于远程连接管理。
    
    参数说明：
    无需参数
    
    返回值：
    - list[Account]: 所有账号对象的列表
    """
    with get_session() as session:
        return session.exec(select(Account)).all()

def create_operation_log(log: OperationLog):
    """
    创建操作日志记录
    
    功能描述：
    在数据库中创建新的操作日志记录，用于审计和追踪。
    
    参数说明：
    - log (OperationLog): 日志对象，包含action、detail、operator等信息
    
    返回值：
    - OperationLog: 创建成功的日志对象，包含自动生成的ID
    """
    with get_session() as session:
        session.add(log)
        session.commit()
        session.refresh(log)
        return log

def get_operation_logs():
    """
    获取所有操作日志列表
    
    功能描述：
    查询数据库中所有的操作日志记录，用于审计和问题排查。
    
    参数说明：
    无需参数
    
    返回值：
    - list[OperationLog]: 所有日志对象的列表
    """
    with get_session() as session:
        return session.exec(select(OperationLog)).all()

def create_host_with_account(host: Host, account: Account):
    """
    创建主机和账号关联记录
    
    功能描述：
    同时创建主机记录和对应的SSH账号记录，并建立关联关系。
    用于支持远程SSH操作功能。
    
    参数说明：
    - host (Host): 主机对象，包含主机基本信息
    - account (Account): 账号对象，包含SSH登录信息
    
    返回值：
    - tuple: 包含两个字典的元组
        - 第一个字典: 主机信息 {"id": host_id}
        - 第二个字典: 账号信息 {"id": account_id}
    """
    with get_session() as session:
        session.add(host)
        session.commit()
        session.refresh(host)
        account.host_id = host.id
        session.add(account)
        session.commit()
        session.refresh(account)
        return {"id": host.id}, {"id": account.id} 