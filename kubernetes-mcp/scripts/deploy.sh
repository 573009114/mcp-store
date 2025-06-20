#!/bin/bash

# Kubernetes MCP服务器部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查Kubernetes集群连接
check_k8s_connection() {
    print_info "检查Kubernetes集群连接..."
    if ! kubectl cluster-info &> /dev/null; then
        print_error "无法连接到Kubernetes集群，请检查kubeconfig配置"
        exit 1
    fi
    print_success "Kubernetes集群连接正常"
}

# 构建Docker镜像
build_image() {
    print_info "构建Docker镜像..."
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        print_error "Docker未运行，请启动Docker服务"
        exit 1
    fi
    
    # 构建镜像
    docker build -t mcp-server:latest .
    print_success "Docker镜像构建完成"
}

# 部署到Kubernetes
deploy_to_k8s() {
    print_info "部署到Kubernetes集群..."
    
    # 创建命名空间
    kubectl apply -f k8s-deployment.yaml
    
    # 等待部署完成
    print_info "等待部署完成..."
    kubectl wait --for=condition=available --timeout=300s deployment/mcp-server -n mcp-server
    
    print_success "部署完成！"
}

# 获取服务信息
get_service_info() {
    print_info "获取服务信息..."
    
    # 获取Pod状态
    echo "Pod状态:"
    kubectl get pods -n mcp-server
    
    echo ""
    echo "服务信息:"
    kubectl get svc -n mcp-server
    
    echo ""
    echo "访问信息:"
    kubectl get ingress -n mcp-server
}

# 查看日志
view_logs() {
    print_info "查看MCP服务器日志..."
    kubectl logs -f deployment/mcp-server -n mcp-server
}

# 清理部署
cleanup() {
    print_warning "清理部署..."
    kubectl delete -f k8s-deployment.yaml
    print_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "Kubernetes MCP服务器部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build     构建Docker镜像"
    echo "  deploy    部署到Kubernetes集群"
    echo "  info      获取服务信息"
    echo "  logs      查看日志"
    echo "  cleanup   清理部署"
    echo "  full      完整部署流程（构建+部署）"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 full    # 完整部署"
    echo "  $0 deploy  # 仅部署"
    echo "  $0 logs    # 查看日志"
}

# 主函数
main() {
    case "${1:-help}" in
        "build")
            check_command "docker"
            build_image
            ;;
        "deploy")
            check_command "kubectl"
            check_k8s_connection
            deploy_to_k8s
            ;;
        "info")
            check_command "kubectl"
            get_service_info
            ;;
        "logs")
            check_command "kubectl"
            view_logs
            ;;
        "cleanup")
            check_command "kubectl"
            cleanup
            ;;
        "full")
            check_command "docker"
            check_command "kubectl"
            check_k8s_connection
            build_image
            deploy_to_k8s
            get_service_info
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 