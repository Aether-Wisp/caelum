# Caelum 自动化渗透测试系统 - 教学实验指导手册

本教学文档旨在指导使用者从零开始，完成 Caelum 基于大模型的自动化渗透测试系统的部署与功能验证。文档包含了环境安装、操作步骤、预期实验结果以及相关注意事项。

---

## 一、 实验环境要求与准备

### 1.1 实验环境建议

为了保证各项自动化渗透测试引擎（如扫描器、Payload 生成、LLM 接口）稳定运行，以及本地靶场环境的顺利搭建，推荐配置如下：

- **操作系统**：Ubuntu 20.04/22.04 LTS (或 Linux 虚拟机环境)、macOS。暂不建议在纯 Windows 环境下直接运行底层扫描器（建议使用 WSL2 或 Linux 虚拟机）。
- **内存配置**：推荐 4GB 及以上（运行 Docker 靶场需要一定内存）。
- **网络环境**：能够正常访问外网（用于下载前端 CDN 静态资源、pip 依赖包以及调用云端大模型 API）。

### 1.2 必备软件依赖

- **Python**：3.8+ (用于运行 Caelum 核心工具与后端服务)
- **Docker & Docker Compose**：(用于一键启动项目及漏洞靶场环境)
- **Git**：(代码版本控制与拉取)

---

## 二、 所有的安装步骤

### 2.1 方案 A：Docker 容器化部署 (推荐，快速且可复现)

这是最简便的部署方式，系统内置了自动化构建脚本。

1. **获取项目代码**
   使用 Git 克隆或直接解压项目文件夹 `caelum` 到目标服务器/主机。

   ```bash
   cd caelum
   ```

2. **配置权限**
   确保启动脚本和安装脚本具备执行权限：

   ```bash
   chmod +x docker-entrypoint.sh install_tools.sh
   ```

3. **一键构建与启动**
   使用 Docker Compose 在后台构建并启动 Caelum 系统。此过程可能耗时几分钟，具体取决于网络。

   ```bash
   docker-compose up -d --build
   ```

4. **验证部署状态**
   ```bash
   docker-compose ps
   ```
   _状态显示为 `Up` 即表示 Caelum 核心服务启动成功。_

### 2.2 方案 B：本地物理机/虚拟环境部署 (适合调试开发)

1. **创建 Python 虚拟环境**

   ```bash
   python3 -m venv caelum_env
   source caelum_env/bin/activate  # Linux/macOS
   # Windows: .\caelum_env\Scripts\activate
   ```

