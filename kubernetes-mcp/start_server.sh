#!/bin/bash

# Kubernetes MCP SSE服务器启动脚本

set -eu

echo "🐳 构建Kubernetes MCP服务器..."

# 构建Docker镜像
docker build -t kubernetes-mcp-server:v1 .

echo "✅ Docker镜像构建完成"

echo "🚀 启动Kubernetes MCP服务器..."

# 检查kubeconfig文件
if [ -f /etc/rancher/k3s/k3s.yaml ]; then
    echo "📁 找到kubeconfig文件: /etc/rancher/k3s/k3s.yaml"
    KUBECONFIG_PATH="/etc/rancher/k3s/k3s.yaml"
elif [ -f "$HOME/.kube/config" ]; then
    echo "📁 找到kubeconfig文件: $HOME/.kube/config"
    KUBECONFIG_PATH="$HOME/.kube/config"
else
    echo "⚠️  未找到kubeconfig文件，将使用集群内配置"
    KUBECONFIG_PATH=""
fi

# 启动前删除同名容器（如果存在）
docker rm -f kubernetes-mcp-server 2>/dev/null || true

# 运行容器
if [ -n "$KUBECONFIG_PATH" ]; then
    docker run -d --network host --name kubernetes-mcp-server \
        -v "${KUBECONFIG_PATH}:/app/kubeconfig:ro" \
        -e K8S_KUBECONFIG_PATH=/app/kubeconfig \
        -e K8S_NAMESPACE=default \
        -e MCP_DEBUG=true \
        -e MCP_HOST=0.0.0.0 \
        -e MCP_PORT=8081 \
        kubernetes-mcp-server:v1
else
    docker run -d --network host --name kubernetes-mcp-server \
        -e K8S_NAMESPACE=default \
        -e MCP_DEBUG=true \
        -e MCP_HOST=0.0.0.0 \
        -e MCP_PORT=8081 \
        kubernetes-mcp-server:v1
fi

echo "✅ 服务器已启动"
echo "📊 服务器信息:"
echo "   - 地址: http://localhost:8080"
echo "   - SSE端点: http://localhost:8080/mcp/sse"
echo "   - 健康检查: http://localhost:8080/health"
echo ""
echo "🔧 管理命令:"
echo "   - 查看日志: docker logs kubernetes-mcp-server"
echo "   - 停止服务: docker stop kubernetes-mcp-server"
echo "   - 重启服务: docker restart kubernetes-mcp-server"
echo "   - 删除容器: docker rm kubernetes-mcp-server"
echo ""
echo "🧪 测试服务器:"
echo "   - 运行测试: python test_mcp_client.py" 
