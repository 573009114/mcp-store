#!/usr/bin/env python3
"""
MCP客户端测试脚本
用于测试SSE版本的MCP服务器
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any


class MCPClient:
    """MCP客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        async with self.session.get(f"{self.base_url}/") as response:
            return await response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出工具"""
        async with self.session.post(f"{self.base_url}/mcp/tools/list") as response:
            return await response.json()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用工具"""
        if arguments is None:
            arguments = {}
        
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        
        async with self.session.post(
            f"{self.base_url}/mcp/tools/call",
            json=payload
        ) as response:
            return await response.json()
    
    async def list_resources(self) -> Dict[str, Any]:
        """列出资源"""
        async with self.session.get(f"{self.base_url}/mcp/resources") as response:
            return await response.json()
    
    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """读取资源"""
        async with self.session.get(f"{self.base_url}/mcp/resources/{resource_uri}") as response:
            return await response.json()


async def test_mcp_server():
    """测试MCP服务器"""
    print("🧪 测试Kubernetes MCP SSE服务器...")
    print("=" * 50)
    
    async with MCPClient() as client:
        try:
            # 1. 测试服务器信息
            print("1. 获取服务器信息...")
            info = await client.get_server_info()
            print(f"   服务器: {info['message']} v{info['version']}")
            print(f"   状态: {info['status']}")
            print()
            
            # 2. 健康检查
            print("2. 健康检查...")
            health = await client.health_check()
            print(f"   状态: {health['status']}")
            print()
            
            # 3. 列出工具
            print("3. 列出可用工具...")
            tools = await client.list_tools()
            for tool in tools['tools']:
                print(f"   - {tool['name']}: {tool['description']}")
            print()
            
            # 4. 测试工具调用
            print("4. 测试工具调用...")
            
            # 获取集群信息
            print("   4.1 获取集群信息...")
            cluster_info = await client.call_tool("get_cluster_info")
            if "error" in cluster_info:
                print(f"   ❌ 错误: {cluster_info['error']}")
            else:
                print(f"   ✅ 成功: 集群状态 {cluster_info['result']['status']}")
            
            # 列出Pod
            print("   4.2 列出Pod...")
            pods = await client.call_tool("list_pods", {"namespace": "default"})
            if "error" in pods:
                print(f"   ❌ 错误: {pods['error']}")
            else:
                pod_count = len(pods['result'])
                print(f"   ✅ 成功: 找到 {pod_count} 个Pod")
            
            # 执行kubectl命令
            print("   4.3 执行kubectl命令...")
            kubectl_result = await client.call_tool("execute_kubectl", {"command": "version --client"})
            if "error" in kubectl_result:
                print(f"   ❌ 错误: {kubectl_result['error']}")
            else:
                print(f"   ✅ 成功: kubectl版本信息获取成功")
            
            print()
            
            # 5. 列出资源
            print("5. 列出可用资源...")
            resources = await client.list_resources()
            for resource in resources['resources']:
                print(f"   - {resource['uri']}: {resource['name']}")
            print()
            
            # 6. 测试资源读取
            print("6. 测试资源读取...")
            cluster_resource = await client.read_resource("k8s://cluster/info")
            if "error" in cluster_resource:
                print(f"   ❌ 错误: {cluster_resource['error']}")
            else:
                print(f"   ✅ 成功: 集群资源信息获取成功")
            
            print()
            print("🎉 所有测试完成！")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                MCP客户端测试工具                             ║")
    print("║                                                              ║")
    print("║  测试Kubernetes MCP SSE服务器的功能                          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    await test_mcp_server()


if __name__ == "__main__":
    asyncio.run(main()) 