#!/bin/bash
set -e

IMAGE_NAME=op-mcp
CONTAINER_NAME=op-mcp
PORT=8000

function build() {
    echo "[+] 构建Docker镜像..."
    docker build -t $IMAGE_NAME . || { echo '[!] 镜像构建失败'; exit 1; }
}

function start() {
    # 精确匹配容器名
    if docker ps -a --format '{{.Names}}' | grep -w $CONTAINER_NAME > /dev/null; then
        echo "[+] 停止并删除旧容器..."
        docker stop $CONTAINER_NAME || true
        docker rm $CONTAINER_NAME || true
    fi
    # 检查端口占用
    if lsof -i :$PORT | grep LISTEN; then
        echo "[!] 端口 $PORT 已被占用，请先释放端口。"
        exit 1
    fi
    echo "[+] 启动新容器..."
    docker run -d --name $CONTAINER_NAME -p $PORT:8000 $IMAGE_NAME
    echo "[+] 部署完成，访问：http://localhost:$PORT"
    echo "[+] 查看日志：docker logs -f $CONTAINER_NAME"
}

function stop() {
    if docker ps -a --format '{{.Names}}' | grep -w $CONTAINER_NAME > /dev/null; then
        echo "[+] 停止并删除容器..."
        docker stop $CONTAINER_NAME || true
        docker rm $CONTAINER_NAME || true
    else
        echo "[!] 未找到容器 $CONTAINER_NAME"
    fi
}

function logs() {
    docker logs -f $CONTAINER_NAME
}

case "$1" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    logs)
        logs
        ;;
    *)
        echo "用法: $0 {build|start|stop|logs}"
        ;;
esac 
