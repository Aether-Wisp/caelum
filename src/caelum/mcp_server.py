#!/usr/bin/env python3
"""
Caelum v8.0 MCP 客户端 - AI代理通信接口
"""

import sys
import logging
import json
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化MCP服务器
mcp = FastMCP("Caelum", "7.0")

# Caelum服务器地址
CAELUM_SERVER = "http://localhost:8888"

# ============================================================================
# MCP 工具 - 由AI代理调用
# ============================================================================

@mcp.tool()
def execute_tool(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行单个安全工具
    
    参数:
        tool: 工具名称 (nmap, nuclei, sqlmap 等)
        params: 工具参数字典
    """
    try:
        response = requests.post(
            f"{CAELUM_SERVER}/api/tools/execute",
            json={"tool": tool, "params": params},
            timeout=300
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def execute_tool_chain(chain: list, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    按顺序执行多个工具链
    
    参数:
        chain: 工具列表 ['nmap', 'nuclei', 'sqlmap']
        params: 共享参数
    """
    try:
        response = requests.post(
            f"{CAELUM_SERVER}/api/tools/execute-chain",
            json={"chain": chain, "params": params},
            timeout=600
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_payload(type: str, difficulty: str = "basic", count: int = 1) -> Dict[str, Any]:
    """
    生成安全测试Payload
    
    参数:
        type: Payload类型 (xss, sqli, lfi, cmd, xxe)
        difficulty: 难度等级 (basic, intermediate, advanced)
        count: 生成数量
    """
    try:
        response = requests.post(
            f"{CAELUM_SERVER}/api/payloads/generate",
            json={"type": type, "difficulty": difficulty, "count": count},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_tools() -> Dict[str, Any]:
    """列出所有可用的安全工具"""
    try:
        response = requests.get(f"{CAELUM_SERVER}/api/tools/list", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_payloads() -> Dict[str, Any]:
    """列出所有可用的Payload类型"""
    try:
        response = requests.get(f"{CAELUM_SERVER}/api/payloads/list", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def server_health() -> Dict[str, Any]:
    """检查Caelum服务器状态"""
    try:
        response = requests.get(f"{CAELUM_SERVER}/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"error": f"Server unavailable: {str(e)}"}

@mcp.tool()
def server_telemetry() -> Dict[str, Any]:
    """获取服务器性能指标"""
    try:
        response = requests.get(f"{CAELUM_SERVER}/api/telemetry", timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# 启动MCP服务器
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 启动 Caelum v8.0 MCP 客户端")
    logger.info(f"📡 连接到 Caelum 服务器: {CAELUM_SERVER}")
    
    # 定期检查服务器状态
    import asyncio
    import time
    
    async def check_server():
        """异步检查服务器状态"""
        while True:
            try:
                response = requests.get(f"{CAELUM_SERVER}/health", timeout=5)
                if response.status_code == 200:
                    logger.debug("✅ 服务器连接正常")
            except:
                logger.warning("⚠️ 无法连接到 Caelum 服务器")
            await asyncio.sleep(30)
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("✋ MCP 客户端已停止")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 错误: {str(e)}")
        sys.exit(1)
