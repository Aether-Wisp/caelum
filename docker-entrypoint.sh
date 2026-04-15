#!/bin/bash

# Caelum Docker 启动脚本

set -e

echo "🚀 正在启动 Caelum v8.0 服务器..."
echo "================================"

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  警告: 未配置任何 AI 模型 API 密钥"
    echo "   建议配置以下之一："
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - DEEPSEEK_API_KEY"
    echo ""
fi

# 创建必要的目录
mkdir -p data reports .cache

# 检查工具可用性
echo "🔍 检查安全工具..."
tools=(nmap sqlmap nuclei ffuf gobuster nikto hashcat john hydra gdb radare2)
installed=0
missing=0

for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "  ✅ $tool"
        ((installed++))
    else
        echo "  ❌ $tool (未安装)"
        ((missing++))
    fi
done

echo ""
echo "📊 工具统计: $installed 个已安装，$missing 个缺失"
echo ""

if [ $installed -eq 0 ]; then
    echo "⚠️  没有检测到任何安全工具！"
    echo "   某些功能可能无法正常工作。"
    echo ""
fi

# 启动 Flask 服务器
echo "🌐 启动 Flask 服务器在 0.0.0.0:8888..."
echo "视图访问: http://localhost:8888"
echo ""

# 如果提供了命令参数，执行参数命令，否则运行服务器
if [ $# -eq 0 ]; then
    exec python3 caelum_server.py
else
    exec "$@"
fi
