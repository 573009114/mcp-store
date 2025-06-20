from mcp.store import store
from mcp.actions import shell

async def register_node(params):
    ip = params.get("ip")
    hostname = params.get("hostname")
    group = params.get("group")
    if not ip or not hostname:
        return {"error": "ip 和 hostname 必填"}
    return store.register_node(ip, hostname, group)

def list_nodes():
    return {"nodes": store.list_nodes()}

async def exec_on_node(params):
    ip = params.get("ip")
    cmd = params.get("cmd")
    node = store.get_node(ip)
    if not node:
        yield {"error": "节点不存在"}
        return
    # 本地执行（如需远程，需扩展）
    async for event in shell.run_shell({"cmd": cmd}):
        yield event 