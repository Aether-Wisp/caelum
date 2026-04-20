import os

files = {
    r'd:\1-compitition\waibao\caelum\src\caelum\static\js\caelum.js': r'''document.addEventListener("DOMContentLoaded", () => {
  const navItems = document.querySelectorAll(".nav-item");
  const mainContent = document.querySelector("main");
  const pageTitle = document.querySelector("#page-title");

  // Api config
  const API_BASE = "/api";
  async function apiFetch(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, options);
      if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
      return await response.json();
    } catch (err) {
      console.warn("API Error (using mock fallback):", err);
      // Return mock data if real API is missing to avoid crashing UI completely
      return null;
    }
  }

  // --- Navigation ---
  navItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const page = item.getAttribute("href").substring(1);
      navItems.forEach((i) => i.classList.remove("active", "bg-[#E8F3FF]", "text-[#1677FF]", "font-medium", "shadow-[inset_3px_3px_6px_rgba(22,119,255,0.1),inset_-3px_-3px_6px_rgba(255,255,255,0.7)]"));
      item.classList.add("active", "bg-[#E8F3FF]", "text-[#1677FF]", "font-medium", "shadow-[inset_3px_3px_6px_rgba(22,119,255,0.1),inset_-3px_-3px_6px_rgba(255,255,255,0.7)]");
      loadPageContent(page);
    });
  });

  async function loadPageContent(page) {
    try {
      let url = "", title = "";
      switch (page) {
        case "test-tasks": url = "/HTML/01-test-tasks-content.html"; title = "安全测试任务"; break;
        case "payload-generator": url = "/HTML/02-payload-caelum.html"; title = "Payload 生成器"; break;
        case "history-logs": url = "/HTML/03-history-logs.html"; title = "历史日志"; break;
        default: return;
      }
      mainContent.innerHTML = `<div class="neu-card p-6 flex justify-center items-center h-48"><iconify-icon icon="lucide:loader-2" class="animate-spin text-3xl text-[#1677FF]"></iconify-icon></div>`;
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const html = await response.text();
      const doc = new DOMParser().parseFromString(html, "text/html");
      const newMainContent = doc.querySelector("main");

      if (newMainContent) {
        mainContent.innerHTML = newMainContent.innerHTML;
        mainContent.style.opacity = 0;
        requestAnimationFrame(() => {
            mainContent.style.transition = "opacity 0.4s ease-out";
            mainContent.style.opacity = 1;
        });
        pageTitle.textContent = title;
        if (page === "test-tasks") initTestTasksPage();
        else if (page === "payload-generator") initPayloadGeneratorPage();
        else if (page === "history-logs") initHistoryLogsPage();
      }
    } catch (error) {
      console.error(error);
      mainContent.innerHTML = `<div class="neu-card p-6 text-[#FF4D4F]"><h1 class="text-2xl font-semibold">加载失败</h1><p class="mt-4">网络异常，无法加载页面内容。</p></div>`;
    }
  }

  // --- Test Tasks Page ---
  let pollingInterval = null;
  function initTestTasksPage() {
    if (pollingInterval) clearInterval(pollingInterval);
    const modelTabs = document.querySelectorAll(".neu-model-tab");
    const startTestBtn = document.getElementById("start-test-btn");
    
    // API Bindings
    const progressEl = document.getElementById("task-progress-bar");
    const progressText = document.getElementById("task-progress-text");
    const statusBadge = document.getElementById("task-status-badge");
    const totalItems = document.getElementById("task-total");
    const doneItems = document.getElementById("task-done");

    modelTabs.forEach(tab => {
      tab.addEventListener("click", () => {
        modelTabs.forEach(t => t.classList.remove("selected", "bg-[#E8F3FF]", "text-[#1677FF]", "border-[#1677FF]/30"));
        tab.classList.add("selected", "bg-[#E8F3FF]", "text-[#1677FF]", "border-[#1677FF]/30");
      });
    });

    if (startTestBtn) {
      startTestBtn.addEventListener("click", async () => {
        startTestBtn.disabled = true;
        startTestBtn.innerHTML = `<iconify-icon icon="lucide:loader-2" class="animate-spin text-lg mr-2"></iconify-icon>正在初始化...`;
        
        // Call backend API to start task
        const res = await apiFetch("/tasks/start", { method: "POST" });
        // Start polling
        startTestBtn.innerHTML = `<iconify-icon icon="lucide:play" class="text-lg mr-2"></iconify-icon>测试运行中`;
        
        let mockProgress = 0;
        pollingInterval = setInterval(async () => {
            const data = await apiFetch("/tasks/status") || { progress: mockProgress += 10, total: 156, done: Math.floor(156 * (mockProgress/100)), status: "running" };
            if(!progressEl) return;
            let currentProg = Math.min(data.progress, 100);
            progressEl.style.width = currentProg + "%";
            progressText.textContent = currentProg + "%";
            if(data.done !== undefined) doneItems.textContent = data.done;
            
            if (currentProg >= 100) {
                clearInterval(pollingInterval);
                startTestBtn.disabled = false;
                startTestBtn.innerHTML = `<iconify-icon icon="lucide:play" class="text-lg mr-2"></iconify-icon>开始测试`;
                statusBadge.innerHTML = `<span class="w-1.5 h-1.5 bg-[#52C41A] rounded-full mr-2"></span>已完成`;
            }
        }, 1500);
      });
    }
  }

  // --- Payload Generator ---
  function initPayloadGeneratorPage() {
    const generateBtn = document.getElementById("generate-payload-btn");
    const payloadOutput = document.getElementById("payload-output");

    if (generateBtn) {
      generateBtn.addEventListener("click", async () => {
        generateBtn.disabled = true;
        generateBtn.innerHTML = `<iconify-icon icon="lucide:loader-2" class="animate-spin text-lg mr-2"></iconify-icon>生成中...`;
        const res = await apiFetch("/payload/generate", { method: "POST" }) || { payload: "union select 1,2,user()--" };
        
        if (payloadOutput) payloadOutput.value = res.payload;
        generateBtn.disabled = false;
        generateBtn.innerHTML = `生成Payload`;
      });
    }
  }

  // --- History Logs ---
  async function initHistoryLogsPage() {
      const tableBody = document.querySelector("tbody");
      if(!tableBody) return;
      tableBody.innerHTML = `<tr><td colspan="5" class="py-10 text-center"><iconify-icon icon="lucide:loader-2" class="animate-spin text-2xl text-[#1677FF]"></iconify-icon> 数据加载中...</td></tr>`;
      
      const logs = await apiFetch("/logs") || [
          { ip: "101.34.21.118", time: "2026-04-19 14:30:15", level: "severe", count: 5 },
          { ip: "218.94.15.201", time: "2026-04-19 12:12:45", level: "high", count: 2 },
          { ip: "192.168.1.100", time: "2026-04-18 22:45:00", level: "low", count: 12 }
      ];
      
      tableBody.innerHTML = "";
      logs.forEach(log => {
          const mapClass = { "severe": "severe", "high": "high", "medium": "medium", "low": "low" };
          const mapText = { "severe": "严重", "high": "高危", "medium": "中危", "low": "低危" };
          tableBody.innerHTML += `
            <tr class="neu-table-row bg-white">
                <td class="px-6 py-4 font-medium text-[#1D2129]">${log.ip}</td>
                <td class="px-6 py-4 text-[#86909C]">${log.time}</td>
                <td class="px-6 py-4"><span class="neu-badge ${mapClass[log.level]}">${mapText[log.level]}</span></td>
                <td class="px-6 py-4">${log.count}</td>
                <td class="px-6 py-4 text-center space-x-3">
                    <button class="text-[#1677FF] font-medium hover:text-[#1466E6] transition-colors">详情</button>
                    <button class="text-[#1677FF] font-medium hover:text-[#1466E6] transition-colors">下载PDF</button>
                </td>
            </tr>`;
      });
  }

  // Initial Load
  const initialPage = window.location.hash ? window.location.hash.substring(1) : "test-tasks";
  loadPageContent(initialPage);
  const activeNavItem = document.querySelector(`.nav-item[href="#${initialPage}"]`);
  if (activeNavItem) activeNavItem.click();
});''',
    r'd:\1-compitition\waibao\caelum\HTML\01-caelum.html': r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Caelum 渗透测试系统</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../src/caelum/static/css/caelum.css">
</head>
<body class="antialiased min-h-screen bg-[#F7F9FC] text-[#4E5969]">
    <div class="flex h-screen overflow-hidden">
        <!-- Left Sidebar (15%) -->
        <aside class="w-[15%] min-w-[240px] bg-[#F7F9FC] neu-card m-4 flex flex-col flex-shrink-0 z-10 transition-transform duration-300 md:block hidden">
            <!-- Logo -->
            <div class="h-[8vh] flex items-center px-6 border-b border-[#E5E6EB]/50">
                <iconify-icon icon="lucide:hexagon" class="text-2xl text-[#1677FF]"></iconify-icon>
                <span class="text-xl font-bold text-[#1D2129] ml-3 tracking-wide">Caelum</span>
            </div>
            
            <!-- Navigation Menu -->
            <nav class="flex-1 py-6 overflow-y-auto">
                <a href="#test-tasks" class="nav-item neu-nav-item active">
                    <iconify-icon icon="lucide:shield-check" class="text-xl w-6"></iconify-icon>
                    <span class="ml-3">测试任务</span>
                </a>
                <a href="#payload-generator" class="nav-item neu-nav-item">
                    <iconify-icon icon="lucide:code-2" class="text-xl w-6"></iconify-icon>
                    <span class="ml-3">Payload生成</span>
                </a>
                <a href="#history-logs" class="nav-item neu-nav-item">
                    <iconify-icon icon="lucide:history" class="text-xl w-6"></iconify-icon>
                    <span class="ml-3">历史日志</span>
                </a>
            </nav>
        </aside>
        
        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col overflow-hidden w-full md:w-[85%]">
            <!-- Top Navigation Bar (8%) -->
            <header class="h-[8vh] bg-[#FFFFFF] shadow-sm flex items-center justify-between px-8 flex-shrink-0 z-20">
                <div class="flex items-center">
                    <h1 id="page-title" class="text-[24px] font-semibold text-[#1D2129] tracking-tight">安全测试任务</h1>
                </div>
                
                <div class="flex items-center space-x-6">
                    <button class="relative p-2 text-[#86909C] hover:text-[#1677FF] hover:bg-[#F7F9FC] rounded-lg transition-all duration-300">
                        <iconify-icon icon="lucide:bell" class="text-[22px]"></iconify-icon>
                        <span class="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-[#FF4D4F] border-2 border-white rounded-full"></span>
                    </button>
                    <div class="flex items-center cursor-pointer hover:opacity-80 transition-opacity">
                        <div class="w-9 h-9 rounded-full bg-[#E8F3FF] flex items-center justify-center text-[#1677FF] text-sm font-semibold border border-[#1677FF]/20 shadow-inner">
                            A
                        </div>
                        <span class="ml-3 text-sm font-medium text-[#1D2129] hidden sm:block">Administrator</span>
                    </div>
                </div>
            </header>
            
            <!-- Dynamic Sub-page Container -->
            <main class="flex-1 overflow-y-auto p-6 md:p-8 bg-[#F7F9FC] scroll-smooth fade-in">
                <!-- Content injected by caelum.js -->
            </main>
        </div>
    </div>

    <!-- Script -->
    <script src="../src/caelum/static/js/caelum.js"></script>
</body>
</html>''',
    r'd:\1-compitition\waibao\caelum\HTML\01-test-tasks-content.html': r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
</head>
<body>
    <main class="flex-1 w-full max-w-[1600px] mx-auto fade-in">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <!-- Left Column: New Test Task Form -->
            <div class="lg:col-span-4 space-y-8">
                <!-- New Task Card -->
                <div class="neu-card p-8">
                    <h2 class="text-[18px] font-medium text-[#1D2129] mb-8 flex items-center tracking-tight">
                        <iconify-icon icon="lucide:plus-circle" class="text-[22px] mr-3 text-[#1677FF]"></iconify-icon>
                        新建安全测试任务
                    </h2>
                    
                    <!-- Target Input -->
                    <div class="mb-8">
                        <label class="block text-[14px] font-medium text-[#4E5969] mb-3">
                            测试目标 <span class="text-[#FF4D4F] ml-1">*</span>
                        </label>
                        <div class="flex space-x-3">
                            <input 
                                type="text" 
                                id="target-input"
                                placeholder="如: example.com 或 192.168.1.1"
                                class="neu-input flex-1 text-[14px] placeholder-[#86909C]"
                            />
                            <button id="add-target-btn" class="neu-btn-primary px-5 py-2.5 text-[14px]">
                                <iconify-icon icon="lucide:plus" class="mr-1"></iconify-icon>
                                添加
                            </button>
                        </div>
                        
                        <!-- Target List -->
                        <div id="target-list" class="mt-4 space-y-3">
                            <!-- Populated dynamically -->
                            <div class="flex items-center justify-between bg-[#F7F9FC] px-4 py-2.5 rounded-xl border border-[#E5E6EB]/50 shadow-sm">
                                <span class="text-[14px] text-[#4E5969]">192.168.1.100</span>
                                <button class="text-[#86909C] hover:text-[#FF4D4F] transition-colors w-6 h-6 flex items-center justify-center rounded-md hover:bg-white pb-[2px] shadow-none">
                                    <iconify-icon icon="lucide:x"></iconify-icon>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Model Selection -->
                    <div class="mb-10">
                        <label class="block text-[14px] font-medium text-[#4E5969] mb-4">
                            测试模型选择 <span class="text-[#FF4D4F] ml-1">*</span>
                        </label>
                        <div class="grid grid-cols-3 gap-4">
                            <div class="neu-model-tab selected" data-model="deepseek">
                                <iconify-icon icon="lucide:brain" class="text-[26px] mb-2.5"></iconify-icon>
                                <div class="text-[14px] font-semibold text-[#1D2129]">DeepSeek</div>
                                <div class="text-[12px] opacity-70 mt-1">深度推理</div>
                            </div>
                            <div class="neu-model-tab" data-model="chatgpt">
                                <iconify-icon icon="lucide:sparkles" class="text-[26px] mb-2.5"></iconify-icon>
                                <div class="text-[14px] font-semibold text-[#1D2129]">ChatGPT</div>
                                <div class="text-[12px] opacity-70 mt-1">通用智能</div>
                            </div>
                            <div class="neu-model-tab" data-model="claude">
                                <iconify-icon icon="lucide:zap" class="text-[26px] mb-2.5"></iconify-icon>
                                <div class="text-[14px] font-semibold text-[#1D2129]">Claude</div>
                                <div class="text-[12px] opacity-70 mt-1">安全专家</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Start Test Button -->
                    <div class="flex justify-center pt-2">
                        <button id="start-test-btn" class="neu-btn-primary w-full py-3.5 text-[16px] tracking-wide">
                            <iconify-icon icon="lucide:play" class="text-[20px] mr-2"></iconify-icon>
                            开始测试
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Right Column: Status Monitor and Logs -->
            <div class="lg:col-span-8 space-y-8 flex flex-col h-full">
                <!-- Task Status Monitor -->
                <div class="neu-card p-8">
                    <div class="flex items-center justify-between mb-6">
                        <h3 class="text-[18px] font-medium text-[#1D2129] flex items-center">
                            <iconify-icon icon="lucide:activity" class="text-[22px] mr-3 text-[#1677FF]"></iconify-icon>
                            任务状态监控
                        </h3>
                        <span id="task-status-badge" class="neu-badge low px-4 py-1.5 text-[13px]">
                            等待就绪
                        </span>
                    </div>
                    
                    <div class="space-y-6">
                        <!-- Progress Bar -->
                        <div>
                            <div class="flex items-center justify-between mb-3">
                                <span class="text-[14px] text-[#86909C]">测试进度</span>
                                <span id="task-progress-text" class="text-[16px] font-semibold text-[#1677FF]">0%</span>
                            </div>
                            <div class="w-full bg-[#E5E6EB]/50 rounded-full h-3 overflow-hidden shadow-inner">
                                <div id="task-progress-bar" class="bg-[#1677FF] h-full rounded-full transition-all duration-700 ease-out" style="width: 0%;"></div>
                            </div>
                        </div>
                        
                        <!-- Stats Grid -->
                        <div class="grid grid-cols-2 gap-6 pt-2">
                            <div class="bg-[#F7F9FC] rounded-2xl p-5 shadow-[inset_2px_2px_5px_rgba(200,206,215,0.2)]">
                                <div class="text-[13px] text-[#86909C] mb-1.5 flex justify-between">检测项 <iconify-icon icon="lucide:crosshair"></iconify-icon></div>
                                <div class="text-[24px] font-bold text-[#1D2129]" id="task-total">0</div>
                            </div>
                            <div class="bg-[#F7F9FC] rounded-2xl p-5 shadow-[inset_2px_2px_5px_rgba(200,206,215,0.2)]">
                                <div class="text-[13px] text-[#86909C] mb-1.5 flex justify-between">已完成 <iconify-icon icon="lucide:check-circle"></iconify-icon></div>
                                <div class="text-[24px] font-bold text-[#1D2129]" id="task-done">0</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Log Report -->
                <div class="neu-card p-8 flex-1 flex flex-col min-h-[300px]">
                    <h3 class="text-[18px] font-medium text-[#1D2129] mb-5 flex items-center">
                        <iconify-icon icon="lucide:file-text" class="text-[22px] mr-3 text-[#1677FF]"></iconify-icon>
                        测试报告日志
                    </h3>
                    
                    <div class="bg-[#F7F9FC] shadow-[inset_4px_4px_8px_rgba(200,206,215,0.3),inset_-4px_-4px_8px_rgba(255,255,255,0.8)] border-none rounded-xl p-5 flex-1 overflow-y-auto mb-6">
                        <div class="space-y-3 text-[13px] font-mono text-[#4E5969]" id="live-logs-container">
                            <!-- Injected by API -->
                            <div>[等待系统初始化...] 日志监听中</div>
                        </div>
                    </div>

                    <div class="flex space-x-5">
                        <button class="neu-btn-secondary flex-1 py-3">查看详细报告</button>
                        <button class="neu-btn-secondary flex-1 py-3 text-[#1677FF]"><iconify-icon icon="lucide:download" class="mr-2"></iconify-icon>下载 PDF</button>
                    </div>
                </div>
            </div>
        </div>
    </main>
</body>
</html>''',
    r'd:\1-compitition\waibao\caelum\HTML\02-payload-caelum.html': r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
</head>
<body>
    <main class="flex-1 w-full max-w-[1280px] mx-auto p-4 md:p-8 fade-in">
        <div class="neu-card p-10">
            <h2 class="text-[24px] font-medium text-[#1D2129] mb-10 flex items-center tracking-tight">
                <iconify-icon icon="lucide:terminal-square" class="text-[28px] mr-4 text-[#1677FF]"></iconify-icon>
                Payload 智能生成器
            </h2>
            
            <div class="space-y-10">
                <!-- Type Selection -->
                <div>
                    <label class="block text-[16px] font-medium text-[#4E5969] mb-4">目标 Payload 类型</label>
                    <div class="relative">
                        <select class="neu-input w-full h-[52px] appearance-none pr-10 text-[15px]">
                            <option disabled selected>选择一种注入或测试向量类型...</option>
                            <option>SQL Injection (SQLi)</option>
                            <option>Cross-Site Scripting (XSS)</option>
                            <option>Command Injection (RCE)</option>
                            <option>Local File Inclusion (LFI)</option>
                            <option>Server-Side Request Forgery (SSRF)</option>
                        </select>
                        <iconify-icon icon="lucide:chevron-down" class="absolute right-4 top-1/2 -translate-y-1/2 text-[20px] text-[#86909C] pointer-events-none"></iconify-icon>
                    </div>
                </div>

                <!-- Parameters config -->
                <div>
                    <label class="block text-[16px] font-medium text-[#4E5969] mb-4">特征参数配置 (JSON)</label>
                    <textarea 
                        rows="6" 
                        class="neu-input w-full p-5 text-[14px] font-mono leading-relaxed" 
                        placeholder="{
  &quot;length&quot;: 10,
  &quot;encoding&quot;: &quot;base64&quot;,
  &quot;waf_bypass&quot;: true
}"
                    ></textarea>
                    <p class="text-[12px] text-[#86909C] mt-3 ml-1 tracking-wide">填写 JSON 格式以覆盖默认生成策略参数。</p>
                </div>

                <!-- Generate Button -->
                <div class="pt-2">
                    <button id="generate-payload-btn" class="neu-btn-primary w-full h-[56px] text-[18px] tracking-widest font-semibold flex justify-center items-center">
                        <iconify-icon icon="lucide:rocket" class="mr-3 text-[22px]"></iconify-icon>
                        智能生成
                    </button>
                </div>

                <!-- Output Area -->
                <div class="pt-8 border-t border-[#E5E6EB]/50 mt-10">
                    <label class="block text-[16px] font-medium text-[#4E5969] mb-4">生成结果回显</label>
                    <div class="relative">
                        <textarea 
                            id="payload-output" 
                            rows="4" 
                            readonly 
                            class="neu-input w-full p-5 text-[#1D2129] font-mono text-[15px] bg-[#F7F9FC] shadow-[inset_4px_4px_8px_rgba(200,206,215,0.3),inset_-4px_-4px_8px_rgba(255,255,255,0.8)]"
                            placeholder="点击上方生成按钮获取结果..."
                        ></textarea>
                        <button class="absolute top-4 right-4 text-[#86909C] hover:text-[#1677FF] transition-colors p-2 bg-white rounded-lg shadow-sm hover:shadow-md cursor-pointer border border-[#E5E6EB]/50 active:shadow-inner flex items-center justify-center">
                            <iconify-icon icon="lucide:copy" class="text-[18px]"></iconify-icon>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </main>
