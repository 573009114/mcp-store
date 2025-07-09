#!/bin/bash
set -e

NAME=minio-mcp
PORT=8000

case "$1" in
  start)
    docker build --network host -t $NAME .
    docker run -d --name $NAME -p $PORT:8000 $NAME
    ;;
  stop)
    docker stop $NAME || true
    ;;
  logs)
    docker logs -f $NAME
    ;;
  rm)
    docker stop $NAME || true
    docker rm $NAME || true
    docker rmi $NAME || true
    ;;
  local)
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port $PORT --reload
    ;;
  *)
    echo "用法: $0 {start|stop|logs|rm|local}"
    ;;
esac 