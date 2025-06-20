# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 配置apt使用国内源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装curl和必要的工具
RUN apt-get update && apt-get install -y curl wget && rm -rf /var/lib/apt/lists/*

# 直接用官方源下载x86_64 kubectl，避免架构和HTML问题
RUN curl -LO "https://dl.k8s.io/release/v1.25.7/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# 复制依赖文件
COPY requirements.txt .

# 配置pip使用国内源并安装Python依赖
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --no-cache-dir -r requirements.txt

# 复制应用代码
COPY main.py .
COPY config.py .
COPY k8s_client.py .
COPY mcp_server.py .

# 创建kubeconfig目录并设置权限
RUN mkdir -p /app/.kube && chown -R root:root /app/.kube

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8081

# 启动命令
CMD ["python", "mcp_server.py"] 