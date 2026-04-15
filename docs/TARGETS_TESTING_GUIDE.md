# Caelum 打靶测试指南：覆盖 Vulhub、Vulnhub 与 Bugku PAR

为了满足“高阶靶机环境适配”的竞赛要求，Caelum 系统已被设计为可以无缝对接当前主流的三大靶机平台。请按照本指南进行环境接入与自动化渗透测试。

## 1. 基础 Docker 靶场：Vulhub

Vulhub 是基于 Docker 的单节点漏洞环境集合，非常适合验证单一漏洞（如 CVE）的检测率和误报率。

- **环境搭建**：进入项目根目录下的 `vulhub/` 目录中对应的漏洞环境，执行 `docker-compose up -d` 即可。
- **打靶方式**：靶机启动后，直接在 Caelum 系统中输入 `http://127.0.0.1:端口` 进行自动化扫描与利用。

---

## 2. 虚拟机系统级靶机：Vulnhub

Vulnhub 提供的是完整的操作系统虚拟机镜像（通常为 `.ova` 格式），注重从提权到获取 Root Flag 的完整单机渗透流程。
由于镜像体积庞大（通常几个 GB），无法直接放在代码仓库中。

###接入与测试流程：

1. **下载与启动**：从 [Vulnhub官网](https://www.vulnhub.com/) 下载靶机镜像，导入 VMware 或 VirtualBox。
2. **网络配置**：将虚拟机的网络适配器设置为 **NAT 模式** 或 **桥接模式**，确保与运行 Caelum 的宿主机处于同一局域网内。
3. **资产发现（Caelum 介入）**：
   在 Caelum 系统中输入你所在的局域网段（例如 `192.168.1.0/24`），CAELUM 的底层的 `nmap` 和 `netdiscover` 会自动扫描出靶机的真实 IP。
4. **自动化提权**：CAELUM 会自动对其探测端口、寻找 Web 突破口、写入 Webshell，进而利用系统提权漏洞拿到最终的 root Flag。

---

## 3. 高阶多节点内网靶机：Bugku PAR

Bugku PAR (Penetration Active Range) 是一种基于云端的“多节点套娃”实战靶场，往往需要通过 VPN 接入，并且包含外网边界突破、内网横向移动等复杂场景。

### 接入与测试流程（结合 Caelum 内网穿透引擎）：

1. **连接 VPN**：
   从 Bugku 平台下载靶场专用的 `.ovpn` 配置证书。
   在 Caelum 的所处机器上运行：`openvpn --config your_bugku_par.ovpn`，连入靶场外围网络（例如获得一个 `10.10.x.x` 的 IP）。
2. **第一阶段：边界突破**：
   在 Caelum 平台输入 Bugku 提供给你的初始靶机 IP（通常是唯一的对外开放网站节点）。Caelum 会自动化攻破并获得这台机器的 WebShell。
3. **第二阶段：自动构建隧道 (Proxy Pivoting)**：
   Caelum 拿到第一层权限后，内部 AI Analyzer (结合状态机和 `use_proxychains` 功能) 会自动向靶场第一层节点注入 `chisel` 或 `frp`，并在后台**动态分配空闲监听端口**。
4. **第三阶段：内网横向移动**：
   隧道建立后，Caelum 的所有后续扫描命令都会被静默套上 `proxychains4`，从而直接透过第一台靶机，自动化扫描隐藏在 Bugku PAR 内网中的第二台、第三台设备，直至打穿整个靶场环境！

---

_注：进行外部靶机测试时，请确保你拥有所在网络和 Bugku 账号的合法访问授权。严禁使用 Caelum 对未授权目标进行扫描。_
