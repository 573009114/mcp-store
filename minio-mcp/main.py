import os
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
from minio import Minio
from minio.error import S3Error
from typing import Optional
from datetime import timedelta
import json
import logging
from functools import wraps
from datetime import datetime

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger("minio-mcp")

# 通用日志装饰器
def log_entry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"调用: {func.__name__} args={args} kwargs={kwargs}")
        return func(*args, **kwargs)
    return wrapper

# ------------------ 配置与客户端初始化 ------------------
# 支持环境变量优先，未设置则用默认
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "10.69.77.89:19000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "MINIO")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "MINIO123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "0") in ("1", "true", "True")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# ------------------ MCP 服务器实例 ------------------
mcp = FastMCP("MinioMCP")

# ------------------ Bucket 管理工具 ------------------
@mcp.tool()
@log_entry
def create_bucket(bucket_name: str) -> str:
    """创建 bucket"""
    if not bucket_name:
        return "Error: bucket_name 不能为空"
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            return f"Bucket '{bucket_name}' created."
        else:
            return f"Bucket '{bucket_name}' already exists."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
@log_entry
def delete_bucket(bucket_name: str) -> str:
    """删除 bucket"""
    if not bucket_name:
        return "Error: bucket_name 不能为空"
    try:
        minio_client.remove_bucket(bucket_name)
        return f"Bucket '{bucket_name}' deleted."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
@log_entry
def list_buckets() -> str:
    """列举所有 bucket"""
    try:
        buckets = minio_client.list_buckets()
        return "\n".join([bucket.name for bucket in buckets])
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------ 文件管理工具 ------------------
@mcp.tool()
@log_entry
def upload_file(bucket_name: str, object_name: str, file_path: str) -> str:
    """上传本地文件到指定 bucket"""
    if not (bucket_name and object_name and file_path):
        return "Error: bucket_name/object_name/file_path 不能为空"
    if not os.path.isfile(file_path):
        return f"Error: File '{file_path}' does not exist."
    try:
        minio_client.fput_object(bucket_name, object_name, file_path)
        return f"File '{file_path}' uploaded to '{bucket_name}/{object_name}'."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
@log_entry
def download_file(bucket_name: str, object_name: str, file_path: str) -> str:
    """从指定 bucket 下载对象到本地文件"""
    if not (bucket_name and object_name and file_path):
        return "Error: bucket_name/object_name/file_path 不能为空"
    try:
        minio_client.fget_object(bucket_name, object_name, file_path)
        return f"Object '{bucket_name}/{object_name}' downloaded to '{file_path}'."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
@log_entry
def delete_file(bucket_name: str, object_name: str) -> str:
    """删除指定 bucket 的对象"""
    if not (bucket_name and object_name):
        return "Error: bucket_name/object_name 不能为空"
    try:
        minio_client.remove_object(bucket_name, object_name)
        return f"Object '{bucket_name}/{object_name}' deleted."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
@log_entry
def list_files(bucket_name: str, prefix: Optional[str] = None) -> str:
    """列举 bucket 下所有对象（可选前缀）"""
    if not bucket_name:
        return "Error: bucket_name 不能为空"
    try:
        objects = minio_client.list_objects(bucket_name, prefix=prefix or "", recursive=True)
        return "\n".join([obj.object_name for obj in objects])
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------ 文件分享工具 ------------------
@mcp.tool()
@log_entry
def share_file(bucket_name: str, object_name: str, expires_seconds: int = 3600) -> str:
    """生成对象的临时分享链接，expires_seconds 为过期秒数（默认1小时）"""
    if not (bucket_name and object_name):
        return "Error: bucket_name/object_name 不能为空"
    if not isinstance(expires_seconds, int) or expires_seconds <= 0:
        return "Error: expires_seconds 必须为正整数"
    try:
        url = minio_client.presigned_get_object(
            bucket_name,
            object_name,
            expires=timedelta(seconds=expires_seconds)
        )
        return url
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------ 权限管理工具 ------------------
@mcp.tool()
@log_entry
def get_bucket_policy(bucket_name: str) -> str:
    """查询 bucket 的访问策略"""
    if not bucket_name:
        return "Error: bucket_name 不能为空"
    try:
        policy = minio_client.get_bucket_policy(bucket_name)
        return policy
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
@log_entry
def set_bucket_policy(bucket_name: str, policy_json: str) -> str:
    """设置 bucket 的访问策略，policy_json 为 JSON 字符串"""
    if not (bucket_name and policy_json):
        return "Error: bucket_name/policy_json 不能为空"
    try:
        # 校验 policy_json 是否为合法 JSON
        json.loads(policy_json)
        minio_client.set_bucket_policy(bucket_name, policy_json)
        return f"Policy set for bucket '{bucket_name}'."
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------ 资源与提示词 ------------------
@mcp.resource("minio://{bucket}/{object}")
@log_entry
def minio_resource(bucket: str, object: str) -> str:
    return f"Resource minio: {bucket}/{object}"

@mcp.prompt()
@log_entry
def minio_prompt(bucket: str, object: str) -> str:
    return f"Please process minio object: {bucket}/{object}"

# ------------------ SSE 服务挂载 ------------------
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 