#!/bin/bash

# Caelum v8.0 - 自动化工具安装脚本
# 支持：Ubuntu/Debian, CentOS/RHEL, Kali Linux, macOS

set -e  # 任何错误都停止执行

echo "🚀 Caelum v8.0 安全工具自动安装"
echo "================================"

# 检测操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
fi

echo "📍 检测到系统: $OS"

# 更新包管理器
echo "🔄 更新包管理器..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    sudo apt update
    sudo apt upgrade -y
elif [[ "$OS" == "centos" || "$OS" == "rhel" ]]; then
    sudo yum update -y
elif [[ "$OS" == "macos" ]]; then
    brew update
fi

# 安装基础工具
echo "📦 安装基础开发工具..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    sudo apt install -y \
        build-essential \
        git \
        curl \
        wget \
        python3-pip \
        python3-dev \
        libssl-dev \
        libffi-dev \
        golang-go

elif [[ "$OS" == "centos" || "$OS" == "rhel" ]]; then
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y \
        git \
        curl \
        wget \
        python3-devel \
        openssl-devel \
        libffi-devel \
        golang

elif [[ "$OS" == "macos" ]]; then
    brew install git curl wget python3 openssl libffi go
fi

# 安装网络扫描工具
echo "🔍 安装网络扫描工具..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    sudo apt install -y \
        nmap \
        masscan \
        rustscan \
        autorecon \
        zmap \
        unicornscan \
        netdiscover

elif [[ "$OS" == "centos" || "$OS" == "rhel" ]]; then
    sudo yum install -y nmap
    # 其他工具从源码安装
    echo "⚠️  某些工具需要从源码安装..."

elif [[ "$OS" == "macos" ]]; then
    brew install nmap
fi

# 安装Web应用扫描工具
echo "🌐 安装Web应用扫描工具..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    sudo apt install -y \
        sqlmap \
        wpscan \
        nikto \
        ffuf \
        gobuster \
        dirbuster \
        dirb \
        dirsearch \
        wfuzz

    # Nuclei (Go-based)
    echo "📥 安装 Nuclei..."
    GO111MODULE=on go get -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei
    
    # 其他工具
    sudo apt install -y \
        dalfox \
        paramspider

elif [[ "$OS" == "centos" || "$OS" == "rhel" ]]; then
    sudo yum install -y \
        httpd-tools \
        curl
    echo "⚠️  Web工具需要手动安装..."

elif [[ "$OS" == "macos" ]]; then
    brew install sqlmap nikto ffuf gobuster wfuzz
fi

# 安装密码破解工具
echo "🔐 安装密码破解工具..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    sudo apt install -y \
        hashcat \
        john \
        hydra \
        medusa \
        patator

elif [[ "$OS" == "centos" || "$OS" == "rhel" ]]; then
    sudo yum install -y john hydra

elif [[ "$OS" == "macos" ]]; then
    brew install hashcat john hydra
fi

# 安装后渗透工具
echo "⚡ 安装后渗透工具..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    sudo apt install -y \
        enum4linux \
        smbmap \
        bloodhound \
        responder

elif [[ "$OS" == "macos" ]]; then
    brew install enum4linux smbmap
fi

# 安装二进制分析工具
echo "🔬 安装二进制分析工具..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    sudo apt install -y \
        gdb \
        radare2 \
        binwalk \
        strings \
        objdump \
        readelf

    # Ghidra (Java-based)
    if ! command -v ghidra &> /dev/null; then
        echo "📥 Ghidra 需要单独下载：https://github.com/NationalSecurityAgency/ghidra/releases"
    fi

elif [[ "$OS" == "macos" ]]; then
    brew install gdb radare2 binwalk
fi

# 安装取证工具
echo "🔎 安装取证工具..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    sudo apt install -y \
        volatility3 \
        steghide \
        exiftool \
        foremost \
        photorec \
        testdisk \
        scalpel \
        bulk-extractor

elif [[ "$OS" == "macos" ]]; then
    brew install exiftool steghide
fi

# 安装OSINT工具
echo "🕵️ 安装OSINT工具..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "kali" ]]; then
    # Amass (Go-based)
    GO111MODULE=on go get -v github.com/OWASP/Amass/v3/...
    
    # Subfinder (Go-based)
    GO111MODULE=on go get -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder
    
    # httpx (Go-based)
    GO111MODULE=on go get -v github.com/projectdiscovery/httpx/cmd/httpx

elif [[ "$OS" == "macos" ]]; then
    GO111MODULE=on go get -v github.com/OWASP/Amass/v3/...
    GO111MODULE=on go get -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder
fi

# Python工具
echo "🐍 安装Python安全工具..."
pip3 install --upgrade \
    pwntools \
    angr \
    shodan \
    censys \
    requests \
    beautifulsoup4

# 验证安装
echo ""
echo "✅ 验证工具安装..."
echo "================================"

tools_to_check=(
    "nmap"
    "sqlmap"
    "nikto"
    "ffuf"
    "gobuster"
    "hashcat"
    "john"
    "hydra"
    "gdb"
    "radare2"
    "binwalk"
)

for tool in "${tools_to_check[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "✅ $tool - 已安装"
    else
        echo "❌ $tool - 未安装"
    fi
done

echo ""
echo "🎉 安装完成！"
echo "现在可以启动 Caelum 服务器："
echo "  python caelum_server.py"
echo ""
echo "然后访问：http://localhost:8888"
