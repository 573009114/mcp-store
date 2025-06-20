#!/usr/bin/env python3
"""
Kubernetes MCP服务器主入口
"""
import asyncio
import sys
import os
import subprocess
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from mcp_server import main as mcp_main
from config import config


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Kubernetes MCP Server                     ║
║                                                              ║
║  基于Model Context Protocol的Kubernetes集群管理服务器        ║
║                                                              ║
║  功能特性:                                                   ║
║  • 获取集群信息                                              ║
║  • 管理Pod、Service、Deployment                              ║
║  • 执行kubectl命令                                           ║
║  • 获取资源日志                                              ║
║  • 实时监控集群状态                                          ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_config():
    """打印配置信息"""
    print("📋 配置信息:")
    print(f"   Kubernetes配置路径: {config.k8s.kubeconfig_path or '自动检测'}")
    print(f"   Kubernetes上下文: {config.k8s.context or '默认'}")
    print(f"   默认命名空间: {config.k8s.namespace}")
    print(f"   MCP服务器地址: {config.mcp.host}:{config.mcp.port}")
    print(f"   调试模式: {'开启' if config.mcp.debug else '关闭'}")
    print()


def check_kubectl():
    """检查kubectl是否可用"""
    try:
        result = subprocess.run(
            ["kubectl", "version", "--client"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


async def main():
    """主函数"""
    try:
        print_banner()
        print_config()
        
        # 检查Kubernetes配置
        if not config.k8s.kubeconfig_path:
            print("⚠️  警告: 未找到kubeconfig文件，将尝试使用集群内配置")
            print("   请确保:")
            print("   1. 已安装kubectl并配置了kubeconfig")
            print("   2. 或者在Kubernetes集群内运行")
            print()
        
        # 检查kubectl是否可用
        if not check_kubectl():
            print("⚠️  警告: kubectl命令不可用")
            print("   请安装kubectl: https://kubernetes.io/docs/tasks/tools/")
            print()
        
        print("🚀 启动Kubernetes MCP服务器...")
        print("   按Ctrl+C停止服务器")
        print()
        
        # 启动MCP服务器
        await mcp_main()
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        if config.mcp.debug:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 
