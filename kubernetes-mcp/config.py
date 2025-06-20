"""
Kubernetes MCP Server 配置文件
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings  # type: ignore


class KubernetesConfig(BaseSettings):
    """Kubernetes配置"""
    kubeconfig_path: Optional[str] = None
    context: Optional[str] = None
    namespace: str = "default"
    
    model_config = {"env_prefix": "K8S_"}


class MCPServerConfig(BaseSettings):
    """MCP服务器配置"""
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    
    model_config = {"env_prefix": "MCP_"}


class Config:
    """主配置类"""
    def __init__(self):
        self.k8s = KubernetesConfig()
        self.mcp = MCPServerConfig()
        
        # 如果没有指定kubeconfig路径，尝试使用默认路径
        if not self.k8s.kubeconfig_path:
            default_paths = [
                os.path.expanduser("~/.kube/config"),
                "/etc/kubernetes/admin.conf",
                "/etc/kubernetes/kubeconfig"
            ]
            
            for path in default_paths:
                if os.path.exists(path):
                    self.k8s.kubeconfig_path = path
                    break


# 全局配置实例
config = Config() 