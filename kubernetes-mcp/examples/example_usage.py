#!/usr/bin/env python3
"""
Kubernetes MCP服务器使用示例
"""
import asyncio
import json
import sys
from pathlib import Path

# 添加父目录到Python路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from k8s_client import KubernetesClient


async def example_usage():
    """使用示例"""
    print("🔧 Kubernetes MCP服务器使用示例")
    print("=" * 50)
    
    # 创建Kubernetes客户端
    client = KubernetesClient()
    
    # 示例1: 获取集群信息
    print("\n1️⃣ 获取集群信息:")
    cluster_info = await client.get_cluster_info()
    print(json.dumps(cluster_info, indent=2, ensure_ascii=False))
    
    # 示例2: 列出Pod
    print("\n2️⃣ 列出Pod:")
    pods = await client.list_pods()
    print(json.dumps(pods, indent=2, ensure_ascii=False))
    
    # 示例3: 列出Service
    print("\n3️⃣ 列出Service:")
    services = await client.list_services()
    print(json.dumps(services, indent=2, ensure_ascii=False))
    
    # 示例4: 列出Deployment
    print("\n4️⃣ 列出Deployment:")
    deployments = await client.list_deployments()
    print(json.dumps(deployments, indent=2, ensure_ascii=False))
    
    # 示例5: 执行kubectl命令
    print("\n5️⃣ 执行kubectl命令 (get nodes):")
    result = await client.execute_kubectl("get nodes")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 示例6: 获取特定命名空间的资源
    print("\n6️⃣ 获取kube-system命名空间的Pod:")
    kube_system_pods = await client.list_pods("kube-system")
    print(json.dumps(kube_system_pods, indent=2, ensure_ascii=False))


async def interactive_example():
    """交互式示例"""
    print("\n🎯 交互式示例")
    print("=" * 50)
    
    client = KubernetesClient()
    
    while True:
        print("\n请选择操作:")
        print("1. 获取集群信息")
        print("2. 列出Pod")
        print("3. 列出Service")
        print("4. 列出Deployment")
        print("5. 执行kubectl命令")
        print("6. 获取Pod日志")
        print("7. 获取资源详情")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-7): ").strip()
        
        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            result = await client.get_cluster_info()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "2":
            namespace = input("请输入命名空间 (回车使用默认): ").strip() or None
            result = await client.list_pods(namespace)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "3":
            namespace = input("请输入命名空间 (回车使用默认): ").strip() or None
            result = await client.list_services(namespace)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "4":
            namespace = input("请输入命名空间 (回车使用默认): ").strip() or None
            result = await client.list_deployments(namespace)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "5":
            command = input("请输入kubectl命令 (不包含kubectl前缀): ").strip()
            result = await client.execute_kubectl(command)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "6":
            pod_name = input("请输入Pod名称: ").strip()
            namespace = input("请输入命名空间 (回车使用默认): ").strip() or None
            tail_lines = input("请输入日志行数 (回车使用100): ").strip()
            tail_lines = int(tail_lines) if tail_lines.isdigit() else 100
            result = await client.get_pod_logs(pod_name, namespace, tail_lines)
            print(result)
        elif choice == "7":
            resource_type = input("请输入资源类型 (pod/service/deployment): ").strip()
            resource_name = input("请输入资源名称: ").strip()
            namespace = input("请输入命名空间 (回车使用默认): ").strip() or None
            result = await client.get_resource_details(resource_type, resource_name, namespace)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ 无效选择，请重试")


async def main():
    """主函数"""
    try:
        # 运行基本示例
        await example_usage()
        
        # 运行交互式示例
        await interactive_example()
        
    except KeyboardInterrupt:
        print("\n👋 示例已停止")
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 