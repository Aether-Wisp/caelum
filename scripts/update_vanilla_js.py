import os
import re

js_content = """document.addEventListener("DOMContentLoaded", () => {
  const navItems = document.querySelectorAll(".nav-item");
  const mainContent = document.querySelector("main");
  const pageTitle = document.querySelector("#page-title");

  // Api config
  const API_BASE = "http://" + window.location.hostname + ":8888/api";
  async function apiFetch(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, options);
      if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
      return await response.json();
    } catch (err) {
      console.warn("API Error:", err);
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
    const liveLogsContainer = document.getElementById("live-logs-container");
    const targetInput = document.getElementById("target-input");
    const addTargetBtn = document.getElementById("add-target-btn");
    const targetList = document.getElementById("target-list");

    let targets = ["192.168.1.100"];
    let selectedModel = "deepseek";
    let activeSessionId = null;

    function renderTargets() {
        if(!targetList) return;
        targetList.innerHTML = targets.map((t, idx) => `
            <div class="flex items-center justify-between bg-[#F7F9FC] px-4 py-2.5 rounded-xl border border-[#E5E6EB]/50 shadow-sm">
                <span class="text-[14px] text-[#4E5969]">${t}</span>
                <button class="remove-target-btn text-[#86909C] hover:text-[#FF4D4F] transition-colors w-6 h-6 flex items-center justify-center rounded-md hover:bg-white pb-[2px] shadow-none" data-idx="${idx}">
                    <iconify-icon icon="lucide:x"></iconify-icon>
                </button>
            </div>
        `).join("");
        document.querySelectorAll(".remove-target-btn").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const idx = parseInt(e.currentTarget.getAttribute("data-idx"));
                targets.splice(idx, 1);
                renderTargets();
            });
        });
    }

    if (addTargetBtn && targetInput) {
        addTargetBtn.addEventListener("click", () => {
            const val = targetInput.value.trim();
            if(val) {
                targets.push(val);
                targetInput.value = "";
                renderTargets();
            }
        });
    }

    modelTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            modelTabs.forEach(t => t.classList.remove("selected", "bg-[#E8F3FF]", "text-[#1677FF]", "border-[#1677FF]/30"));
            tab.classList.add("selected", "bg-[#E8F3FF]", "text-[#1677FF]", "border-[#1677FF]/30");
            selectedModel = tab.getAttribute("data-model");
        });
    });
    
    // Initial render
    renderTargets();

    function formatLogs(logs) {
        if(!logs || logs.length === 0) return `<div>待测试开始后将在此显示日志，系统已处于监听状态...</div>`;
        return logs.map(log => {
            const timeStr = log.timestamp ? log.timestamp.split('T')[1]?.split('.')[0] : new Date(log.time * 1000).toISOString().split('T')[1].split('.')[0];
            const color = log.status === 'success' ? 'text-[#52C41A]' : log.status === 'error' ? 'text-[#FF4D4F]' : 'text-[#86909C]';
            return `<div class="flex items-start">
                        <span class="text-[#86909C] w-24 shrink-0">[${timeStr || ''}]</span>
                        <span class="${color}">${log.message || JSON.stringify(log)}</span>
                    </div>`;
        }).join("");
    }

    if (startTestBtn) {
      startTestBtn.addEventListener("click", async () => {
        if (targets.length === 0) {
            alert("请至少添加一个测试目标");
            return;
        }

        startTestBtn.disabled = true;
        startTestBtn.innerHTML = `<iconify-icon icon="lucide:loader-2" class="animate-spin text-lg mr-2"></iconify-icon>正在初始化...`;
        statusBadge.innerHTML = `<span class="w-1.5 h-1.5 bg-[#1677FF] rounded-full mr-2"></span>运行中`;
        statusBadge.className = "neu-badge px-4 py-1.5 text-[13px] bg-[#E8F3FF] text-[#1677FF] mb-0 ml-auto";
        if (liveLogsContainer) liveLogsContainer.innerHTML = "<div>正在启动自动化测试任务...</div>";
        
        const res = await apiFetch("/automated-test/run", { 
            method: "POST", 
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                target: targets[0], 
                model: selectedModel 
            }) 
        });

        if (!res || !res.session_id) {
            startTestBtn.disabled = false;
            startTestBtn.innerHTML = `<iconify-icon icon="lucide:play" class="text-lg mr-2"></iconify-icon>开始测试`;
            statusBadge.innerHTML = `<span class="w-1.5 h-1.5 bg-[#FF4D4F] rounded-full mr-2"></span>启动失败`;
            return;
        }

        activeSessionId = res.session_id;

        // Start polling
        startTestBtn.innerHTML = `<iconify-icon icon="lucide:play" class="text-lg mr-2"></iconify-icon>测试运行中`;
        
        pollingInterval = setInterval(async () => {
            const data = await apiFetch(`/automated-test/progress/${activeSessionId}`);
            if(!data || !progressEl) return;
            
            let currentProg = Math.min(data.progress || 0, 100);
            progressEl.style.width = currentProg + "%";
            progressText.textContent = currentProg + "%";
            if (data.total_steps !== undefined) totalItems.textContent = data.total_steps;
            if (data.status === 'running') doneItems.textContent = Math.floor(currentProg / 100 * (data.total_steps || 0));
            if (liveLogsContainer && data.logs) liveLogsContainer.innerHTML = formatLogs(data.logs);
            
            if (data.status === 'completed' || currentProg >= 100) {
                clearInterval(pollingInterval);
                startTestBtn.disabled = false;
                startTestBtn.innerHTML = `<iconify-icon icon="lucide:play" class="text-lg mr-2"></iconify-icon>开始测试`;
                statusBadge.innerHTML = `<span class="w-1.5 h-1.5 bg-[#52C41A] rounded-full mr-2"></span>已完成`;
                progressEl.style.width = "100%";
                progressText.textContent = "100%";
                doneItems.textContent = data.total_steps || totalItems.textContent;
            } else if (data.status === 'error') {
                clearInterval(pollingInterval);
                startTestBtn.disabled = false;
                startTestBtn.innerHTML = `<iconify-icon icon="lucide:play" class="text-lg mr-2"></iconify-icon>开始测试`;
                statusBadge.innerHTML = `<span class="w-1.5 h-1.5 bg-[#FF4D4F] rounded-full mr-2"></span>测试失败`;
            }
        }, 1500);
      });
    }
  }

  // --- Payload Generator ---
  function initPayloadGeneratorPage() {
    const generateBtn = document.getElementById("generate-payload-btn");
    const payloadOutput = document.getElementById("payload-output");
    const paramInput = document.querySelector("textarea[placeholder*='length']"); 
    const typeSelect = document.querySelector("select");

    if (generateBtn) {
      generateBtn.addEventListener("click", async () => {
        let params = {};
        try {
            if (paramInput && paramInput.value.trim()) {
                params = JSON.parse(paramInput.value.trim());
            }
        } catch(e) {
            alert("参数JSON格式错误");
            return;
        }

        const type = typeSelect ? typeSelect.value : "SQL Injection (SQLi)";

        generateBtn.disabled = true;
        generateBtn.innerHTML = `<iconify-icon icon="lucide:loader-2" class="animate-spin text-lg mr-2"></iconify-icon>生成中...`;
        
        const res = await apiFetch("/payloads/generate", { 
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                vuln_type: type, 
                target_env: params.target_env || "mysql",
                bypass_waf: params.waf_bypass || false,
                max_length: params.length || 0,
                encoding: params.encoding || "none"
            })
        });
        
        if (payloadOutput) {
            if (res && res.payload) {
                payloadOutput.value = res.payload;
            } else {
                payloadOutput.value = "Failed to generate payload.";
            }
        }
        
        generateBtn.disabled = false;
        generateBtn.innerHTML = `<iconify-icon icon="lucide:rocket" class="mr-3 text-[22px]"></iconify-icon>智能生成`;
      });
    }
  }

  // --- History Logs ---
  async function initHistoryLogsPage() {
      const tableBody = document.querySelector("tbody");
      if(!tableBody) return;
      tableBody.innerHTML = `<tr><td colspan="5" class="py-10 text-center"><iconify-icon icon="lucide:loader-2" class="animate-spin text-2xl text-[#1677FF]"></iconify-icon> 数据加载中...</td></tr>`;
      
      const res = await apiFetch("/automated-test/history");
      const logs = res ? (res.history || res) : [];
      const countEl = document.getElementById("total-logs-count");
      if(countEl) countEl.textContent = logs.length;
      
      tableBody.innerHTML = "";
      if (logs.length === 0) {
          tableBody.innerHTML = `<tr><td colspan="5" class="py-10 text-[#86909C] text-center">暂无历史记录</td></tr>`;
          return;
      }
      
      logs.forEach((log) => {
          let level = "medium", mapText = "中危", mapClass = "medium";
          // Try to simulate a severity if not provided from backend
          if (!log.level) {
              const status = log.status || "";
              if (status === "completed") { level = "high"; mapText = "高危"; mapClass = "high"; }
              else if (status === "error") { level = "severe"; mapText = "严重"; mapClass = "severe"; }
              else { level = "low"; mapText = "低危"; mapClass = "low"; }
          }
          
          tableBody.innerHTML += `
            <tr class="neu-table-row bg-white">
                <td class="px-6 py-4 font-medium text-[#1D2129]">${log.target || log.session_id || "Unknown"}</td>
                <td class="px-6 py-4 text-[#86909C]">${log.start_time || "-"}</td>
                <td class="px-6 py-4"><span class="neu-badge ${mapClass}">${mapText}</span></td>
                <td class="px-6 py-4">${log.status}</td>
                <td class="px-6 py-4 text-center space-x-3">
                    <button class="text-[#1677FF] font-medium hover:text-[#1466E6] transition-colors" onclick="alert('Session ID:\\n${log.session_id}')">详情</button>
                    <!-- <button class="text-[#1677FF] font-medium hover:text-[#1466E6] transition-colors">下载PDF</button> -->
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
"""

with open(r'd:\1-compitition\waibao\caelum\src\caelum\static\js\caelum.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("Updated caelum.js successfully!")