2. **安装依赖与工具**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt

   # 执行工具安装脚本安装所需扫描器或环境依赖
   bash install_tools.sh
   ```

3. **模型 API 与系统配置**
   打开配置文件 `config/mcp_config.json`，在配置项中填入用于测试的大模型（如 DeepSeek、ChatGPT 或 Claude）的 API 密钥及接口地址。

4. **启动前端或服务**
   直接用浏览器打开前端文件 `HTML/01-caelum.html` 体验界面，或者如果您已经写好后端脚本（如 `app.py` ），请执行：
   ```bash
   python caelum_tools_framework.py
   ```

---

## 三、 实验步骤 (靶场与测试验证)

本实验将通过系统自带的 `geoserver` 漏洞靶场，验证 Caelum 系统的渗透测试与 Payload 生成能力。

### 第一步：启动漏洞靶场环境

在另一终端窗口中，进入项目自带的靶场目录，启动 Geoserver 漏洞环境（CVE-2024-36401）：

```bash
cd caelum/geoserver_CVE-2024-36401
docker-compose up -d
```

> _启动后，记录下靶场的 IP 地址和映射端口（假定靶场部署在本地 `127.0.0.1` 对应的端口）。_

### 第二步：访问系统前端控制台

打开浏览器，访问部署好的 Caelum 控制台 URL（如果是本地静态打开则是 `HTML/01-caelum.html`，如果是 Docker 部署则访问设定的公网 IP/端口）。

### 第三步：新建自动化测试任务

1. 在左侧导航栏点击 **“测试任务”**。
2. 在 **“测试目标”** 输入框中，输入刚才启动的靶场地址（例如：`127.0.0.1:8080`），点击 **“添加”**。
3. 在 **“测试模型选择”** 模块，选择一个驱动大模型（如 `DeepSeek`）。
4. 点击 **“开始测试”**。此时系统会模拟调用后端引擎进行自动侦察、漏洞探测及利用分析。

### 第四步：使用 Payload 生成器

1. 在左侧导航栏点击 **“Payload生成”**。
2. 在下拉框中选择想要生成的载荷类型（例如：命令注入 / OGNL 表达式等，取决于具体漏洞）。
3. 在 JSON 参数配置区，输入目标特性参数。
4. 点击 **“生成Payload”**，大模型将根据设定自动组装针对性的攻击载荷。

---

## 四、 预期结果

1. **界面交互结果**：
   - 提交测试任务后，“任务状态监控”模块的进度条应开始滚动，当前状态显示“运行中”。
   - “测试报告日志”控制台应能动态输出扫描进度，如提示发现某端口开放、发现特定漏洞等。
   - 任务完成后，系统弹出“测试完成”弹窗，提供简要漏洞统计，并展示“高危/中危/低危”数量的动态变化（更新到右下角图表）。
2. **Payload 预期**：
   - 在 Payload 生成页面，在配置参数并点击生成后，经过短暂停顿，下方文本框应能正确回显出类似 `union select ...` 或针对相关漏洞特制的命令执行 Payload。
3. **靶场交互结果（后端对接后）**：
   - 最终生成的测试报告能准确指出 Geoserver（CVE-2024-36401）或对应 Vulhub 容器的存在漏洞和验证方式。

---

## 五、 注意事项与安全声明

⚠️ **请务必认真阅读以下安全准则：**

1. **授权与合规性**：
   - 本套“Caelum自动化渗透测试系统”及其实验流程**仅供学术研究、教学演示与内部安全防御测试使用**。
   - **绝对禁止**将本系统用于未经明确授权的第三方网络、生产环境或公共互联网目标。擅自对外进行渗透测试属于违法行为。
2. **资源消耗说明**：
   - 云端大语言模型（LLM）的分析能力非常依赖 Token 开销，在进行大量目标侦察和深度漏洞分析时，会产生一定的 API 计费成本，请留意您的 API 账户余额。
   - 运行多个 Vulhub 靶场容器将占用较多服务器 CPU 与内存资源，实验完毕后请务必执行 `docker-compose down` 关闭靶场，释放资源。
3. **前端呈现限制**：
   - 当前阶段若没有完善好具体的 Python 爬虫和漏洞发包后端，前端面板的进度条与日志可能部分是基于 JavaScript 模拟反馈的，请在接通正式 API 接口后进行真实渗透测试的验证。
4. **网络通信**：
   - 如果部署在云服务器而非本地，请确认云安全组（防火墙）开启了必要的 Web 服务端口（80/443），而用于靶场的测试端口请**限制只允许自己的测试 IP 访问**，防止靶场被互联网上的真实黑客恶意利用。















这里是为您量身定制的 **Caelum 自动化渗透测试系统** 项目安装与部署指南。您可以将此内容保存到项目根目录下的 `INSTALL.md` 或直接覆盖 README.md 文件。

考虑到您的项目结构中同时包含了本地脚本（requirements.txt, install_tools.sh）和容器化配置（`Dockerfile`, docker-compose.yml），我为您整理了**本地开发测试**和**服务端容器化**两种主流部署方式。

---

# Caelum 自动化渗透测试系统 - 安装与部署指南

Caelum 是一款基于大语言模型（LLM）驱动的自动化渗透测试辅助系统，集成了自动化安全测试任务执行、Payload 智能生成、多模型协同（DeepSeek, ChatGPT, Claude）以及历史日志分析等功能。

## 📌 环境要求

在开始部署之前，请确保您的目标服务器或本地机器满足以下基础环境：
- **操作系统**：推荐使用 Ubuntu 20.04/22.04 LTS、CentOS 8 或 macOS（Windows 推荐使用 WSL2）。
- **Python 版本**：Python 3.8 及以上版本（如选择本地部署）。
- **容器环境**：Docker 及 Docker Compose V2（如选择容器化部署）。
- **网络要求**：如果需要调用云端大模型 API，请确保服务器具备正常访问对应 API（如 OpenAI、DeepSeek）的外网权限。

---

## 🚀 方式一：Docker 容器化一键部署（⭐ 推荐生产/公网环境）

使用 Docker 部署是获得**可复现公网地址**最快、最稳定的方式。所有依赖环境（包括核心工具和前后端分离服务）均已在镜像中配置完毕。

### 1. 克隆或上传项目代码
将整个代码仓库上传至您的云服务器（如 `/opt/caelum` 目录下）。
```bash
git clone <您的仓库地址> caelum
cd caelum
```

### 2. 赋予脚本执行权限
确保部署和启动脚本具有可执行权限：
```bash
chmod +x docker-entrypoint.sh
chmod +x install_tools.sh
```

### 3. 启动项目
通过 Docker Compose 拉取基础镜像、构建项目并放置于后台运行：
```bash
docker-compose up -d --build
```
> *首次启动时，Docker 会自动执行 `Dockerfile` 和 install_tools.sh 安装所需的渗透测试基础工具库和 Python 依赖。*

### 4. 验证服务状态
查看容器是否已经正常拉起：
```bash
docker-compose ps
```
查看后端服务的运行日志：
```bash
docker-compose logs -f
```

### 5. 访问系统
默认配置下，Web 服务启动后，打开浏览器访问：
```text
http://<您的服务器公网IP>
```
页面将自动加载 01-caelum.html 主控制台。

---

## 💻 方式二：本地开发环境部署（适合二次开发与调试）

如果您需要修改前端页面或调整后端 Python 测试逻辑，推荐使用本地物理机环境进行部署。

### 1. 准备 Python 虚拟环境
在项目根目录下创建一个专用的独立虚拟环境，防止依赖冲突：
```bash
python3 -m venv caelum_env

