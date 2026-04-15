# Caelum v8.0 - 快速部署指南

## 🚀 最快的方式（推荐）

### 只需 2 条命令！

```bash
# 1. 启动 Docker Compose
docker-compose up -d

# 2. 在浏览器打开
http://localhost:8888
```

✨ **完成！** 所有 74 个安全工具都已自动集成。

---

## 部署方案对比

| 方案               | 难度            | 时间       | 工具完整度 | 跨平台            |
| ------------------ | --------------- | ---------- | ---------- | ----------------- |
| **Docker Compose** | ⭐ 简单         | 5 分钟     | 100% ✅    | Windows/Mac/Linux |
| **启动脚本**       | ⭐⭐ 中等       | 10-15 分钟 | 90% ✅     | Linux/Mac         |
| **自动化安装**     | ⭐⭐⭐ 复杂     | 20-30 分钟 | 95% ✅     | Linux 优先        |
| **手动安装**       | ⭐⭐⭐⭐ 很复杂 | 1-2 小时   | 80% ⚠️     | 取决于系统        |

---

## 方案 1: Docker Compose（推荐 ⭐⭐⭐⭐⭐）

### 前置条件

- 已安装 Docker 和 Docker Compose

### 步骤

1. **配置 API 密钥（可选）**

```bash
# 编辑 docker-compose.yml 或直接设置环境变量
export DEEPSEEK_API_KEY="sk-xxx"
export OPENAI_API_KEY="sk-xxx"
```

2. **一键启动**

```bash
docker-compose up -d
```

3. **访问系统**

```
http://localhost:8888
```

4. **查看日志**

```bash
docker-compose logs -f caelum
```

5. **停止系统**

```bash
docker-compose down
```

### 优点

- ✅ 自动安装所有 74 个工具
- ✅ 无系统依赖冲突
- ✅ 跨平台完全兼容（Windows/Mac/Linux）
- ✅ 一键启动和停止
- ✅ 生产级配置

### 缺点

- ⚠️ 需要预装 Docker（但现代系统都有）

---

## 方案 2: 启动脚本（快速简单）

### Windows

```batch
REM 1. 双击运行
start.bat

REM 或在 PowerShell 中
.\start.bat
```

### Linux/Mac

```bash
# 1. 赋予执行权限
chmod +x start.sh

# 2. 运行
./start.sh
```

脚本会自动：

- ✅ 创建虚拟环境
- ✅ 安装 Python 依赖
- ✅ 配置 .env 文件
- ✅ 启动服务器

### 访问

```
http://localhost:8888
```

### 优点

- ✅ 一键启动
- ✅ 自动配置虚拟环境
- ✅ 适合快速开发

### 缺点

- ⚠️ 外部工具需要手动安装
- ⚠️ 某些工具仅在 Linux/Mac 上可用

---

## 方案 3: 自动化工具安装

### Linux/Mac

```bash
# 自动检测系统并安装所有工具
chmod +x install_tools.sh
./install_tools.sh
```

### 支持的系统

- ✅ Ubuntu/Debian
- ✅ Kali Linux
- ✅ CentOS/RHEL
- ✅ macOS

### 访问

```
http://localhost:8888
```

### 优点

- ✅ 完全自动化
- ✅ 支持多种 Linux 发行版
- ✅ 工具完整度高（95%）

### 缺点

- ⚠️ Windows 不直接支持（需要 WSL2）
- ⚠️ 某些工具需要编译（时间较长）
- ⚠️ 可能需要 sudo 权限

---

## 方案 4: 手动配置（适合定制）

### 步骤 1：创建虚拟环境

```bash
python3 -m venv caelum_env
source caelum_env/bin/activate  # Linux/Mac
# 或
caelum_env\Scripts\activate  # Windows
```

### 步骤 2：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 3：配置 API 密钥

创建 `.env` 文件：

```
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
```

### 步骤 4：安装外部工具

**Kali Linux（最简单）**

```bash
# 大多数工具已预装
sudo apt update && sudo apt upgrade -y
```

**Ubuntu/Debian**

```bash
# 安装关键工具
sudo apt install -y nmap sqlmap nuclei ffuf gobuster hydra hashcat
```

**macOS**

```bash
brew install nmap sqlmap ffuf gobuster hydra hashcat binwalk radare2
```

### 步骤 5：启动服务器

```bash
python caelum_server.py
```

### 访问

```
http://localhost:8888
```

---

## 📊 工具加载验证

启动后查看已加载的工具：

```bash
# API 查询
curl http://localhost:8888/api/tools/list

# 服务器日志中会显示
# ✅ Tool registered: nmap
# ✅ Tool registered: nuclei
# ... 等等
```

---

## 🔧 故障排除

### 问题：无法连接到 localhost:8888

**解决方案：**

```bash
# 检查服务器是否运行
docker ps  # 查看容器状态

# 检查端口
netstat -an | grep 8888

# 查看日志
docker-compose logs caelum
```

### 问题：工具显示"未安装"

**解决方案：**

1. 确保使用了正确的部署方案（Docker 最简单）
2. 对于非 Docker 部署，手动安装缺失的工具
3. 使用 `/api/tools/list` 检查已加载的工具

### 问题：API 密钥不生效

**解决方案：**

```bash
# 检查 .env 文件
cat .env

# 或检查环境变量
echo $DEEPSEEK_API_KEY
echo $OPENAI_API_KEY
```

---

## 推荐流程

1. **最快体验**：使用 Docker Compose（推荐）
2. **快速开发**：使用启动脚本
3. **定制需求**：使用自动化安装脚本
4. **学习用途**：手动配置

---

## 常见问题 FAQ

**Q: 我应该选择哪个方案？**

A:

- 想要最快体验？→ **Docker Compose**
- 想要方便启动？→ **启动脚本**
- 想要完全定制？→ **手动配置**

**Q: 没有 Docker 能运行吗？**

A: 可以，使用启动脚本（`.bat` 或 `.sh`）或手动配置。

**Q: Windows 怎么安装外部工具？**

A:

- 使用 Docker（简单）
- 使用 WSL2 + Ubuntu（推荐）
- 从官方网站下载工具二进制文件

**Q: 能在我的服务器上运行吗？**

A: 可以，所有方案都支持服务器部署。推荐使用 Docker Compose。

---

## 获取帮助

- 📖 查看完整 README：[README_zh.md](README_zh.md)
- 🐛 提交 Issue（如遇问题）
- 📧 联系技术支持

---

**现在就开始吧！** 🚀 选择你喜欢的方案，5 分钟内即可运行完整的渗透测试系统！
