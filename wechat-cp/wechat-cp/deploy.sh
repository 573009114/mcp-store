#!/bin/bash
set -e

IMAGE_NAME=wechat-cp-mcp:latest
CONTAINER_NAME=wechat-cp-mcp

function build_image() {
  echo "[构建镜像]"
  docker build --no-cache --network host -t $IMAGE_NAME .
}

function start_container() {
  echo "[启动容器]"
  mkdir -p $(pwd)/data
  ENV_ARGS=""
  if [ -f .env ]; then
    echo "检测到 .env 文件，自动注入环境变量"
    while IFS= read -r line; do
      if [[ $line == \#* ]] || [[ -z $line ]]; then continue; fi
      varname=$(echo $line | cut -d '=' -f 1)
      ENV_ARGS="$ENV_ARGS -e $varname"
    done < .env
  fi
  docker run -d --name $CONTAINER_NAME -p 8000:8000 \
    -v $(pwd)/app:/app/app \
    -v $(pwd)/data:/app/data \
    $ENV_ARGS \
    $IMAGE_NAME
  echo "服务已启动，访问：http://localhost:8000/docs"
}

function stop_and_remove_container() {
  echo "[停止并删除容器]"
  docker rm -f $CONTAINER_NAME 2>/dev/null || echo "容器未运行"
}

function show_logs() {
  echo "[查看容器日志]"
  docker logs -f $CONTAINER_NAME
}

case "$1" in
  build)
    build_image
    ;;
  start)
    stop_and_remove_container
    start_container
    ;;
  stop)
    stop_and_remove_container
    ;;
  logs)
    show_logs
    ;;
  *)
    echo "用法: $0 {build|start|stop|logs}"
    echo "  build  构建镜像"
    echo "  start  停止旧容器并启动新容器"
    echo "  stop   停止并删除容器"
    echo "  logs   查看容器日志"
    exit 1
    ;;
esac 