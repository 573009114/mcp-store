#!/usr/bin/env python3
"""
Kubernetes客户端测试
"""
import pytest  # type: ignore
import asyncio
import sys
from pathlib import Path

# 添加父目录到Python路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from k8s_client import KubernetesClient


class TestKubernetesClient:
    """Kubernetes客户端测试类"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        return KubernetesClient()
    
    @pytest.mark.asyncio
    async def test_get_cluster_info(self, client):
        """测试获取集群信息"""
        info = await client.get_cluster_info()
        assert isinstance(info, dict)
        assert "status" in info
    
    @pytest.mark.asyncio
    async def test_list_pods(self, client):
        """测试列出Pod"""
        pods = await client.list_pods()
        assert isinstance(pods, list)
    
    @pytest.mark.asyncio
    async def test_list_services(self, client):
        """测试列出Service"""
        services = await client.list_services()
        assert isinstance(services, list)
    
    @pytest.mark.asyncio
    async def test_list_deployments(self, client):
        """测试列出Deployment"""
        deployments = await client.list_deployments()
        assert isinstance(deployments, list)
    
    @pytest.mark.asyncio
    async def test_execute_kubectl(self, client):
        """测试执行kubectl命令"""
        result = await client.execute_kubectl("version --client")
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_get_resource_details_invalid_type(self, client):
        """测试获取无效资源类型的详情"""
        result = await client.get_resource_details("invalid_type", "test")
        assert isinstance(result, dict)
        assert "error" in result


def run_tests():
    """运行测试"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests() 