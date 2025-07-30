"""
CMDB数据库配置模块

功能描述：
配置和管理CMDB系统的SQLite数据库，包括数据库连接、表结构初始化和会话管理。
基于SQLModel ORM框架，提供统一的数据库访问接口。

主要功能：
- 数据库连接配置：SQLite数据库文件路径和连接设置
- 表结构初始化：自动创建Host、Service、Account、OperationLog等表
- 会话管理：提供数据库会话获取接口
- 自动初始化：模块导入时自动执行数据库初始化

数据库文件位置：项目根目录下的db/cmdb.db
"""

from sqlmodel import SQLModel, create_engine, Session
import os

# 数据库文件目录配置
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'db')
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'cmdb.db')}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """
    初始化数据库表结构
    
    功能描述：
    创建所有数据模型对应的数据库表，包括Host、Service、Account、OperationLog等。
    如果表已存在则不会重复创建，支持增量更新。
    
    参数说明：
    无需参数
    
    返回值：
    无返回值
    
    使用说明：
    通常在应用启动时调用，确保数据库表结构正确创建。
    """
    from .models import Host, Service, Account, OperationLog
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    获取数据库会话
    
    功能描述：
    创建并返回一个新的数据库会话，用于执行数据库操作。
    支持上下文管理器模式，自动处理事务提交和回滚。
    
    参数说明：
    无需参数
    
    返回值：
    - Session: SQLModel数据库会话对象
    
    使用示例：
    ```python
    with get_session() as session:
        # 执行数据库操作
        session.add(host)
        session.commit()
    ```
    """
    return Session(engine)

# 模块导入时自动初始化数据库
init_db()  # 必须在全局作用域，保证无论如何都执行 