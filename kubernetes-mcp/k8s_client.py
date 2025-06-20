"""
Kubernetes客户端封装
"""
import asyncio
import subprocess
import json
from typing import Dict, List, Optional, Any
from kubernetes import client, config as k8s_config  # type: ignore
from kubernetes.client.rest import ApiException  # type: ignore
from config import config


class KubernetesClient:
    """Kubernetes客户端类"""
    
    def __init__(self):
        self.client = None
        self.apps_client = None
        self._init_client()
    
    def _init_client(self):
        """初始化Kubernetes客户端"""
        try:
            if config.k8s.kubeconfig_path:
                k8s_config.load_kube_config(  # type: ignore
                    config_file=config.k8s.kubeconfig_path,
                    context=config.k8s.context
                )
            else:
                k8s_config.load_incluster_config()  # type: ignore
            
            self.client = client.CoreV1Api()
            self.apps_client = client.AppsV1Api()
            
        except Exception as e:
            print(f"初始化Kubernetes客户端失败: {e}")
            self.client = None
            self.apps_client = None
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """获取集群信息"""
        if not self.client:
            return {
                "status": "error",
                "error": "Kubernetes客户端未初始化"
            }
        
        try:
            # 使用线程池执行同步的Kubernetes API调用
            loop = asyncio.get_event_loop()
            version_info = await loop.run_in_executor(None, self.client.get_api_resources)
            
            return {
                "status": "connected",
                "api_resources": len(version_info.resources),
                "kubeconfig_path": config.k8s.kubeconfig_path,
                "context": config.k8s.context,
                "namespace": config.k8s.namespace
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def list_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出Pod"""
        if not self.client:
            return [{"error": "Kubernetes客户端未初始化"}]
        
        if not namespace:
            namespace = config.k8s.namespace
            
        try:
            loop = asyncio.get_event_loop()
            pods = await loop.run_in_executor(None, self.client.list_namespaced_pod, namespace)
            
            return [
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "ready": pod.status.ready,
                    "restarts": pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0,
                    "age": pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else None
                }
                for pod in pods.items
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    async def list_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出Service"""
        if not self.client:
            return [{"error": "Kubernetes客户端未初始化"}]
        
        if not namespace:
            namespace = config.k8s.namespace
            
        try:
            loop = asyncio.get_event_loop()
            services = await loop.run_in_executor(None, self.client.list_namespaced_service, namespace)
            
            return [
                {
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "type": svc.spec.type,
                    "cluster_ip": svc.spec.cluster_ip,
                    "external_ip": svc.status.load_balancer.ingress[0].ip if svc.status.load_balancer.ingress else None,
                    "ports": [f"{port.port}:{port.target_port}" for port in svc.spec.ports] if svc.spec.ports else []
                }
                for svc in services.items
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    async def list_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出Deployment"""
        if not self.apps_client:
            return [{"error": "Kubernetes客户端未初始化"}]
        
        if not namespace:
            namespace = config.k8s.namespace
            
        try:
            loop = asyncio.get_event_loop()
            deployments = await loop.run_in_executor(None, self.apps_client.list_namespaced_deployment, namespace)
            
            return [
                {
                    "name": dep.metadata.name,
                    "namespace": dep.metadata.namespace,
                    "replicas": dep.spec.replicas,
                    "available": dep.status.available_replicas,
                    "ready": dep.status.ready_replicas,
                    "updated": dep.status.updated_replicas
                }
                for dep in deployments.items
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    async def get_pod_logs(self, pod_name: str, namespace: Optional[str] = None, tail_lines: int = 100) -> str:
        """获取Pod日志"""
        if not self.client:
            return "Kubernetes客户端未初始化"
        
        if not namespace:
            namespace = config.k8s.namespace
            
        try:
            loop = asyncio.get_event_loop()
            logs = await loop.run_in_executor(
                None, 
                self.client.read_namespaced_pod_log,
                pod_name,
                namespace,
                tail_lines
            )
            return logs
        except Exception as e:
            return f"获取日志失败: {e}"
    
    async def execute_kubectl(self, command: str) -> Dict[str, Any]:
        """执行kubectl命令"""
        try:
            # 构建完整的kubectl命令
            if config.k8s.kubeconfig_path:
                full_command = f"kubectl --kubeconfig={config.k8s.kubeconfig_path} {command}"
            else:
                full_command = f"kubectl {command}"
            
            if config.k8s.context:
                full_command += f" --context={config.k8s.context}"
            
            # 使用线程池执行命令
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    full_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": full_command
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "命令执行超时",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    async def get_resource_details(self, resource_type: str, resource_name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """获取资源详细信息"""
        if not self.client or not self.apps_client:
            return {"error": "Kubernetes客户端未初始化"}
        
        if not namespace:
            namespace = config.k8s.namespace
            
        try:
            loop = asyncio.get_event_loop()
            
            if resource_type.lower() == "pod":
                resource = await loop.run_in_executor(None, self.client.read_namespaced_pod, resource_name, namespace)
            elif resource_type.lower() == "service":
                resource = await loop.run_in_executor(None, self.client.read_namespaced_service, resource_name, namespace)
            elif resource_type.lower() == "deployment":
                resource = await loop.run_in_executor(None, self.apps_client.read_namespaced_deployment, resource_name, namespace)
            else:
                return {"error": f"不支持的资源类型: {resource_type}"}
            
            return {
                "name": resource.metadata.name,
                "namespace": resource.metadata.namespace,
                "labels": resource.metadata.labels,
                "annotations": resource.metadata.annotations,
                "creation_timestamp": resource.metadata.creation_timestamp.isoformat() if resource.metadata.creation_timestamp else None,
                "resource_version": resource.metadata.resource_version,
                "uid": resource.metadata.uid
            }
            
        except Exception as e:
            return {"error": str(e)} 