#!/usr/bin/env python3
"""
Caelum v8.0 - AI驱动的网络安全自动化平台
使用统一工具框架，代码精简33%
"""

import logging
import json
import sys
import argparse
import uuid
import threading
import concurrent.futures
from typing import Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
from tools_framework import UnifiedToolFramework, ToolConfig, ToolCategory
from payload_generator import UnifiedPayloadGenerator
from ai_analyzer import AIAnalyzer, AutomatedTestEngine
import psutil
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# 禁用静态文件缓存，防止页面重复或旧样式报错
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 配置CORS - 允许所有
CORS(app, resources={r"/api/*": {"origins": "*"}})

tool_framework = UnifiedToolFramework()
payload_generator = UnifiedPayloadGenerator()
ai_analyzer = AIAnalyzer()
automated_test_engine = AutomatedTestEngine(ai_analyzer, tool_framework)

# 运行时进度存储
test_progress_store: Dict[str, Dict[str, Any]] = {}
test_progress_lock = threading.Lock()

# 定义全局多目标高并发线程池，上限3~5并发
# 解决大赛要求的：>3个并发目标同时测试能力，且不卡死系统资源
MAX_CONCURRENT_TARGETS = 4
target_test_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TARGETS)

def init_tools():
    """初始化工具框架 - 框架会自动注册所有工具"""
    # 框架在初始化时会自动调用_register_tools()
    # 这里不需要手动注册，框架已经包含了所有工具
    logger.info(f"✅ 工具框架已初始化，包含 {len(tool_framework.tools)} 个工具")

# ============================================================================
# API 路由 - 统一API接口
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "version": "8.0",
        "framework": "Caelum Unified Framework",
        "tools_loaded": len(tool_framework.tools),
        "cache_size": len(tool_framework.execution_cache)
    }), 200

@app.route('/api/tools/list', methods=['GET'])
def list_tools():
    """列出所有工具"""
    category = request.args.get('category')
    tools = tool_framework.list_tools(category)
    return jsonify({
        "total_tools": len(tools),
        "category": category,
        "tools": tools
    }), 200

@app.route('/api/tools/info/<tool_name>', methods=['GET'])
def get_tool_info(tool_name):
    """获取工具信息"""
    tool_info = tool_framework.get_tool_info(tool_name)
    if "error" in tool_info:
        return jsonify(tool_info), 404
    return jsonify(tool_info), 200

