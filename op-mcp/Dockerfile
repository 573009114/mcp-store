FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 

COPY . .

RUN set -eux; \
    release=$(grep VERSION_CODENAME /etc/os-release | cut -d= -f2); \
    rm -rf /etc/apt/sources.list.d/*; \
    echo "deb http://mirrors.aliyun.com/debian $release main contrib non-free\n\
deb http://mirrors.aliyun.com/debian $release-updates main contrib non-free\n\
deb http://mirrors.aliyun.com/debian-security $release-security main contrib non-free" > /etc/apt/sources.list; \
    apt-get update && apt-get install -y \
    procps \
    iproute2 \
    net-tools \
    curl \
    vim \
    less \
    psmisc \
    lsof \
    tree \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"] 