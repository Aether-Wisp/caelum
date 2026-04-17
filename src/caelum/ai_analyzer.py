#!/usr/bin/env python3
"""
Caelum v8.0 - AI驱动的网络安全自动化平台
大模型分析与决策模块
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai
import anthropic
import requests
from session_manager import PenetrationState, SessionManager

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """大模型分析与决策引擎"""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self._init_clients()

    def _init_clients(self):
        """初始化AI客户端"""
        # 强制使用用户提供的 DeepSeek API Key 作为默认客户端
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-ab474a0de0b84ff1bffd8aff98ed35c3')
        
        # 将 DeepSeek 直接挂载为 openai_client，因为 DeepSeek 完全兼容 OpenAI 库
        self.openai_client = openai.OpenAI(
            api_key=self.deepseek_api_key, 
            base_url="https://api.deepseek.com"
        )
        logger.info("✅ DeepSeek 客户端(通过 OpenAI 协议)初始化成功")

        # Anthropic Claude
        claude_key = os.getenv('ANTHROPIC_API_KEY')
        if claude_key:
            self.anthropic_client = anthropic.Anthropic(api_key=claude_key)
            logger.info("✅ Anthropic 客户端初始化成功")

    def analyze_target(self, target_info: Dict[str, Any], model: str = "gpt-4") -> Dict[str, Any]:
        """
        分析目标系统并提供测试建议

        Args:
            target_info: 目标信息字典
            model: 使用的模型 (gpt-4, claude-3, deepseek)

        Returns:
            分析结果字典
        """
        # 检查大模型API是否配置，如果没有则直接返回错误信息
        if not self.openai_client and not self.anthropic_client:
            error_msg = "未配置大模型 API Key，无法进行分析。请配置后重试。"
            return {"error": error_msg}

        prompt = f"""
        作为资深的高级红队安全专家与情报分析师，请基于 MITRE ATT&CK 框架与 PTES 标准，对以下目标资产进行深度评估并输出结构化建议：

        【目标情报资产】
        - 资产标识 (IP/Domain): {target_info.get('target', 'unknown')}
        - 暴露端口 (Ports): {target_info.get('ports', 'unknown')}
        - 服务指纹 (Services): {target_info.get('services', 'unknown')}
        - 操作系统 (OS Fingerprint): {target_info.get('os', 'unknown')}
        - 附加情报 (Context): {target_info.get('additional_info', 'none')}

        【分析指令】
        请输出包含以下维度的 JSON 格式研判报告：
        1. `system_assessment`: 目标基础设施架构画像 (Windows/Linux/Cloud/Container等) 及确信度评估。
        2. `attack_surface`: 基于暴露面的高价值脆弱点预测与攻击向量映射 (CVE/Misconfigurations)。
        3. `tool_chain`: 针对该目标的定制化杀伤链工具序列清单 (TTPs 对接)。
        4. `risk_rating`: 综合威胁评级 (Critical/High/Medium/Low) 及 CVSS 预估参考。
        5. `tactical_plan`: 涵盖纵向深入与横向扩展 (Lateral Movement) 的多阶测试策略脉络。

        必须严格遵循 JSON 格式输出，确保无多余 Markdown 代码块包裹导致解析失败。
        """

        try:
            if model.startswith("gpt"):
                return self._call_openai(prompt, model)
            elif model.startswith("claude"):
                return self._call_anthropic(prompt, model)
            elif model == "deepseek":
                return self._call_deepseek(prompt)
            else:
                return {"error": f"不支持的模型: {model}"}
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return {"error": str(e)}

    def generate_test_plan(self, analysis_result: Dict[str, Any], available_tools: List[str]) -> Dict[str, Any]:
        """
        基于分析结果生成测试计划

        Args:
            analysis_result: AI分析结果
            available_tools: 可用的工具列表

        Returns:
            测试计划字典
        """
        # 检查大模型API是否配置，如果没有则直接返回错误信息
        if not self.openai_client and not self.anthropic_client:
            error_msg = "未配置大模型 API Key，生成测试计划失败。请配置后重试。"
            return {"error": error_msg}

        prompt = f"""
        基于上一阶段的深度架构画像与已知测试武器库，请扮演 Red Team 指挥官 (Operations Commander)，自动生成高度详细的作战计划大纲，以应对复杂多阶的实战演练场景(如 Bugku PAR / HTB)。

        【目标研判输入】 
        {json.dumps(analysis_result, ensure_ascii=False, indent=2)}

        【现存武库资源】 
        {', '.join(available_tools)}

        请输出遵循 JSON 标准格式的《交战规则与执行大纲(ROE)》，且必须不含 markdown ````json` 外界包裹内容，JSON 必须包括以下结构：
        1. 阶段划分 (`phases` 数组)：(如 Recon_OSINT / Initial_Access_Web / PrivEsc_Local / Lateral_Movement_Internal 等)，体现明显的递进与扩展能力。
        2. 每阶段参数集 (`tool_execution`): 指导自动化引擎使用的工具序列与具体指令特征 (Payload Types)。
        3. 依赖流转 (`dependencies`): 本阶段测试是否依赖上一阶段捕获的凭证或网段路由信息(Hashes/Routing Tables)。
        4. 战果闭环与清洗 (`verification`): 用于验证渗透成果与痕迹清理操作的预期标准。
        5. OPSEC 风险控制 (`opsec_controls`): 防止业务破坏或触发高风险蜜罐/WAF防护拦截的战术安全阈值。
        """

        try:
            return self._call_available_model(prompt, preferred_model="gpt-4")
        except Exception as e:
            logger.error(f"测试计划生成失败: {str(e)}")
            return {"error": str(e)}

    def analyze_vulnerability(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析漏洞扫描结果并提供利用建议

        Args:
            scan_result: 扫描结果字典

        Returns:
            漏洞分析结果
        """
        # 检查大模型API是否配置，如果没有则直接返回错误信息
        if not self.openai_client and not self.anthropic_client:
            error_msg = "未配置大模型 API Key，漏洞分析失败。请配置后重试。"
            return {"error": error_msg}

        prompt = f"""
        【严格要求：双重验证去伪存真原则】作为资深红队分析师，分析以下漏洞扫描结果并进行真伪判定：

        为满足误报率 ≤5% 的核心指标，我们在解析底层工具（Nuclei/Nmap/Sqlmap等）产生的结果时强加“第二维度严重性”：
        如果仅是低微暴露或无实际回显打穿结果的，请一律打上“False Positive(误报)”降级剔除。
        必须给出进一步“上传特定 Payload 或执行命令以确认漏洞实际存在”的具体二重验证手段指示！

        扫描结果: {json.dumps(scan_result, ensure_ascii=False, indent=2)}

        请提供:
        1. 漏洞严重性评估
        2. 可利用性分析
        3. 推荐的利用工具和方法
        4. 潜在影响评估
        5. 修复建议

        以JSON格式返回。
        """

        try:
            return self._call_available_model(prompt, preferred_model="gpt-4")
        except Exception as e:
            logger.error(f"漏洞分析失败: {str(e)}")
            return {"error": str(e)}

    def generate_report(self, test_results: List[Dict[str, Any]], target_info: Dict[str, Any]) -> str:
        """
        生成渗透测试报告

        Args:
            test_results: 测试结果列表
            target_info: 目标信息

        Returns:
            报告内容（Markdown格式）
        """
        # 检查大模型API是否配置，如果没有则直接返回错误信息
        if not self.openai_client and not self.anthropic_client:
            error_msg = "未配置大模型 API Key，生成报告失败。请配置后重试。"
            return f"# 渗透测试报告\n\n生成失败: {error_msg}"

        prompt = f"""
        基于以下测试结果生成专业的渗透测试报告：

        目标信息: {json.dumps(target_info, ensure_ascii=False, indent=2)}

        测试结果: {json.dumps(test_results, ensure_ascii=False, indent=2)}

        请生成包含以下章节的报告:
        1. 执行摘要
        2. 测试方法论
        3. 发现的漏洞详情
        4. 风险评估
        5. 修复建议
        6. 结论

        使用Markdown格式，保持专业性和结构化。
        """

        try:
            response = self._call_available_model(prompt, preferred_model="gpt-4")
            return response.get("report") or response.get("response") or "报告生成失败"
        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}")
            return f"# 渗透测试报告\n\n生成失败: {str(e)}"

    def _call_available_model(self, prompt: str, preferred_model: str = "gpt-4") -> Dict[str, Any]:
        """按可用性选择AI提供商，优先使用指定模型。"""
        if preferred_model.startswith("gpt") and self.openai_client:
            return self._call_openai(prompt, preferred_model)

        if preferred_model.startswith("claude") and self.anthropic_client:
            return self._call_anthropic(prompt, preferred_model)

        if preferred_model == "deepseek" and self.deepseek_api_key:
            return self._call_deepseek(prompt)

        if self.openai_client:
            return self._call_openai(prompt, "gpt-4")

        if self.anthropic_client:
            return self._call_anthropic(prompt, "claude-3-sonnet-20240229")

        if self.deepseek_api_key:
            return self._call_deepseek(prompt)

        raise Exception("无可用AI客户端，请配置 OPENAI_API_KEY / ANTHROPIC_API_KEY / DEEPSEEK_API_KEY")

    def _call_openai(self, prompt: str, model: str = "deepseek-chat") -> Dict[str, Any]:
        """调用OpenAI API (目前连接到了DeepSeek)"""
        if not self.openai_client:
            raise Exception("客户端未初始化")

        # 强制替换为 DeepSeek 的模型名
        actual_model = "deepseek-chat"
        
        response = self.openai_client.chat.completions.create(
            model=actual_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )

        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except:
            return {"response": content}

    def _call_anthropic(self, prompt: str, model: str = "claude-3-sonnet-20240229") -> Dict[str, Any]:
        """调用Anthropic Claude API"""
        if not self.anthropic_client:
            raise Exception("Anthropic客户端未初始化")

        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text
        try:
            return json.loads(content)
        except:
            return {"response": content}

    def _call_deepseek(self, prompt: str) -> Dict[str, Any]:
        """调用DeepSeek API"""
        if not self.deepseek_api_key:
            raise Exception("DeepSeek API Key未配置")

        # DeepSeek API调用示例（需要根据实际API调整）
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.3
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",  # 示例URL
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            try:
                return json.loads(content)
            except:
                return {"response": content}
        else:
            raise Exception(f"DeepSeek API调用失败: {response.status_code}")

class AutomatedTestEngine:
    """自动化测试引擎 - Agentic Workflow"""

    def __init__(self, ai_analyzer: AIAnalyzer, tool_framework):
        self.ai_analyzer = ai_analyzer
        self.tool_framework = tool_framework
        self.test_history = []
        self.session_manager = SessionManager()

    def _get_tools_schema(self):
        """动态生成 OpenAI Tools Schema"""
        tools = []
        for name, config in self.tool_framework.tools.items():
            tool_schema = {
                "type": "function",
                "function": {
                    "name": name.replace("-", "_"),  # OpenAI 不允许函数名有横线
                    "description": config.description,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": config.required_params
                    }
                }
            }
            for param in config.required_params + config.optional_params:
                tool_schema["function"]["parameters"]["properties"][param] = {
                    "type": "string",
                    "description": f"参数: {param}"
                }
            tools.append(tool_schema)
        # 为避免超出模型上限，这里只提取最重要的几个核心工具，或者你可以去除限制
        core_tools = ["nmap", "nuclei", "sqlmap", "ffuf", "hydra", "msfconsole"]
        return [t for t in tools if t["function"]["name"] in core_tools]

    def run_automated_test(self, target: str, model: str = "gpt-4", progress_callback=None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行基于 Agentic Workflow 的自主渗透测试
        """
        logger.info(f"🚀 开始自主智能体自动化测试: {target}")

        test_session = {
            "session_id": session_id,
            "target": target,
            "start_time": datetime.now().isoformat(),
            "stages": [],
            "results": [],
            "status": "running"
        }

        # 如果没有真实的大模型客户端，直接告警并返回错误，不再使用粗糙的硬编码流水线
        if not self.ai_analyzer.openai_client:
            error_msg = "缺少有效的 API Key。请配置大模型后启用真正的 Agent 自主测试。"
            logger.error(error_msg)
            test_session["status"] = "failed"
            test_session["error"] = error_msg
            if progress_callback:
                progress_callback("error", "failed", error_msg)
            self.test_history.append(test_session)
            return test_session

        try:
            if progress_callback:
                progress_callback("analysis", "running", "【AI Agent 初始化】")
            
            client = self.ai_analyzer.openai_client
            tools = self._get_tools_schema()
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "【身份设定】\n"
                        "你是 Caelum 智能渗透测试平台(Caelum v8.0)核心的「特权自主红队架构师 Agent (Autonomous Red Team AI)」。你的核心职能是深入剖析复杂的网络环境(包含但不限于 Bugku PAR, 本地物理隔离区, 或多层级 DMZ)，主导多阶段深度渗透战役。\n\n"
                        "【核心行动法则 (Core Directives) —— 必须无条件遵守】\n"
                        "1. **[授权边界与防御控制]**：收到目标指令后，必须立刻确认资产范围归属。如果是明显的高危公有云基础设施或非自管代码库/网站，必须中止并拒绝。若为代码仓库地址，只进行纯理论或静态审计，绝对禁止任何主动网络包探测！任何超出边界的行为均不被允许。\n"
                        "2. **[双重验证逻辑与极低误报执行标准 (Double Verification & Zero-Hallucination)]**：你的每一个断言、结论都必须 100% 建立在终端工具真实的 `stdout`/`stderr` 基础上。严禁「想象」。**【关键要求】为了达成极低误报率（≤5%），对 Nuclei/Nmap 等漏洞扫描工具报出的疑似、中低危漏洞，绝对不能立即确认为“真漏洞”！必须自主选择 Exploit Payload / 攻击脚本进行“第二维度打穿验证”。** 只有当 Payload 真实回显特定执行输出（如 `uid=0`, 特定用户甚至特定报错回显等不可伪造的特征）后，才允许判为真漏洞。如果仅仅是漏扫报出、但无法被成功利用或返回空白的，一律标记为『疑似但未成功 (False Positive)』予以抛弃与剔除，实战「未成功证实的，一律视为推测或失败」。\n"
                        "3. **[链路复用与内网穿透隧道 (Lateral Movement & Proxy Pivoting)]**：展现高级战术意图！当你通过首个 Web Shell 后，若发现当前机器可访问其他内网网段 (例如发现 Bugku PAR 中的内部网段，如 `192.168.0.x`)，你必须：①通过 Webshell 在靶机上使用 `chisel` / `frp` 或开启动态端口转发，②**在随后所有的工具调用参数 params 中，必须额外加上 `\"use_proxychains\": true` 字段！** 框架会自动为你挂载 proxychains 隧道。这才能实现多节点“套娃”式穿透。\n"
                        "4. **[高并发与极速扫描策略 (Efficiency & Fast Scanning)]**：目标必须在 15 分钟内完成测试！**绝不允许**执行 `nmap -p-` 全端口或大字典全目录扫描。必须使用高并发、极速探测方案（如 `nmap -F --min-rate 10000`、`--top-ports 100` 或 `ffuf` 极小核心字典）。**一旦发现高价值暴露面（如 80 端口有个 Tomcat），立即终止耗时的盲扫，立刻切入针对性突破与弱口令攻击阶段**，实现“部分结果即时阻断判定”。\n"
                        "5. **[自动化决策与工具链调度 (TTPs Chaining)]**：你在15步循环的循环思考(`Thought`)内，必须严谨规划：在侦查(Recon)->漏洞识别(Scanner)->打点利用(Exploit)->后门及扩展(Post/Lateral)这四大阶段中，你应当灵活调用各类授权的渗透工具。\n"
                        "6. **[OPSEC 与免责输出 (Legal OPSEC)]**：整个作战评估应极具专业、干练的高级分析师语态呈现事实证据（附带返回的原始指纹）。最后递交的终极审查报告开头必须印有明确的合规免责声明，重申授权模拟攻防的性质。\n\n"
                        "💡 不断提出大胆的阶段测试假设，利用现成的安全工具列表不断证伪或确定靶标链路的安全风险。直到无可探测面时，提交详细闭环安全研究战报。"
                    )
                },
                {"role": "user", "content": f"本次评估的目标为: {target}。请结合多阶段复杂测试思路进行渗透评估或漏洞扫描。"}
            ]
            
            agent_max_steps = 15
            current_step = 0
            
            while current_step < agent_max_steps:
                current_step += 1
                logger.info(f"🧠 Agent 思考中 (Step {current_step}/{agent_max_steps})...")
                if progress_callback:
                    # 借用不同的UI阶段名呈现进度
                    stage_name = "recon" if current_step <= 2 else "scan" if current_step <= 5 else "exploit"
                    progress_callback(stage_name, "running", f"AI Agent 决策中... (步骤 {current_step})")

                response = client.chat.completions.create(
                    model="deepseek-chat",  # 强行指定模型，因为目前绑定的 API 是 DeepSeek
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
                
                ai_msg = response.choices[0].message
                
                # openai >= 1.0 的 message 对象可转为 Dict，或者直接 append 都可以
                messages.append(ai_msg)
                
                # 如果没有调用工具，说明 AI 认为测试结束或者做出了总结
                if not ai_msg.tool_calls:
                    logger.info("✅ Agent 决策完成，给出最终总结。")
                    test_session["report"] = ai_msg.content
                    break
                    
                # 否则执行工具
                for tool_call in ai_msg.tool_calls:
                    tool_name = tool_call.function.name
                    args_dict = json.loads(tool_call.function.arguments)
                    logger.info(f"🛠️ Agent 决定执行工具: {tool_name} with params {args_dict}")
                    
                    if progress_callback:
                        progress_callback(stage_name, "running", f"执行工具: {tool_name}")
                        
                    # 调用本地框架工具
                    tool_res = self.tool_framework.execute_tool(tool_name.replace("_", "-"), args_dict)
                    
                    # 放入历史
                    test_session["stages"].append({
                        "stage": f"Agent Step {current_step}: {tool_name}",
                        "params": args_dict,
                        "result": tool_res.get("stdout", "无输出"),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # 返回结果给大模型
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_res.get("stdout", "Execute Failed/Error"))
                    })
            
            # 生成报告
            if progress_callback:
                progress_callback("report", "running", "自动生成终极战报")
            
            # 如果是因为达到最大步骤跳出，强制让它总结
            if current_step >= agent_max_steps and test_session.get("report") is None:
                messages.append({
                    "role": "user", 
                    "content": "测试结束。请基于前面步骤中**所有工具的真实完整返回结果**，生成本次最终的安全评估Markdown报告。\n"
                               "**强制要求**：\n"
                               "1. 绝不允许使用占位符、没有原始 stdout 支撑的过程推断、编造的 CVE ID 和漏洞。\n"
                               "2. 如果工具报错、失败、未发现端口/服务，照实描述『扫描失败』或『无漏洞』。\n"
                               "3. 如果目标是如 GitHub 仓库或不允许的公共 SaaS，必须在开头写明『超出被授权主动扫描的范围』，并且后续不得报告主动扫描漏洞结果。\n"
                               "4. 尾部必须包含明确的『未经授权系统严禁探测』的强制合法合规免责声明。\n"
                               "5. 对于复杂的渗透场景（如 Bugku PAR），报告中必须清晰展现“多阶段/多层级”测试的智能决策流。明确列出【Phase 1: 外网边界突破】、【Phase 2: 内网信息搜集】、【Phase 3: 横向移动】等结构，体现系统在多节点和依赖环境下的自动化组织能力。"
                })
                final_res = client.chat.completions.create(model="deepseek-chat", messages=messages)
                test_session["report"] = final_res.choices[0].message.content

            test_session["status"] = "completed"
            test_session["end_time"] = datetime.now().isoformat()

            if progress_callback:
                progress_callback("report", "completed", "报告生成完成")
                
            self.test_history.append(test_session)
            return test_session

        except Exception as e:
            logger.error(f"自动化测试(Agent)失败: {str(e)}")
            test_session["status"] = "failed"
            test_session["error"] = str(e)
            if progress_callback:
                progress_callback("error", "failed", str(e))
                
        self.test_history.append(test_session)
        return test_session


    def run_post_exploitation_agent(self, state_machine: PenetrationState, session_id: str, max_steps: int = 5) -> Dict[str, Any]:
        """后渗透自动化 Agent 循环（多阶段链式攻击核心）"""
        logger.info(f"🚀 开始后渗透链式攻击循环, 目标: {state_machine.target_ip}, 会话: {session_id}")
        
        client = openai.OpenAI(
            api_key=self.ai_analyzer.deepseek_api_key, 
            base_url="https://api.deepseek.com"
        )
        
        messages = [{
            "role": "system",
            "content": "你是 Caelum 后渗透阶段的 Red Team 智能体。目标已被初步控制。你当前可以通过 webshell 发送命令。\n"
                       "每次决策请务必返回合法的 JSON 格式，如下所示：\n"
                       "{\n"
                       '  "reasoning": "分析当前权限，认为需要...",\n'
                       '  "action": "command_exec" | "upload_exploit" | "finish",\n'
                       '  "payload": "具体命令或EXP利用参数"\n'
                       "}\n"
                       "禁止回复任何不在 JSON 中的多余文字！"
        }]
        
        step_results = []
        
        for step in range(max_steps):
            # 将当前渗透进度同步给 AI
            current_state = state_machine.to_json()
            messages.append({
                "role": "user",
                "content": f"当前状态机进度：{current_state}\n当前会话ID：{session_id}\n"
                           f"第 {step+1} 步，请下发下一步指令 JSON："
            })
            
            try:
                # 请求大模型
                response = client.chat.completions.create(model="deepseek-chat", messages=messages)
                ai_text = response.choices[0].message.content
                
                # 清洗 JSON
                clean_json_str = ai_text.replace("```json", "").replace("```", "").strip()
                ai_decision = json.loads(clean_json_str)
                
                action = ai_decision.get("action")
                payload = ai_decision.get("payload")
                reasoning = ai_decision.get("reasoning")
                
                logger.info(f"🧠 [后渗透 AI] 决策: {action} - 原因: {reasoning}")
                step_results.append({"step": step+1, "decision": ai_decision})
                
                # 执行逻辑
                if action == "command_exec":
                    output = self.session_manager.execute_command(session_id, payload)
                    logger.info(f"💻 [Session] 执行: {payload} \\n -> 结果: {output[:100]}...")
                    messages.append({
                        "role": "assistant",
                        "content": json.dumps(ai_decision)
                    })
                    messages.append({
                        "role": "user",
                        "content": f"命令 `{payload}` 执行结果:\n{output}"
                    })
                    # 可以在这里更新状态机，比如抓到 ROOT 切换状态
                    if "uid=0(root)" in output or "NT AUTHORITY\\SYSTEM" in output:
                        state_machine.current_stage = "RootAccess"
                        
                elif action == "upload_exploit":
                    # 模拟提权或传马操作
                    logger.info(f"🚀 发送提权代码/载荷: {payload[:50]}...")
                    output = self.session_manager.execute_command(session_id, payload)
                    messages.append({
                        "role": "assistant",
                        "content": json.dumps(ai_decision)
                    })
                    messages.append({
                        "role": "user",
                        "content": f"EXP执行结果:\n{output}"
                    })
                    
                elif action == "finish":
                    logger.info(f"✅ 后渗透任务由 AI 判定完成: {reasoning}")
                    break
                    
            except Exception as e:
                logger.error(f"❌ 后渗透循环出错: {e}")
                break
                
        return {
            "status": "completed",
            "target": state_machine.target_ip,
            "final_stage": state_machine.current_stage,
            "steps_taken": step_results
        }