# 激活虚拟环境 (Linux/macOS)
source caelum_env/bin/activate
# 激活虚拟环境 (Windows PowerShell)
.\caelum_env\Scripts\Activate.ps1
```

### 2. 安装 Python 核心依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 环境初始化与工具安装
运行项目准备的自动化工具包安装脚本（主要适用于 Linux/macOS 环境下扫描器的安装依赖）：
```bash
bash install_tools.sh
```

### 4. 配置文件确认
检查 mcp_config.json 文件，根据需要填入大模型 API 密钥或配置扫描引擎参数。

### 5. 运行服务
如果是纯前端调试，直接使用浏览器或者 Live Server 打开 01-caelum.html 即可。
如果已经接入了后端的接口框架，则启动主 Python 进程：
```bash
python caelum_tools_framework.py
# 或对应的后端入口 app.py / serve.py
```

---

## 🎯 附加说明：漏洞靶场环境 (Vulhub/Geoserver)

系统根目录下附带了 vulhub 和 geoserver_CVE-2024-36401 目录，这是为 Caelum 准备的**漏洞验证靶场**。

当需要测试本系统的扫描与 Payload 模块时，可以进入对应漏洞目录独立开启靶场：
```bash
cd geoserver_CVE-2024-36401
docker-compose up -d
```
在测试任务中，将目标 IP 指向此靶场的 IP 和映射端口，即可安全地开展漏洞复现演练。

---

**常见问题排查**：
* **前端图标不显示**：请确认所处环境是否拦截了 `cdn.tailwindcss.com` 和 `iconify-icon` 相关的外网 CDN 请求。
* **Docker 启动无休止重启或报错退出**：请检查 docker-entrypoint.sh 的行尾换行符是否格式正常（推荐转为 `LF` 而不是 `CRLF`，可通过 `dos2unix docker-entrypoint.sh` 转换）。
