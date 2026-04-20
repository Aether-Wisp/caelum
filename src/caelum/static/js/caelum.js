document.addEventListener("DOMContentLoaded", () => {
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
});