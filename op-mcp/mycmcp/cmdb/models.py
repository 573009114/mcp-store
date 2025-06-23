from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Host(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hostname: str
    ip: str
    os: str
    group: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    port: int
    host_id: int
    status: str

class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    host_id: Optional[int] = Field(default=None)
    username: str
    password: Optional[str] = Field(default=None)
    sudo: bool = False
    pubkey: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OperationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    detail: str
    operator: str
    created_at: datetime = Field(default_factory=datetime.utcnow) 