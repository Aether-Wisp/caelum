#!/usr/bin/env python3
"""
Caelum Unified Tools Framework
统一工具执行框架 - 消除冗余，提高效率
"""

import logging
import subprocess
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    """工具分类"""
    NETWORK_SCAN = "network_scan"
    WEB_SCAN = "web_scan"
    VULN_SCAN = "vuln_scan"
    EXPLOITATION = "exploitation"
    ENUMERATION = "enumeration"
    BRUTE_FORCE = "brute_force"
    POST_EXPLOITATION = "post_exploitation"
    BINARY_ANALYSIS = "binary_analysis"
    CLOUD_SECURITY = "cloud_security"
    FORENSICS = "forensics"
    RECON = "recon"

@dataclass
class ToolConfig:
    """工具配置"""
    name: str
    category: ToolCategory
    command_template: str
    description: str
    required_params: list
    optional_params: list
    platforms: list  # ["linux", "windows", "all"]
    
class UnifiedToolFramework:
    """统一工具执行框架 - 所有工具通过此框架执行"""
    
    def __init__(self):
        self.tools: Dict[str, ToolConfig] = {}
        self.execution_cache = {}
        self._register_tools()
    
    def _register_tools(self):
        """注册所有支持的工具"""
        
        # 内网隧道穿透工具 (FRP/Chisel)
        self.register_tool(ToolConfig(
            name="frp",
            category=ToolCategory.POST_EXPLOITATION,
            command_template="frpc -c {config_path} {args}",
            description="内网穿透 FRP 客户端启动",
            required_params=["config_path"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))

        self.register_tool(ToolConfig(
            name="chisel",
            category=ToolCategory.POST_EXPLOITATION,
            command_template="chisel client {server_url} {tunnel_mapping} {args}",
            description="Chisel 快速内网穿透隧道建立",
            required_params=["server_url", "tunnel_mapping"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        # 网络扫描工具 (10+)
        self.register_tool(ToolConfig(
            name="nmap",
            category=ToolCategory.NETWORK_SCAN,
            command_template="nmap {scan_type} {target} {ports} {args}",
            description="通用网络扫描工具",
            required_params=["target"],
            optional_params=["scan_type", "ports", "timing", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="masscan",
            category=ToolCategory.NETWORK_SCAN,
            command_template="masscan {target} -p {ports} --rate {rate} {args}",
            description="高速端口扫描",
            required_params=["target"],
            optional_params=["ports", "rate", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="rustscan",
            category=ToolCategory.NETWORK_SCAN,
            command_template="rustscan -a {target} -- {args}",
            description="超快速端口扫描",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="autorecon",
            category=ToolCategory.NETWORK_SCAN,
            command_template="autorecon {target} {args}",
            description="自动化侦察框架",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="naabu",
            category=ToolCategory.NETWORK_SCAN,
            command_template="naabu -host {target} {args}",
            description="快速端口扫描和主机发现",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="unicornscan",
            category=ToolCategory.NETWORK_SCAN,
            command_template="unicornscan {target}:{ports} {args}",
            description="异步网络扫描器",
            required_params=["target"],
            optional_params=["ports", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="zmap",
            category=ToolCategory.NETWORK_SCAN,
            command_template="zmap -p {port} {target} {args}",
            description="互联网规模扫描器",
            required_params=["port"],
            optional_params=["target", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="smap",
            category=ToolCategory.NETWORK_SCAN,
            command_template="smap -i {interface} {target} {args}",
            description="简单快速的端口扫描器",
            required_params=["target"],
            optional_params=["interface", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="sx",
            category=ToolCategory.NETWORK_SCAN,
            command_template="sx {target} {args}",
            description="快速端口扫描和抓取",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="netdiscover",
            category=ToolCategory.NETWORK_SCAN,
            command_template="netdiscover -r {range} {args}",
            description="主动/被动ARP侦察工具",
            required_params=["range"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        # Web应用工具 (15+)
        self.register_tool(ToolConfig(
            name="gobuster",
            category=ToolCategory.WEB_SCAN,
            command_template="gobuster dir -u {url} -w {wordlist} -t {threads} {args}",
            description="目录枚举工具",
            required_params=["url"],
            optional_params=["wordlist", "threads", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="feroxbuster",
            category=ToolCategory.WEB_SCAN,
            command_template="feroxbuster -u {url} -w {wordlist} {args}",
            description="递归内容发现工具",
            required_params=["url"],
            optional_params=["wordlist", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="ffuf",
            category=ToolCategory.WEB_SCAN,
            command_template="ffuf -u {url} -w {wordlist} {args}",
            description="快速Web模糊测试工具",
            required_params=["url"],
            optional_params=["wordlist", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="dirbuster",
            category=ToolCategory.WEB_SCAN,
            command_template="dirbuster -u {url} -l {wordlist} {args}",
            description="Web内容扫描器",
            required_params=["url"],
            optional_params=["wordlist", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="dirb",
            category=ToolCategory.WEB_SCAN,
            command_template="dirb {url} {wordlist} {args}",
            description="Web内容扫描器",
            required_params=["url"],
            optional_params=["wordlist", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="dirsearch",
            category=ToolCategory.WEB_SCAN,
            command_template="dirsearch -u {url} -w {wordlist} {args}",
            description="Web路径扫描器",
            required_params=["url"],
            optional_params=["wordlist", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="katana",
            category=ToolCategory.WEB_SCAN,
            command_template="katana -u {url} {args}",
            description="下一代爬虫，支持JavaScript",
            required_params=["url"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="hakrawler",
            category=ToolCategory.WEB_SCAN,
            command_template="hakrawler -url {url} {args}",
            description="快速Web端点发现和爬取",
            required_params=["url"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="gau",
            category=ToolCategory.WEB_SCAN,
            command_template="gau {domain} {args}",
            description="从多个来源获取所有URL",
            required_params=["domain"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="waybackurls",
            category=ToolCategory.WEB_SCAN,
            command_template="waybackurls {domain} {args}",
            description="从Wayback Machine获取历史URL",
            required_params=["domain"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="nuclei",
            category=ToolCategory.VULN_SCAN,
            command_template="nuclei -u {target} -t {template_path} {args}",
            description="现代漏洞扫描框架",
            required_params=["target"],
            optional_params=["template_path", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="nikto",
            category=ToolCategory.WEB_SCAN,
            command_template="nikto -h {target} {args}",
            description="Web漏洞扫描",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="sqlmap",
            category=ToolCategory.WEB_SCAN,
            command_template="sqlmap -u {url} {args}",
            description="SQL注入检测",
            required_params=["url"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="wpscan",
            category=ToolCategory.WEB_SCAN,
            command_template="wpscan --url {url} {args}",
            description="WordPress安全扫描器",
            required_params=["url"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="arjun",
            category=ToolCategory.WEB_SCAN,
            command_template="arjun -u {url} {args}",
            description="HTTP参数发现",
            required_params=["url"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        # 枚举工具 (8+)
        self.register_tool(ToolConfig(
            name="enum4linux",
            category=ToolCategory.ENUMERATION,
            command_template="enum4linux-ng {target} {args}",
            description="SMB枚举工具",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="smbmap",
            category=ToolCategory.ENUMERATION,
            command_template="smbmap -H {target} {args}",
            description="SMB共享映射",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="bloodhound",
            category=ToolCategory.ENUMERATION,
            command_template="bloodhound-python -c {collection} -u {username} -p {password} -d {domain} {args}",
            description="Active Directory枚举",
            required_params=["collection", "username", "password", "domain"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="responder",
            category=ToolCategory.ENUMERATION,
            command_template="responder -I {interface} {args}",
            description="LLMNR/NBT-NS/mDNS中毒",
            required_params=["interface"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        # 暴力破解工具 (8+)
        self.register_tool(ToolConfig(
            name="hydra",
            category=ToolCategory.BRUTE_FORCE,
            command_template="hydra -l {username} -P {password_file} {target} {service} {args}",
            description="暴力破解工具",
            required_params=["target", "service"],
            optional_params=["username", "password_file", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="medusa",
            category=ToolCategory.BRUTE_FORCE,
            command_template="medusa -h {target} -u {username} -P {password_file} -M {module} {args}",
            description="快速并行模块化登录暴力破解器",
            required_params=["target", "module"],
            optional_params=["username", "password_file", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="patator",
            category=ToolCategory.BRUTE_FORCE,
            command_template="patator {module} {args}",
            description="多用途暴力破解器",
            required_params=["module"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="hashcat",
            category=ToolCategory.BRUTE_FORCE,
            command_template="hashcat -m {hash_type} {hash_file} {wordlist} {args}",
            description="GPU加速密码恢复",
            required_params=["hash_file"],
            optional_params=["hash_type", "wordlist", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="john",
            category=ToolCategory.BRUTE_FORCE,
            command_template="john {hash_file} {args}",
            description="高级密码哈希破解",
            required_params=["hash_file"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        # 漏洞扫描工具 (10+)
        self.register_tool(ToolConfig(
            name="jaeles",
            category=ToolCategory.VULN_SCAN,
            command_template="jaeles scan -u {url} -s {signatures} {args}",
            description="高级漏洞扫描",
            required_params=["url"],
            optional_params=["signatures", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="subjack",
            category=ToolCategory.VULN_SCAN,
            command_template="subjack -w {wordlist} -t {threads} -o {output} {args}",
            description="子域接管漏洞检查器",
            required_params=["wordlist"],
            optional_params=["threads", "output", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="wfuzz",
            category=ToolCategory.VULN_SCAN,
            command_template="wfuzz -c -z file,{wordlist} {url} {args}",
            description="Web应用模糊器",
            required_params=["url"],
            optional_params=["wordlist", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="dalfox",
            category=ToolCategory.VULN_SCAN,
            command_template="dalfox url {url} {args}",
            description="高级XSS漏洞扫描",
            required_params=["url"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="wafw00f",
            category=ToolCategory.VULN_SCAN,
            command_template="wafw00f {url} {args}",
            description="Web应用防火墙指纹识别",
            required_params=["url"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="testssl",
            category=ToolCategory.VULN_SCAN,
            command_template="testssl.sh {target} {args}",
            description="SSL/TLS配置测试",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="sslscan",
            category=ToolCategory.VULN_SCAN,
            command_template="sslscan {target} {args}",
            description="SSL/TLS密码套件枚举",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="sslyze",
            category=ToolCategory.VULN_SCAN,
            command_template="sslyze {target} {args}",
            description="SSL/TLS配置分析器",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        # 二进制分析工具 (15+)
        self.register_tool(ToolConfig(
            name="gdb",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="gdb {binary} {args}",
            description="GNU调试器",
            required_params=["binary"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="radare2",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="r2 -A {binary} {args}",
            description="高级逆向工程框架",
            required_params=["binary"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="ghidra",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="ghidra {project} {binary} {args}",
            description="NSA软件逆向工程套件",
            required_params=["binary"],
            optional_params=["project", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="ida_free",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="ida {binary} {args}",
            description="交互式反汇编器",
            required_params=["binary"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="binwalk",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="binwalk {file} {args}",
            description="固件分析和提取工具",
            required_params=["file"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="ropgadget",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="ROPgadget --binary {binary} {args}",
            description="ROP/JOP小工具查找器",
            required_params=["binary"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="checksec",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="checksec --file {binary} {args}",
            description="二进制安全属性检查器",
            required_params=["binary"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="strings",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="strings {binary} {args}",
            description="从二进制中提取可打印字符串",
            required_params=["binary"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="objdump",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="objdump -d {binary} {args}",
            description="显示对象文件信息",
            required_params=["binary"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="readelf",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="readelf -a {binary} {args}",
            description="ELF文件分析器",
            required_params=["binary"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="xxd",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="xxd {file} {args}",
            description="十六进制转储工具",
            required_params=["file"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="volatility",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="volatility -f {memory_dump} {plugin} {args}",
            description="高级内存取证框架",
            required_params=["memory_dump", "plugin"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="msfvenom",
            category=ToolCategory.BINARY_ANALYSIS,
            command_template="msfvenom -p {payload} -f {format} {args}",
            description="Metasploit载荷生成器",
            required_params=["payload", "format"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        # 云安全工具 (10+)
        self.register_tool(ToolConfig(
            name="prowler",
            category=ToolCategory.CLOUD_SECURITY,
            command_template="prowler {provider} {args}",
            description="云安全评估",
            required_params=["provider"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="scout_suite",
            category=ToolCategory.CLOUD_SECURITY,
            command_template="scout {provider} {args}",
            description="多云安全审计",
            required_params=["provider"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="trivy",
            category=ToolCategory.CLOUD_SECURITY,
            command_template="trivy {target} {args}",
            description="容器和IaC漏洞扫描",
            required_params=["target"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="kube_hunter",
            category=ToolCategory.CLOUD_SECURITY,
            command_template="kube-hunter {args}",
            description="Kubernetes渗透测试",
            required_params=[],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="kube_bench",
            category=ToolCategory.CLOUD_SECURITY,
            command_template="kube-bench {args}",
            description="CIS Kubernetes基准检查",
            required_params=[],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        # CTF/取证工具 (10+)
        self.register_tool(ToolConfig(
            name="foremost",
            category=ToolCategory.FORENSICS,
            command_template="foremost -i {input} -o {output} {args}",
            description="文件雕刻和数据恢复",
            required_params=["input", "output"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="photorec",
            category=ToolCategory.FORENSICS,
            command_template="photorec {args}",
            description="文件恢复软件",
            required_params=[],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="testdisk",
            category=ToolCategory.FORENSICS,
            command_template="testdisk {args}",
            description="磁盘分区恢复和修复",
            required_params=[],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="scalpel",
            category=ToolCategory.FORENSICS,
            command_template="scalpel -c {config} {image} -o {output} {args}",
            description="文件雕刻工具",
            required_params=["image", "output"],
            optional_params=["config", "args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="bulk_extractor",
            category=ToolCategory.FORENSICS,
            command_template="bulk_extractor -o {output} {input} {args}",
            description="数字取证工具",
            required_params=["input", "output"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="autopsy",
            category=ToolCategory.FORENSICS,
            command_template="autopsy {args}",
            description="数字取证平台",
            required_params=[],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        # Bug Bounty工具 (10+)
        self.register_tool(ToolConfig(
            name="amass",
            category=ToolCategory.RECON,
            command_template="amass enum -d {domain} {args}",
            description="高级子域枚举",
            required_params=["domain"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="subfinder",
            category=ToolCategory.RECON,
            command_template="subfinder -d {domain} {args}",
            description="快速被动子域发现",
            required_params=["domain"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="httpx",
            category=ToolCategory.RECON,
            command_template="httpx -l {list} {args}",
            description="快速多用途HTTP工具包",
            required_params=["list"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="paramspider",
            category=ToolCategory.RECON,
            command_template="paramspider -d {domain} {args}",
            description="从Web档案中挖掘参数",
            required_params=["domain"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="aquatone",
            category=ToolCategory.RECON,
            command_template="aquatone-discover -d {domain} {args}",
            description="跨主机的网站可视化检查",
            required_params=["domain"],
            optional_params=["args"],
            platforms=["linux"]
        ))
        
        self.register_tool(ToolConfig(
            name="theharvester",
            category=ToolCategory.RECON,
            command_template="theharvester -d {domain} -l {limit} -b {source} {args}",
            description="从多个来源收集邮箱和子域",
            required_params=["domain"],
            optional_params=["limit", "source", "args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="shodan",
            category=ToolCategory.RECON,
            command_template="shodan search {query} {args}",
            description="互联网连接设备搜索",
            required_params=["query"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        self.register_tool(ToolConfig(
            name="censys",
            category=ToolCategory.RECON,
            command_template="censys search {query} {args}",
            description="互联网资产发现",
            required_params=["query"],
            optional_params=["args"],
            platforms=["linux", "windows"]
        ))
        
        logger.info(f"✅ 已注册 {len(self.tools)} 个安全工具")
    
    def register_tool(self, config: ToolConfig):
        """注册新工具"""
        self.tools[config.name] = config
        logger.info(f"✅ Tool registered: {config.name}")
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        """
        统一的工具执行方法
        
        Args:
            tool_name: 工具名称
            params: 参数字典
            use_cache: 是否使用缓存
            
        Returns:
            执行结果
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "tool": tool_name
            }
        
        tool_config = self.tools[tool_name]
        
        # 验证必需参数
        missing_params = [p for p in tool_config.required_params if p not in params]
        if missing_params:
            return {
                "success": False,
                "error": f"Missing required parameters: {missing_params}",
                "tool": tool_name,
                "required_params": tool_config.required_params
            }
        
        # 构建命令
        command = self._build_command(tool_config, params)
        
        # 检查缓存
        cache_key = f"{tool_name}:{hash(str(sorted(params.items())))}"
        if use_cache and cache_key in self.execution_cache:
            logger.info(f"📦 Cache hit for {tool_name}")
            return self.execution_cache[cache_key]
        
        # 执行工具
        logger.info(f"🚀 Executing {tool_name}: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = {
                "success": result.returncode == 0,
                "tool": tool_name,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "description": tool_config.description
            }
            
            # 缓存结果
            if use_cache:
                self.execution_cache[cache_key] = output
            
            logger.info(f"✅ {tool_name} completed with code {result.returncode}")
            return output
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"{tool_name} execution timeout",
                "tool": tool_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    def execute_tool_chain(self, chain: list, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具链（多个工具按顺序执行）
        
        Args:
            chain: 工具名称列表 ["nmap", "nuclei", "sqlmap"]
            params: 共享参数
            
        Returns:
            所有工具的执行结果
        """
        results = []
        chain_params = params.copy()
        
        for tool_name in chain:
            logger.info(f"⛓️ Executing tool in chain: {tool_name}")
            result = self.execute_tool(tool_name, chain_params)
            results.append(result)
            
            # 后续工具可以使用前一个工具的结果
            chain_params[f"{tool_name}_result"] = result
        
        return {
            "success": all(r.get("success", False) for r in results),
            "chain": chain,
            "total_tools": len(chain),
            "results": results
        }
    
    def _build_command(self, config: ToolConfig, params: Dict[str, Any]) -> str:
        """构建完整的命令行"""
        # 准备参数
        cmd_params = {}
        
        # 添加必需参数
        for param in config.required_params:
            cmd_params[param] = params.get(param, "")
        
        # 添加可选参数
        for param in config.optional_params:
            if param in params:
                cmd_params[param] = params[param]
            else:
                cmd_params[param] = ""
        
        # 始终接收 use_proxychains 独立参数
        use_proxychains = params.get("use_proxychains", False)
        
        # 格式化命令
        try:
            command = config.command_template.format(**cmd_params)
            # 清理多余的空格
            command = " ".join(command.split())
            
            # 【测试效率进阶要求：极速扫描阻断】
            # 强制干预耗时较长的命令，替换为高并发/部分探测参数，以满足单目标≤15分钟的要求
            if config.name == "nmap":
                # 干掉超慢的全端口扫描
                command = command.replace("-p-", "--top-ports 1000")
                command = command.replace("-p 1-65535", "--top-ports 1000")
                # 强制要求极速最小发包率与 T4/T5 级别
                if "--min-rate" not in command:
                    command += " --min-rate 10000"
                if "-T" not in command:
                    command += " -T4"
                    
            elif config.name in ["ffuf", "dirsearch", "gobuster", "dirb"]:
                # 高并发目录扫描强制设置大线程与超时
                if " -t " not in command and " -threads " not in command:
                    command += " -t 200"
                # 对 ffuf 限制最大扫描时间(如120秒直接阶段性退出)
                if config.name == "ffuf" and "-maxtime" not in command:
                    command += " -maxtime 120"
                    
            elif config.name == "nuclei":
                # Nuclei增加并发数和限制重试，极大加快速度
                if " -c " not in command and " -concurrency " not in command:
                    command += " -c 100 -bs 100 -retries 1 -timeout 5"
            
            # 【高阶联动：自动使用 proxychains 内网穿透隧道】
            if use_proxychains or "proxychains" in str(params.get("args", "")):
                # 如果命令没有加上 proxychains
                if not command.startswith("proxychains"):
                    command = f"proxychains4 -q {command}"
            
            return command
        except KeyError as e:
            logger.error(f"❌ Missing parameter in command template: {e}")
            return ""
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """获取工具信息"""
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        
        config = self.tools[tool_name]
        return {
            "name": config.name,
            "category": config.category.value,
            "description": config.description,
            "required_params": config.required_params,
            "optional_params": config.optional_params,
            "platforms": config.platforms,
            "command_template": config.command_template
        }
    
    def list_tools(self, category: Optional[str] = None) -> list:
        """列出所有工具"""
        tools = list(self.tools.values())
        
        if category:
            tools = [t for t in tools if t.category.value == category]
        
        return [
            {
                "name": t.name,
                "category": t.category.value,
                "description": t.description
            }
            for t in tools
        ]
    
    def clear_cache(self):
        """清除缓存"""
        self.execution_cache.clear()
        logger.info("🧹 Tool execution cache cleared")

# 全局框架实例
tool_framework = UnifiedToolFramework()
