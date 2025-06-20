#!/bin/bash

IMAGE_NAME=op-mcp
CONTAINER_NAME=op-mcp
PORT=8000

function build() {
    echo "构建 Docker 镜像..."
    docker build -t $IMAGE_NAME .
}

function start() {
    echo "启动容器..."
    docker run -d --name $CONTAINER_NAME -p $PORT:8000 --restart=always $IMAGE_NAME
}

function stop() {
    echo "停止并删除容器..."
    docker stop $CONTAINER_NAME 2>/dev/null
    docker rm $CONTAINER_NAME 2>/dev/null
}

function clean() {
    stop
    echo "删除镜像..."
    docker rmi $IMAGE_NAME
}

function restart() {
    stop
    start
}

function usage() {
    echo "用法: $0 [build|start|stop|restart|clean]"
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
    restart)
        restart
        ;;
    clean)
        clean
        ;;
    *)
        usage
        ;;
esac 