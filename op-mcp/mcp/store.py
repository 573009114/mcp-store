from sqlalchemy import create_engine, Column, String, Table, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
import threading
import os

DB_PATH = os.environ.get("MCP_DB_PATH", "sqlite:///mcp.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# 节点表
class Node(Base):
    __tablename__ = "nodes"
    ip = Column(String, primary_key=True)
    hostname = Column(String)
    group = Column(String, ForeignKey("groups.name"), nullable=True)

# 分组表
class Group(Base):
    __tablename__ = "groups"
    name = Column(String, primary_key=True)
    nodes = relationship("Node", backref="group_ref")

Base.metadata.create_all(engine)

class NodeStore:
    def __init__(self):
        self.lock = threading.Lock()

    def register_node(self, ip, hostname, group=None):
        with self.lock:
            session = SessionLocal()
            try:
                node = session.query(Node).filter_by(ip=ip).first()
                if node:
                    node.hostname = hostname
                    node.group = group
                else:
                    node = Node(ip=ip, hostname=hostname, group=group)
                    session.add(node)
                if group:
                    grp = session.query(Group).filter_by(name=group).first()
                    if not grp:
                        grp = Group(name=group)
                        session.add(grp)
                session.commit()
                return {"ip": ip, "hostname": hostname, "group": group}
            except Exception as e:
                session.rollback()
                return {"error": str(e)}
            finally:
                session.close()

    def list_nodes(self):
        with self.lock:
            session = SessionLocal()
            nodes = session.query(Node).all()
            res = [{"ip": n.ip, "hostname": n.hostname, "group": n.group} for n in nodes]
            session.close()
            return res

    def create_group(self, group):
        with self.lock:
            session = SessionLocal()
            try:
                if not session.query(Group).filter_by(name=group).first():
                    session.add(Group(name=group))
                    session.commit()
                return {"group": group}
            except Exception as e:
                session.rollback()
                return {"error": str(e)}
            finally:
                session.close()

    def list_groups(self):
        with self.lock:
            session = SessionLocal()
            groups = session.query(Group).all()
            res = [{"group": g.name, "nodes": [n.ip for n in g.nodes]} for g in groups]
            session.close()
            return res

    def add_node_to_group(self, ip, group):
        with self.lock:
            session = SessionLocal()
            try:
                node = session.query(Node).filter_by(ip=ip).first()
                if not node:
                    return {"error": "Node not found"}
                grp = session.query(Group).filter_by(name=group).first()
                if not grp:
                    grp = Group(name=group)
                    session.add(grp)
                node.group = group
                session.commit()
                return {"ip": ip, "group": group}
            except Exception as e:
                session.rollback()
                return {"error": str(e)}
            finally:
                session.close()

    def remove_node_from_group(self, ip, group):
        with self.lock:
            session = SessionLocal()
            try:
                node = session.query(Node).filter_by(ip=ip).first()
                if node and node.group == group:
                    node.group = None
                    session.commit()
                return {"ip": ip, "group": group}
            except Exception as e:
                session.rollback()
                return {"error": str(e)}
            finally:
                session.close()

    def get_group_nodes(self, group):
        with self.lock:
            session = SessionLocal()
            nodes = session.query(Node).filter_by(group=group).all()
            res = [{"ip": n.ip, "hostname": n.hostname, "group": n.group} for n in nodes]
            session.close()
            return res

    def get_node(self, ip):
        with self.lock:
            session = SessionLocal()
            node = session.query(Node).filter_by(ip=ip).first()
            res = {"ip": node.ip, "hostname": node.hostname, "group": node.group} if node else None
            session.close()
            return res

store = NodeStore() 