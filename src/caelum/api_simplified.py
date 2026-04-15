#!/usr/bin/env python3
"""
Caelum Simplified API Layer
使用统一框架的简化API - 替代冗余的端点
"""

from flask import Flask, request, jsonify
import logging
from tools_framework import tool_framework, ToolCategory
from payload_generator import payload_generator

logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================================
# 统一的工具执行API
# ============================================================================

@app.route("/api/tools/execute", methods=["POST"])
def execute_tool():
    """
    统一的工具执行端点 - 替代所有单个工具端点
    
    请求示例:
    {
        "tool": "nmap",
        "params": {
            "target": "192.168.1.1",
            "scan_type": "-sV",
            "ports": "1-65535"
        },
        "use_cache": true
    }
    """
    try:
        data = request.json
        tool_name = data.get("tool", "").lower()
        params = data.get("params", {})
        use_cache = data.get("use_cache", True)
        
        if not tool_name:
            return jsonify({"error": "Tool name required"}), 400
        
        # 执行工具
        result = tool_framework.execute_tool(tool_name, params, use_cache)
        
        return jsonify({
            "success": result.get("success"),
            "tool": tool_name,
            "result": result
        })
    
    except Exception as e:
        logger.error(f"Error executing tool: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/execute-chain", methods=["POST"])
def execute_tool_chain():
    """
    工具链执行 - 按顺序执行多个工具
    
    请求示例:
    {
        "chain": ["nmap", "nuclei", "sqlmap"],
        "params": {
            "target": "192.168.1.1"
        }
    }
    """
    try:
        data = request.json
        chain = data.get("chain", [])
        params = data.get("params", {})
        
        if not chain:
            return jsonify({"error": "Tool chain required"}), 400
        
        result = tool_framework.execute_tool_chain(chain, params)
        
        return jsonify({
            "success": result.get("success"),
            "chain": chain,
            "result": result
        })
    
    except Exception as e:
        logger.error(f"Error executing tool chain: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/list", methods=["GET"])
def list_tools():
    """列出所有可用工具"""
    try:
        category = request.args.get("category")
        tools = tool_framework.list_tools(category)
        
        return jsonify({
            "success": True,
            "total_tools": len(tools),
            "tools": tools
        })
    
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/info/<tool_name>", methods=["GET"])
def get_tool_info(tool_name):
    """获取工具详情"""
    try:
        info = tool_framework.get_tool_info(tool_name)
        
        if "error" in info:
            return jsonify(info), 404
        
        return jsonify({
            "success": True,
            "tool_info": info
        })
    
    except Exception as e:
        logger.error(f"Error getting tool info: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/cache/clear", methods=["POST"])
def clear_tool_cache():
    """清除所有工具缓存"""
    try:
        tool_framework.clear_cache()
        
        return jsonify({
            "success": True,
            "message": "Tool cache cleared"
        })
    
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# 统一的Payload生成API
# ============================================================================

@app.route("/api/payloads/generate", methods=["POST"])
def generate_payload():
    """
    生成Payload
    
    请求示例:
    {
        "type": "xss",
        "difficulty": "basic",
        "count": 5
    }
    """
    try:
        data = request.json
        payload_type = data.get("type", "").lower()
        difficulty = data.get("difficulty", "basic").lower()
        count = data.get("count", 1)
        
        if not payload_type:
            return jsonify({"error": "Payload type required"}), 400
        
        payloads = payload_generator.generate_payload(payload_type, difficulty, count)
        
        return jsonify({
            "success": True,
            "type": payload_type,
            "difficulty": difficulty,
            "count": len(payloads),
            "payloads": payloads
        })
    
    except Exception as e:
        logger.error(f"Error generating payload: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/payloads/for-target", methods=["POST"])
def generate_payload_for_target():
    """
    为特定技术栈生成Payload
    
    请求示例:
    {
        "target_tech": "php",
        "payload_type": "xss"
    }
    """
    try:
        data = request.json
        target_tech = data.get("target_tech", "").lower()
        payload_type = data.get("payload_type", "").lower()
        
        if not target_tech or not payload_type:
            return jsonify({"error": "target_tech and payload_type required"}), 400
        
        payloads = payload_generator.generate_payload_for_target(target_tech, payload_type)
        
        return jsonify({
            "success": True,
            "target_tech": target_tech,
            "payload_type": payload_type,
            "count": len(payloads),
            "payloads": payloads
        })
    
    except Exception as e:
        logger.error(f"Error generating payload: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/payloads/exploit", methods=["POST"])
def generate_exploit():
    """
    生成Exploit代码
    
    请求示例:
    {
        "cve_id": "CVE-2021-1234",
        "target_info": {
            "os": "Linux",
            "arch": "x64"
        }
    }
    """
    try:
        data = request.json
        cve_id = data.get("cve_id", "")
        target_info = data.get("target_info", {})
        
        if not cve_id:
            return jsonify({"error": "CVE ID required"}), 400
        
        exploit = payload_generator.generate_exploit_code(cve_id, target_info)
        
        return jsonify({
            "success": True,
            "exploit": exploit
        })
    
    except Exception as e:
        logger.error(f"Error generating exploit: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/payloads/list", methods=["GET"])
def list_payload_types():
    """列出所有Payload类型"""
    try:
        types = payload_generator.list_payload_types()
        stats = payload_generator.get_payload_stats()
        
        return jsonify({
            "success": True,
            "total_types": len(types),
            "types": types,
            "statistics": stats
        })
    
    except Exception as e:
        logger.error(f"Error listing payload types: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# 重定向旧API到新统一端点（兼容性）
# ============================================================================

@app.route("/api/tools/nmap", methods=["POST"])
def nmap_legacy():
    """Old endpoint - redirects to unified API"""
    data = request.json
    params = {
        "target": data.get("target"),
        "scan_type": data.get("scan_type", "-sCV"),
        "ports": data.get("ports", ""),
        "timing": data.get("timing", "T4") if "timing" in data else None,
        "args": data.get("additional_args", "")
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    result = tool_framework.execute_tool("nmap", params)
    return jsonify(result)

@app.route("/api/tools/gobuster", methods=["POST"])
def gobuster_legacy():
    """Old endpoint - redirects to unified API"""
    data = request.json
    params = {
        "url": data.get("url"),
        "wordlist": data.get("wordlist", "/usr/share/wordlists/dirb/common.txt"),
        "threads": data.get("threads", "50"),
        "args": data.get("additional_args", "")
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    result = tool_framework.execute_tool("gobuster", params)
    return jsonify(result)

@app.route("/api/tools/sqlmap", methods=["POST"])
def sqlmap_legacy():
    """Old endpoint - redirects to unified API"""
    data = request.json
    params = {
        "url": data.get("url"),
        "args": data.get("additional_args", "")
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    result = tool_framework.execute_tool("sqlmap", params)
    return jsonify(result)

@app.route("/api/payloads/generate", methods=["POST"])
def payloads_legacy():
    """Old endpoint - redirects to unified API"""
    data = request.json
    payload_type = data.get("attack_type", data.get("type", ""))
    difficulty = data.get("complexity", data.get("difficulty", "basic"))
    
    return generate_payload()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, host="0.0.0.0", port=8888)
