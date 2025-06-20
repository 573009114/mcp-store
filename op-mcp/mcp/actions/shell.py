import asyncio
import re

# 高危命令正则列表
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",           # rm -rf /
    r":\(\)\{:\|:&\};:",    # fork bomb
    r"shutdown(\s|$)",         # shutdown
    r"reboot(\s|$)",           # reboot
    r"mkfs(\.|\s)",           # mkfs
    r"dd\s+if=",               # dd if=
    r"init\s+0",               # init 0
    r"halt(\s|$)",             # halt
    r"poweroff(\s|$)",         # poweroff
    r"chown\s+-R\s+root\s+/", # chown -R root /
    r"chmod\s+0+\s+/",         # chmod 000 /
]

def is_dangerous(cmd):
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd):
            return True
    return False

async def run_shell(params):
    cmd = params.get("cmd")
    if not cmd:
        yield {"error": "No command specified"}
        return
    if is_dangerous(cmd):
        yield {"error": "检测到高危命令，已阻止执行。"}
        return
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    # 实时读取 stdout
    if proc.stdout:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            yield {"stdout": line.decode().rstrip()}
    # 读取 stderr
    if proc.stderr:
        err = await proc.stderr.read()
        if err:
            yield {"stderr": err.decode().rstrip()}
    await proc.wait()
    yield {"status": "done", "returncode": proc.returncode} 