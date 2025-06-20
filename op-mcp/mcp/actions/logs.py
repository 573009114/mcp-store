import asyncio
import os

async def get_logs(params):
    path = params.get("path")
    lines = params.get("lines", 100)
    if not path or not os.path.isfile(path):
        yield {"error": "Invalid log file path"}
        return
    # 读取最后 N 行
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        block = 1024
        data = b""
        while filesize > 0 and lines > 0:
            read_size = min(block, filesize)
            f.seek(filesize - read_size)
            data = f.read(read_size) + data
            filesize -= read_size
            lines_found = data.count(b"\n")
            if lines_found >= lines:
                break
        log_lines = data.split(b"\n")[-lines:]
        for l in log_lines:
            yield {"log": l.decode(errors="ignore")}
    yield {"status": "done"} 