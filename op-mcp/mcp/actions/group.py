from mcp.store import store
from mcp.actions import shell

async def create_group(params):
    group = params.get("group")
    if not group:
        return {"error": "group 必填"}
    return store.create_group(group)

def list_groups():
    return {"groups": store.list_groups()}

def add_node_to_group(params):
    ip = params.get("ip")
    group = params.get("group")
    if not ip or not group:
        return {"error": "ip 和 group 必填"}
    return store.add_node_to_group(ip, group)

def remove_node_from_group(params):
    ip = params.get("ip")
    group = params.get("group")
    if not ip or not group:
        return {"error": "ip 和 group 必填"}
    return store.remove_node_from_group(ip, group)

async def exec_on_group(params):
    group = params.get("group")
    cmd = params.get("cmd")
    if not group or not cmd:
        yield {"error": "group 和 cmd 必填"}
        return
    nodes = store.get_group_nodes(group)
    if not nodes:
        yield {"error": "分组无节点"}
        return
    for node in nodes:
        yield {"node": node["ip"], "status": "start"}
        async for event in shell.run_shell({"cmd": cmd}):
            yield {"node": node["ip"], **event}
        yield {"node": node["ip"], "status": "done"} 