# Minio MCP Server

本项目基于 [fastmcp](https://github.com/fastmcp/fastmcp) 框架，封装了 Minio 的常用管理操作，支持通过 MCP 工具自动发现和调用，适用于自动化、平台集成、低代码等场景。

---

## 目录结构

```
minio-mcp/
  ├── main.py           # 主程序，包含所有工具接口
  ├── requirements.txt  # 依赖包列表
  ├── Dockerfile        # Docker 构建文件
  ├── deploy.sh         # 本地/容器一键部署脚本
  └── README.md         # 项目说明文档
```

---

## 功能特性
- Bucket 管理（创建、删除、列举）
- 文件管理（上传本地文件、内容直传、下载、删除、列举）
- 文件分享（生成临时分享链接）
- 权限管理（查询/设置 bucket 策略）
- SSE 流式接口，适配 mcp tools
- 全部接口均带有详细日志

---

## 依赖安装

### 1. pip 安装
```bash
pip install -r requirements.txt
```

### 2. requirements.txt 主要依赖
- fastapi / starlette
- uvicorn
- minio
- fastmcp>=0.1.0

### 3. Docker 部署
见下方 Docker 部署说明。

---

## 环境变量配置
可通过环境变量灵活配置 Minio 连接信息：
- `MINIO_ENDPOINT`   Minio 服务地址（如 `10.69.77.89:19000`）
- `MINIO_ACCESS_KEY` Minio Access Key
- `MINIO_SECRET_KEY` Minio Secret Key
- `MINIO_SECURE`     是否使用 https（`1`/`true`/`True` 为真，默认否）

如未设置，使用 main.py 中的默认值。

---

## 启动与部署

### 1. 本地运行
```bash
pip install -r requirements.txt
python main.py
# 或
./deploy.sh local
```

### 2. Docker 部署
```bash
./deploy.sh start
# 查看日志
./deploy.sh logs
# 停止并清理
./deploy.sh stop
./deploy.sh rm
```

### 3. 直接用 Docker 命令
```bash
docker build -t minio-mcp .
docker run -d --name minio-mcp -p 8000:8000 minio-mcp
```

---

## 工具接口说明
所有接口均通过 MCP 工具自动注册，支持平台自动发现。

### Bucket 管理
- `create_bucket(bucket_name: str)` 创建 bucket
- `delete_bucket(bucket_name: str)` 删除 bucket
- `list_buckets()` 列举所有 bucket

### 文件管理
- `upload_file(bucket_name: str, object_name: str, file_path: str)` 上传本地文件到指定 bucket
- `upload_content(bucket_name: str, object_name: str, content: str, encoding: str = "utf-8")` 直接上传内容到指定 bucket（推荐智能体/自动化场景）
- `download_file(bucket_name: str, object_name: str, file_path: str)` 下载对象到本地文件
- `delete_file(bucket_name: str, object_name: str)` 删除对象
- `list_files(bucket_name: str, prefix: Optional[str] = None)` 列举 bucket 下所有对象（可选前缀）

### 文件分享
- `share_file(bucket_name: str, object_name: str, expires_seconds: int = 3600)` 生成对象的临时分享链接，expires_seconds 可自定义过期时间（默认1小时）

### 权限管理
- `get_bucket_policy(bucket_name: str)` 查询 bucket 的访问策略
- `set_bucket_policy(bucket_name: str, policy_json: str)` 设置 bucket 的访问策略（policy_json 为 JSON 字符串）

### 资源与提示词
- `minio_resource(bucket: str, object: str)` 资源接口，返回对象路径
- `minio_prompt(bucket: str, object: str)` 提示词接口，返回处理建议

---

## 接口调用 JSON 指令示例

所有接口均可通过如下 JSON 指令格式调用：

```json
{
  "tool": "接口名",
  "args": {
    // 参数名: 参数值
  }
}
```

### 1. Bucket 管理

- 创建 bucket
```json
{
  "tool": "create_bucket",
  "args": {
    "bucket_name": "mybucket"
  }
}
```

- 删除 bucket
```json
{
  "tool": "delete_bucket",
  "args": {
    "bucket_name": "mybucket"
  }
}
```

- 列举所有 bucket
```json
{
  "tool": "list_buckets",
  "args": {}
}
```

### 2. 文件管理

- 上传本地文件
```json
{
  "tool": "upload_file",
  "args": {
    "bucket_name": "mybucket",
    "object_name": "test.txt",
    "file_path": "/tmp/test.txt"
  }
}
```

- 直接上传内容（推荐智能体生成内容场景）
```json
{
  "tool": "upload_content",
  "args": {
    "bucket_name": "mybucket",
    "object_name": "test.txt",
    "content": "hello world",
    "encoding": "utf-8"
  }
}
```

- 下载文件
```json
{
  "tool": "download_file",
  "args": {
    "bucket_name": "mybucket",
    "object_name": "test.txt",
    "file_path": "/tmp/test.txt"
  }
}
```

- 删除对象
```json
{
  "tool": "delete_file",
  "args": {
    "bucket_name": "mybucket",
    "object_name": "test.txt"
  }
}
```

- 列举 bucket 下所有对象（可选前缀）
```json
{
  "tool": "list_files",
  "args": {
    "bucket_name": "mybucket",
    "prefix": "folder/" // 可选
  }
}
```

### 3. 文件分享

- 生成对象的临时分享链接
```json
{
  "tool": "share_file",
  "args": {
    "bucket_name": "mybucket",
    "object_name": "test.txt",
    "expires_seconds": 600
  }
}
```

### 4. 权限管理

- 查询 bucket 策略
```json
{
  "tool": "get_bucket_policy",
  "args": {
    "bucket_name": "mybucket"
  }
}
```

- 设置 bucket 策略
```json
{
  "tool": "set_bucket_policy",
  "args": {
    "bucket_name": "mybucket",
    "policy_json": "{...}" // 传入 JSON 字符串
  }
}
```

### 5. 资源与提示词

- 获取对象资源路径
```json
{
  "tool": "minio_resource",
  "args": {
    "bucket": "mybucket",
    "object": "test.txt"
  }
}
```

- 获取对象处理建议
```json
{
  "tool": "minio_prompt",
  "args": {
    "bucket": "mybucket",
    "object": "test.txt"
  }
}
```

---

## 常见问题

- **依赖报错/模块找不到？**
  - 请确保已正确安装 requirements.txt 里的所有依赖。
  - Docker 部署建议使用国内源，已在 Dockerfile 配置。
- **MinIO 连接失败？**
  - 检查 MINIO_ENDPOINT、MINIO_ACCESS_KEY、MINIO_SECRET_KEY 环境变量。
  - 检查 MinIO 服务是否可达。
- **如何扩展更多接口？**
  - 参考 main.py，新增 @mcp.tool() 装饰器即可自动注册。

---

## 进阶建议
- 支持 base64/二进制内容上传（可扩展 upload_content）
- 增加 API 鉴权、分片上传、单元测试等
- 代码结构可进一步拆分 app.py/tools.py 等

---

如有问题欢迎提 issue 或联系作者。 