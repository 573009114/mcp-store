# MCP SERVER 运维平台

## 项目简介

本项目旨在打造一个集成多种运维能力的 MCP SERVER 平台，支持多种运维场景的自动化与标准化。平台通过模块化设计，便于扩展和维护，适用于企业级的运维管理需求。

## 主要功能

- **Kubernetes 管理**：支持 K8s 集群的部署、管理与监控。
- **主机管理**：支持主机的远程命令执行、进程管理、日志采集等基础运维操作。
- **自动化运维脚本**：内置多种常用运维脚本，提升运维效率。
- **多环境支持**：支持本地、测试、生产等多种环境的快速切换与部署。
- **可扩展架构**：各模块独立，便于后续功能扩展和定制开发。

## 目录结构

```
mcp-store/
  ├── kubernetes-mcp/    # Kubernetes 相关运维模块
  └── op-mcp/            # 通用主机运维模块
```

- `kubernetes-mcp/`：包含 K8s 相关的配置、客户端、部署脚本及测试用例。
- `op-mcp/`：包含主机运维相关的脚本、服务端实现及数据库模型。

## 快速开始

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd mcp-store
   ```

2. **安装依赖**
   建议使用 Python 3.12 及以上版本，推荐使用虚拟环境。
   ```bash
   cd kubernetes-mcp
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   参考 `env.example` 文件，配置相关环境变量。

4. **运行示例**
   ```bash
   python examples/example_usage.py
   ```

5. **测试**
   ```bash
   pytest
   ```

## 适用场景

- 企业级多集群、多主机的统一运维管理
- 自动化运维脚本的集中管理与调度
- 运维流程的标准化与自动化

## 贡献指南

欢迎提交 Issue 和 PR，完善平台功能。请遵循项目的代码规范和提交规范。

## 许可证

本项目采用 MIT 许可证，详情请见 LICENSE 文件。 