</body>
</html>''',
    r'd:\1-compitition\waibao\caelum\HTML\03-history-logs.html': r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
</head>
<body>
    <main class="flex-1 w-full max-w-[1600px] mx-auto p-4 md:p-8 fade-in">
        <div class="neu-card p-10 flex flex-col h-[calc(100vh-140px)] min-h-[600px]">
            
            <!-- Header & Filter Actions -->
            <div class="flex justify-between items-center mb-8 border-b border-[#E5E6EB]/50 pb-6">
                <h2 class="text-[22px] font-medium text-[#1D2129] flex items-center tracking-tight">
                    <iconify-icon icon="lucide:clipboard-list" class="text-[26px] mr-3 text-[#1677FF]"></iconify-icon>
                    测试执行日志
                </h2>
                
                <div class="flex space-x-4">
                    <div class="relative w-[320px]">
                        <iconify-icon icon="lucide:search" class="absolute left-4 top-1/2 -translate-y-1/2 text-[#86909C] text-[18px]"></iconify-icon>
                        <input type="text" placeholder="搜索目标 IP 或事件..." class="neu-input w-full pl-12 h-[42px] text-[14px] placeholder-[#86909C]">
                    </div>
                    <button class="neu-btn-secondary h-[42px] px-6 text-[14px] flex items-center justify-center space-x-2 text-[#4E5969]">
                        <iconify-icon icon="lucide:filter" class="text-[16px]"></iconify-icon>
                        <span>高级筛选</span>
                    </button>
                    <button class="neu-btn-primary h-[42px] px-6 text-[14px] flex items-center justify-center space-x-2 shadow-[4px_4px_8px_rgba(200,206,215,0.4),-4px_-4px_8px_rgba(255,255,255,0.8)]">
                        <iconify-icon icon="lucide:arrow-down-to-line" class="text-[16px]"></iconify-icon>
                        <span>导出全部</span>
                    </button>
                </div>
            </div>

            <!-- Table Container -->
            <div class="flex-1 w-full overflow-hidden flex flex-col pt-2 pb-6">
                <!-- Neumorphic wrapping container for table to give it inner depth -->
                <div class="flex-1 bg-[#F7F9FC] rounded-[20px] shadow-[inset_6px_6px_12px_rgba(200,206,215,0.4),inset_-6px_-6px_12px_rgba(255,255,255,0.9)] overflow-hidden flex flex-col border border-white">
                    <div class="flex-1 overflow-x-auto overflow-y-auto w-full custom-scrollbar">
                        <table class="w-full text-left text-[14px] whitespace-nowrap min-w-[800px]">
                            <thead class="bg-[#F7F9FC] text-[#86909C] text-[13px] font-medium sticky top-0 z-10 before:content-[''] before:absolute before:left-0 before:right-0 before:bottom-0 before:h-[1px] before:bg-gradient-to-r before:from-transparent before:via-[#E5E6EB] before:to-transparent">
                                <tr>
                                    <th class="px-8 py-5 tracking-wide w-[20%]">目标特征 IP</th>
                                    <th class="px-8 py-5 tracking-wide w-[25%]">最近活动时间</th>
                                    <th class="px-8 py-5 tracking-wide w-[15%]">威胁评级</th>
                                    <th class="px-8 py-5 tracking-wide w-[15%]">触发总计</th>
                                    <th class="px-8 py-5 tracking-wide text-center w-[25%]">操作集</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-[#E5E6EB]/30 divide-dashed text-[#4E5969]">
                                <!-- Row template used by js -->
                                <tr class="neu-table-row bg-[#F7F9FC] hover:bg-[#F0F4F8] transition-colors group cursor-pointer">
                                    <td class="px-8 py-5 font-medium text-[#1D2129] group-hover:text-[#1677FF] transition-colors"><iconify-icon icon="lucide:server" class="mr-2 text-[#86909C] group-hover:text-[#1677FF] transition-colors"></iconify-icon> 正在加载...</td>
                                    <td class="px-8 py-5">--</td>
                                    <td class="px-8 py-5"><span class="neu-badge low">--</span></td>
                                    <td class="px-8 py-5 font-mono">--</td>
                                    <td class="px-8 py-5 text-center">--</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Footer Pagination -->
            <div class="flex items-center justify-between pt-6 border-t border-[#E5E6EB]/50 flex-shrink-0">
                <span class="text-[14px] text-[#86909C] font-medium tracking-wide">
                    共 <span class="text-[#1D2129] font-bold mx-1" id="total-logs-count">3</span> 项条目录入
                </span>
                
                <div class="flex items-center space-x-3">
                    <button class="w-[42px] h-[42px] rounded-xl bg-[#F7F9FC] shadow-[3px_3px_6px_rgba(200,206,215,0.4),-3px_-3px_6px_rgba(255,255,255,0.9)] hover:shadow-[inset_2px_2px_5px_rgba(200,206,215,0.3),inset_-2px_-2px_5px_rgba(255,255,255,0.8)] flex items-center justify-center text-[#86909C] hover:text-[#1677FF] transition-all disabled:opacity-50 disabled:pointer-events-none disabled:shadow-none" disabled>
                        <iconify-icon icon="lucide:chevron-left" class="text-[20px]"></iconify-icon>
                    </button>
                    <!-- Pagination pill -->
                    <div class="px-5 h-[42px] rounded-xl bg-[#E8F3FF] text-[#1677FF] font-medium flex items-center justify-center text-[14px] shadow-[inset_2px_2px_5px_rgba(200,206,215,0.2)] border border-[#1677FF]/20">
                        1 / 5
                    </div>
                    <button class="w-[42px] h-[42px] rounded-xl bg-[#F7F9FC] shadow-[3px_3px_6px_rgba(200,206,215,0.4),-3px_-3px_6px_rgba(255,255,255,0.9)] hover:shadow-[inset_2px_2px_5px_rgba(200,206,215,0.3),inset_-2px_-2px_5px_rgba(255,255,255,0.8)] flex items-center justify-center text-[#86909C] hover:text-[#1677FF] transition-all">
                        <iconify-icon icon="lucide:chevron-right" class="text-[20px]"></iconify-icon>
                    </button>
                </div>
            </div>
            
        </div>
    </main>
</body>
</html>'''
}

for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
print("Files restored successfully.")