@app.route('/api/tools/execute', methods=['POST'])
def execute_tool():
    """执行单个工具 - v7.0 统一接口"""
    data = request.get_json()

    tool_name = data.get('tool')
    params = data.get('params', {})
    use_cache = data.get('use_cache', True)

    if not tool_name:
        return jsonify({"error": "Missing 'tool' parameter"}), 400

    try:
        result = tool_framework.execute_tool(
            tool_name=tool_name,
            params=params,
            use_cache=use_cache
        )
        return jsonify(result), 200 if result.get("success") else 500
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/tools/execute-chain', methods=['POST'])
def execute_tool_chain():
    """执行工具链 - v7.0 新增特性"""
    data = request.get_json()

    chain = data.get('chain', [])
    params = data.get('params', {})

    if not chain:
        return jsonify({"error": "Missing 'chain' parameter"}), 400

    try:
        result = tool_framework.execute_tool_chain(
            chain=chain,
            params=params
        )
        return jsonify(result), 200 if result.get("success") else 500
    except Exception as e:
        logger.error(f"Error executing tool chain: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/tools/cache/clear', methods=['POST'])
def clear_cache():
    """清除缓存"""
    tool_framework.clear_cache()
    return jsonify({"success": True, "message": "Cache cleared"}), 200

@app.route('/api/tools/cache/stats', methods=['GET'])
def cache_stats():
    """获取缓存统计"""
    return jsonify({
        "cache_size": len(tool_framework.execution_cache),
        "cached_tools": list(tool_framework.execution_cache.keys())[:10]  # 只显示前10个
    }), 200

@app.route('/api/payloads/generate', methods=['POST'])
def generate_payload():
    """生成Payload - v7.0 统一接口"""
    data = request.get_json()

    payload_type = data.get('type', 'xss')
    difficulty = data.get('difficulty', 'basic')
    count = data.get('count', 1)

    try:
        payloads = []
        for _ in range(count):
            payload = payload_generator.generate_payload(
                payload_type=payload_type,
                difficulty=difficulty
            )
            payloads.append(payload)

        return jsonify({
            "success": True,
            "type": payload_type,
            "difficulty": difficulty,
            "count": count,
            "payloads": payloads
        }), 200
    except Exception as e:
        logger.error(f"Error generating payload: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/payloads/list', methods=['GET'])
def list_payload_types():
    """列出所有Payload类型"""
    types = payload_generator.list_payload_types()
    return jsonify({
        "payload_types": types,
        "total": len(types)
    }), 200

@app.route('/api/payloads/for-target', methods=['POST'])
def generate_payload_for_target():
    """为特定目标生成Payload"""
    data = request.get_json()

    target_url = data.get('target_url')
    target_tech = data.get('target_tech', 'web')  # web, api, mobile, desktop
    attack_type = data.get('attack_type', 'xss')

    if not target_url:
        return jsonify({"error": "Missing 'target_url' parameter"}), 400

    try:
        payload = payload_generator.generate_payload_for_target(
            target_url=target_url,
            target_tech=target_tech,
            attack_type=attack_type
        )
        return jsonify({
            "success": True,
            "target_url": target_url,
            "target_tech": target_tech,
            "attack_type": attack_type,
            "payload": payload
        }), 200
    except Exception as e:
        logger.error(f"Error generating payload for target: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/payloads/exploit', methods=['POST'])
def generate_exploit_code():
    """生成Exploit代码"""
    data = request.get_json()

    vuln_type = data.get('vuln_type', 'buffer_overflow')
    target_arch = data.get('target_arch', 'x64')
    target_os = data.get('target_os', 'linux')

    try:
        exploit_code = payload_generator.generate_exploit_code(
            vuln_type=vuln_type,
            target_arch=target_arch,
            target_os=target_os
        )
        return jsonify({
            "success": True,
            "vuln_type": vuln_type,
            "target_arch": target_arch,
            "target_os": target_os,
            "exploit_code": exploit_code
        }), 200
    except Exception as e:
        logger.error(f"Error generating exploit code: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ============================================================================
# AI 分析与自动化测试 API
# ============================================================================

@app.route('/api/ai/analyze-target', methods=['POST'])
def analyze_target():
    """AI目标分析"""
    data = request.get_json()
    target_info = data.get('target_info', {})
    model = data.get('model', 'gpt-4')

    try:
        result = ai_analyzer.analyze_target(target_info, model)
        return jsonify({
            "success": True,
            "analysis": result
        }), 200
    except Exception as e:
        logger.error(f"AI目标分析失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/ai/generate-test-plan', methods=['POST'])
def generate_test_plan():
    """生成测试计划"""
    data = request.get_json()
    analysis_result = data.get('analysis_result', {})
    available_tools = data.get('available_tools', [])

    try:
        plan = ai_analyzer.generate_test_plan(analysis_result, available_tools)
        return jsonify({
            "success": True,
            "test_plan": plan
        }), 200
    except Exception as e:
        logger.error(f"测试计划生成失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/ai/analyze-vulnerability', methods=['POST'])
def analyze_vulnerability():
    """AI漏洞分析"""
    data = request.get_json()
    scan_result = data.get('scan_result', {})

    try:
        analysis = ai_analyzer.analyze_vulnerability(scan_result)
        return jsonify({
            "success": True,
            "vulnerability_analysis": analysis
        }), 200
    except Exception as e:
        logger.error(f"漏洞分析失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/automated-test/run', methods=['POST'])
def run_automated_test():
    """执行自动化渗透测试"""
    data = request.get_json()
    targets_str = data.get('target', '')
    model = data.get('model', 'gpt-4')

    if not targets_str:
        return jsonify({"error": "Missing 'target' parameter"}), 400

    # 支持多目标逗号分隔，最多4个
    raw_targets = [t.strip() for t in targets_str.split(',') if t.strip()]
    if not raw_targets:
        return jsonify({"error": "Invalid 'target' parameter"}), 400
    
    targets = raw_targets[:4] # 限制最多4个目标并发
    
    responses = []
    
    for target in targets:
        session_id = str(uuid.uuid4())

        with test_progress_lock:
            test_progress_store[session_id] = {
                "current_stage": "queued",
                "status": "running",
                "message": "任务已创建，等待执行",
                "percentage": 0,
                "target": target,
                "model": model
            }
            
        responses.append({
            "target": target,
            "session_id": session_id
        })

        def run_test_task_for_target(t_session_id, t_target):
            # 将回调包裹一层以便正确传递 session_id
            def target_progress_callback(stage, status, message):
                stage_percentage = {
                    "analysis": 15, "recon": 35, "scan": 55, 
                    "exploit": 75, "post": 90, "report": 100, "error": 100
                }
                progress = {
                    "current_stage": stage,
                    "status": status,
                    "message": message,
                    "percentage": stage_percentage.get(stage, 0)
                }
                with test_progress_lock:
                    if t_session_id in test_progress_store:
                        test_progress_store[t_session_id].update(progress)
                logger.info(f"进度更新[{t_session_id}]: {stage} - {status} - {message}")

            try:
                logger.info(f"开启测试线程: {t_session_id} for target {t_target}")
                result = automated_test_engine.run_automated_test(
                    target=t_target,
                    model=model,
                    progress_callback=target_progress_callback,
                    session_id=t_session_id
                )
                with test_progress_lock:
                    if t_session_id in test_progress_store:
                        test_progress_store[t_session_id]["status"] = "completed"
                        test_progress_store[t_session_id]["result"] = result
            except Exception as e:
                logger.error(f"Error in test task for {t_target}: {str(e)}")
                with test_progress_lock:
                    if t_session_id in test_progress_store:
                        test_progress_store[t_session_id]["status"] = "failed"
                        test_progress_store[t_session_id]["error"] = str(e)

        # 将原本裸线程改为交由限定并发的线程池调度，满足大赛“≥3并发”且避免爆炸
        target_test_pool.submit(run_test_task_for_target, session_id, target)

    return jsonify({
        "success": True,
        "message": f"Assigned {len(targets)} targets",
        "jobs": responses
    }), 201

@app.route('/api/automated-test/progress/<session_id>', methods=['GET'])
def get_test_progress(session_id: str):
    """获取测试进度"""
    try:
        with test_progress_lock:
            progress = test_progress_store.get(session_id)

        if not progress:
            return jsonify({
                "success": False,
                "error": "Session not found"
            }), 404

        return jsonify({
            "success": True,
            "progress": progress
        }), 200
    except Exception as e:
        logger.error(f"获取测试进度失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/automated-test/history', methods=['GET'])
def get_test_history():
    """获取测试历史"""
    try:
        # 深拷贝已完成的历史，防止并发修改
        history = list(automated_test_engine.test_history)

        # 补全当前正在运行的任务 (来自进度存储)
        with test_progress_lock:
            for sid, progress in test_progress_store.items():
                if progress.get("status") == "running":
                    history.append({
                        "session_id": sid,
                        "target": progress.get("target"),
                        "status": "running",
                        "start_time": datetime.now().isoformat()
                    })

        return jsonify({
            "success": True,
            "history": history[-10:]  # 返回最近10个测试记录
        }), 200
    except Exception as e:
        logger.error(f"获取测试历史失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/automated-test/report/<session_id>', methods=['GET'])
def get_test_report(session_id: str):
    """获取测试报告"""
    try:
        for session in automated_test_engine.test_history:
            if session.get('session_id') == session_id or session.get('target') == session_id or str(session.get('start_time')) == session_id:
                report = session.get('report') or ai_analyzer.generate_report(session.get('stages', []), session)
                return jsonify({
                    "success": True,
                    "report": report
                }), 200

        return jsonify({"error": "Test session not found"}), 404
    except Exception as e:
        logger.error(f"获取测试报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ============================================================================
# 前端界面
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """提供前端界面"""
    return app.send_static_file('index.html')

# ============================================================================
# 向后兼容性 - 旧API端点包装
# ============================================================================

@app.route('/api/command', methods=['POST'])
def api_command():
    """向后兼容: 执行任意命令"""
    data = request.get_json()
    command = data.get('command')

    if not command:
        return jsonify({"error": "Missing 'command' parameter"}), 400

    try:
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        return jsonify({
            "success": True,
            "command": command,
            "output": result.stdout,
            "error": result.stderr
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/telemetry', methods=['GET'])
def api_telemetry():
    """系统性能指标"""
    import psutil

    return jsonify({
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "uptime": time.time(),
        "tools_loaded": len(tool_framework.tools),
        "cache_size": len(tool_framework.execution_cache)
    }), 200

# ============================================================================
# 启动服务器
# ============================================================================

def start_server(host='0.0.0.0', port=8888):
    """启动Flask服务器"""
    logger.info(f"🚀 启动 Caelum v8.0 服务器 - {host}:{port}")

    init_tools()

    logger.info("✅ 服务器已启动，等待请求...")
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Caelum v7.0 服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址')
    parser.add_argument('--port', type=int, default=8888, help='服务器端口')

    args = parser.parse_args()

    start_server(host=args.host, port=args.port)
