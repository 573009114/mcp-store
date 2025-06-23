from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./cmdb.db"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from .models import Host, Service, Account, OperationLog
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

init_db()  # 必须在全局作用域，保证无论如何都执行 