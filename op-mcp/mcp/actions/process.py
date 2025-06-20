import psutil

def list_process():
    proc_list = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
        try:
            proc_list.append(p.info)
        except Exception:
            continue
    return {"processes": proc_list}

def kill_process(params):
    pid = params.get("pid")
    if not pid:
        return {"error": "No pid specified"}
    try:
        p = psutil.Process(int(pid))
        p.terminate()
        p.wait(timeout=3)
        return {"status": "killed", "pid": pid}
    except Exception as e:
        return {"error": str(e)} 