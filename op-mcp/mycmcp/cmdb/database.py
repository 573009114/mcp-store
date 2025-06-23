from sqlmodel import SQLModel, create_engine, Session
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'db')
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'cmdb.db')}"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from .models import Host, Service, Account, OperationLog
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

init_db()  # 必须在全局作用域，保证无论如何都执行 