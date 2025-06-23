from .models import Host, Service, Account, OperationLog
from .database import get_session
from sqlmodel import select

def create_host(host: Host):
    with get_session() as session:
        session.add(host)
        session.commit()
        session.refresh(host)
        return host

def get_hosts():
    with get_session() as session:
        return session.exec(select(Host)).all()

def create_service(service: Service):
    with get_session() as session:
        session.add(service)
        session.commit()
        session.refresh(service)
        return service

def get_services():
    with get_session() as session:
        return session.exec(select(Service)).all()

def create_account(account: Account):
    with get_session() as session:
        session.add(account)
        session.commit()
        session.refresh(account)
        return account

def get_accounts():
    with get_session() as session:
        return session.exec(select(Account)).all()

def create_operation_log(log: OperationLog):
    with get_session() as session:
        session.add(log)
        session.commit()
        session.refresh(log)
        return log

def get_operation_logs():
    with get_session() as session:
        return session.exec(select(OperationLog)).all()

def create_host_with_account(host: Host, account: Account):
    with get_session() as session:
        session.add(host)
        session.commit()
        session.refresh(host)
        account.host_id = host.id
        session.add(account)
        session.commit()
        session.refresh(account)
        return {"id": host.id}, {"id": account.id} 