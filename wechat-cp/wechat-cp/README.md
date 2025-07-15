# 微信工作平台 MCP Server

基于 fastmcp 框架，支持文章的发布、删除、查询、编辑等功能，数据库为 SQLite。

## 依赖安装

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
cd wechat-cp
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 主要功能
- 发布文章
- 删除文章
- 文章列表
- 文章详情
- 编辑文章

所有接口均通过 fastmcp 的 app.tools() 暴露，支持 mcp 工具自动发现。 