# Caelum v8.0 - 完整渗透测试平台 Docker 镜像
# 包含所有 74 个安全工具和 Python 依赖

FROM kalilinux/kali-rolling

LABEL maintainer="Caelum Team"
LABEL description="Caelum v8.0 - AI-Driven Security Automation Platform"
LABEL version="8.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 更新系统并安装基础工具
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    # 基础工具
    build-essential \
    git \
    curl \
    wget \
    python3-pip \
    python3-dev \
    libssl-dev \
    libffi-dev \
    golang-go \
    # 网络工具
    nmap \
    masscan \
    netcat-traditional \
    tcpdump \
    # Web应用工具
    sqlmap \
    wpscan \
    nikto \
    # 密码破解
    hashcat \
    john \
    hydra \
    # 二进制分析
    gdb \
    radare2 \
    binwalk \
    # 其他
    vim \
    nano \
    htop \
    tmux \
    screen \
    git-all

# 安装 ffuf, gobuster, nuclei 等工具
RUN apt-get install -y \
    ffuf \
    gobuster \
    wfuzz \
    nuclei \
    amass \
    subfinder \
    httpx-toolkit

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装 Python 依赖 (添加 --break-system-packages 以绕过最新 Kali 的 PEP 668 限制)
RUN pip3 install --upgrade pip --break-system-packages && \
    pip3 install -r requirements.txt --break-system-packages && \
    pip3 install pwntools angr shodan censys --break-system-packages

# 创建虚拟环境（可选）
RUN python3 -m venv /opt/caelum_env

# 暴露端口
EXPOSE 8888

# 启动脚本
RUN chmod +x /app/docker-entrypoint.sh 2>/dev/null || true

# 默认命令
CMD ["python3", "src/caelum/server.py"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1
