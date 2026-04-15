// Caelum v8.0 纯净客户端逻辑
document.addEventListener("DOMContentLoaded", () => {
  loadTestHistory();
  setInterval(loadTestHistory, 3000);

  const mainForm = document.getElementById("main-test-form");
  if (mainForm) mainForm.addEventListener("submit", startTestTask);

  const payloadForm = document.getElementById("payload-form");
  if (payloadForm) payloadForm.addEventListener("submit", generatePayload);
});

// 轻量级 Toast 提示
function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  toast.innerHTML = (type === "success" ? "✅ " : "❌ ") + message;
  toast.className = `toast show ${type}`;
  setTimeout(() => {
    toast.className = "toast";
  }, 3000);
}

let recentCompletedSessions = new Map();

// 获取测试历史
async function loadTestHistory() {
  try {
    const response = await fetch("/api/automated-test/history");
    if (!response.ok) return;
    const data = await response.json();

    if (data.history && data.history.length > 0) {
      renderSidebarHistory(data.history);

      const now = Date.now();
      const activeTasks = data.history.filter((h) => {
        if (h.status === "running") return true;
        if (h.status === "completed" || h.status === "failed") {
          if (!recentCompletedSessions.has(h.session_id)) {
            recentCompletedSessions.set(h.session_id, now);
          }
          const finishedAt = recentCompletedSessions.get(h.session_id);
          return now - finishedAt < 8000;
        }
        return false;
      });

      renderActiveTasksUI(activeTasks);
    }
  } catch (error) {
    console.error("加载历史出错:", error);
  }
}

// 渲染左侧历史栏
function renderSidebarHistory(history) {
  const listContainer = document.getElementById("sidebar-history-list");
  let html = "";

  [...history].reverse().forEach((item) => {
    let statusClass = "status-failed";
    let statusText = "失败";
    let btnDisabled = "disabled";

    if (item.status === "completed") {
      statusClass = "status-completed";
      statusText = "已完成";
      btnDisabled = "";
    } else if (item.status === "running") {
      statusClass = "status-running";
      statusText = "进行中";
    }

    const date = new Date(item.start_time).toLocaleTimeString();

    html += `
            <div class="history-item">
                <div class="history-target">🎯 ${item.target}</div>
                <div class="history-bottom">
                    <span class="history-status ${statusClass}">${statusText}</span>
                    <span class="history-date">${date}</span>
                </div>
                <div class="history-actions">
                    <button class="history-btn" onclick="viewDetails('${item.session_id}')">详情</button>
                    <!-- 我们只传给查看报告函数 session id，确保完成后可以查看 -->
                    <button class="history-btn" ${btnDisabled} onclick="viewReport('${item.session_id}', '${item.status}')">报告</button>
                </div>
            </div>
        `;
  });

  const newHtml = html || `<div class="empty-state">暂无测试记录</div>`;
  // 避免反复重写 innerHTML 导致列表闪烁
  if (listContainer.innerHTML !== newHtml) {
    listContainer.innerHTML = newHtml;
  }
}

// 启动测试任务
async function startTestTask(e) {
  e.preventDefault();
  const target = document.getElementById("target-ip").value.trim();
  const model = document.getElementById("ai-model-select").value;

  if (!target) {
    showToast("请输入目标IP或域名", "error");
    return;
  }

  showToast("任务启动请求发送中...", "success");

  try {
    const response = await fetch("/api/automated-test/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target, model }),
    });

    if (!response.ok) throw new Error("服务异常");

    // 触发更新
    setTimeout(loadTestHistory, 500);
  } catch (error) {
    showToast("测试任务创建失败", "error");
  }
}

// 渲染活跃任务的并发进度条UI
function renderActiveTasksUI(tasks) {
  const container = document.getElementById("active-tasks-container");

  if (!tasks || tasks.length === 0) {
    container.innerHTML = "";
    return;
  }

  let html =
    '<h3>📈 多目标并发测试进度 &nbsp;<span style="font-size:0.8em; color:#ef4444; border: 1px solid #ef4444; border-radius: 4px; padding: 2px 6px;">⚡智能极速扫描模式 (≤15min)</span></h3>';

  tasks.forEach((task) => {
    let width = "10%";
    let text = "准备初始化...";
    let color = "#3b82f6";
    let reconIcon = "⏳";
    let scanIcon = "⏳";
    let exploitIcon = "⏳";

    const stages = task.stages || [];

    if (stages.length >= 1) {
      width = "30%";
      text = "正在进行信息收集...";
      reconIcon = "🔄";
    }
    if (stages.length >= 2) {
      width = "60%";
      text = "正在深度扫描检测...";
      reconIcon = "✅";
      scanIcon = "🔄";
    }
    if (stages.length >= 3) {
      width = "85%";
      text = "正在复杂环境评估与内网横向移动...";
      scanIcon = "✅";
      exploitIcon = "🔄";
    }

    if (task.status === "completed" || task.status === "failed") {
      width = "100%";
      color = task.status === "failed" ? "#e74c3c" : "#10b981";
      text =
        task.status === "failed"
          ? "测试中断或失败！"
          : "测试全面完成与报告生成！";
      if (stages.length >= 3) {
        exploitIcon = task.status === "failed" ? "❌" : "✅";
      } else if (stages.length === 2 && task.status === "failed") {
        scanIcon = "❌";
      } else if (stages.length === 1 && task.status === "failed") {
        reconIcon = "❌";
      }
    }

    html += `
      <div class="concurrent-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
           <h4 style="margin-bottom:0;">🎯 ${task.target}</h4>
           <span style="font-size:12px; background:rgba(59, 130, 246, 0.15); color:#3b82f6; padding:4px 8px; border-radius:12px; font-weight:600;">🤖 AI 状态机 (多阶段链式渗透)</span>
        </div>
        <div class="progress-track" style="margin-bottom:8px;">
          <div class="progress-fill" style="width: ${width}; background-color: ${color};"></div>
        </div>
        <div class="state-machine-ui" style="display:flex; align-items:center; font-size:12px; font-weight:600; margin-bottom:12px; overflow:hidden;">
           <span style="color:${stages.length >= 1 ? "#3b82f6" : "#a0aec0"}">🌐 Initial</span>
           <span style="margin:0 5px; color:#cbd5e1;">➔</span>
           <span style="color:${stages.length >= 2 ? "#3b82f6" : "#a0aec0"}">👤 WebShell</span>
           <span style="margin:0 5px; color:#cbd5e1;">➔</span>
           <span style="color:${stages.length >= 3 ? "#3b82f6" : "#a0aec0"}">👑 Root Pwn</span>
           <span style="margin:0 5px; color:#cbd5e1;">➔</span>
           <span style="color:${task.status === "completed" && stages.length >= 3 ? "#10b981" : "#a0aec0"}">🕵️ Lateral Make</span>
        </div>
        <div class="progress-status" style="margin-top:0;">${text}</div>
        <div class="progress-stages">
          <span>🔍 信息聚合 <span style="font-size:1.2em;">${reconIcon}</span></span>
          <span>🪲 深度扫描 <span style="font-size:1.2em;">${scanIcon}</span></span>
          <span>⚡ 横向扩展 <span style="font-size:1.2em;">${exploitIcon}</span></span>
        </div>
      </div>
    `;
  });

  if (container.innerHTML !== html) {
    container.innerHTML = html;
  }
}

// Payload 生成器
async function generatePayload(e) {
  e.preventDefault();
  const type = document.getElementById("payload-type").value;
  const paramsStr = document.getElementById("payload-params").value.trim();
  const resultBox = document.getElementById("payload-result");

  if (!type) {
    showToast("请选择Payload类型", "warning");
    return;
  }

  let params = {};
  if (paramsStr) {
    try {
      params = JSON.parse(paramsStr);
    } catch (e) {
      showToast("JSON 格式错误，请检查参数", "error");
      return;
    }
  }

  try {
    const res = await fetch("/api/payloads/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, params }),
    });

    const data = await res.json();
    resultBox.style.display = "block";
    if (data.payload) {
      resultBox.innerHTML = `<strong>Result:</strong><br>${data.payload.replace(/</g, "&lt;")}`;
    } else {
      resultBox.innerHTML = `<span style="color:#ef4444">生成错误: ${data.error || "未知"}</span>`;
    }
  } catch (err) {
    showToast("请求失败", "error");
  }
}

// 查看详情日志
window.viewDetails = function (sessionId) {
  showToast("任务日志已打印至控制台 (F12)");
  fetch(`/api/automated-test/history`)
    .then((r) => r.json())
    .then((data) => {
      const task = data.history.find((h) => h.session_id === sessionId);
      if (task) {
        console.log(
          "【详细测试阶段日志】\n",
          JSON.stringify(task.stages, null, 2),
        );
      }
    });
};

// 查看报告 新窗口渲染
window.viewReport = function (sessionId, status) {
  if (status !== "completed") {
    return showToast("任务未完成不能生成报告", "warning");
  }
  showToast("报告渲染中...", "success");
  fetch("/api/automated-test/report/" + sessionId)
    .then((r) => r.json())
    .then((data) => {
      if (!data.report) return showToast("获取报告内容失败", "error");

      const w = window.open("", "_blank");
      let html =
        typeof marked !== "undefined"
          ? marked.parse(data.report)
          : data.report.replace(/\n/g, "<br>");

      w.document.write(`
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>Caelum 渗透测试评估报告</title>
            <style>
                body { font-family: -apple-system, system-ui, sans-serif; padding: 50px; background: #f3f4f6; color: #1f2937; line-height: 1.6; }
                .report-box { max-width: 900px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
                h1, h2, h3 { color: #1e3a8a; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-top: 1.5em; }
                h1 { font-size: 2.2em; border-bottom-width: 2px; }
                pre { background: #1e293b; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; font-family: monospace; }
                code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #db2777; }
                pre code { background: transparent; color: inherit; padding: 0;}
                blockquote { border-left: 4px solid #3b82f6; padding-left: 16px; color: #4b5563; background: #f8fafc; padding: 12px; margin: 1em 0; }
                table { width: 100%; border-collapse: collapse; margin: 1.5em 0; }
                th, td { border: 1px solid #e5e7eb; padding: 12px; text-align: left; }
                th { background: #f9fafb; font-weight: 600; }
                .print-btn { float:right; background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; }
                .print-btn:hover { background: #2563eb; }
                @media print { body { background: white; padding: 0; } .report-box { box-shadow: none; padding: 0; } .print-btn { display: none; } }
            </style>
        </head>
        <body>
            <div class="report-box">
                <button class="print-btn" onclick="window.print()">🖨️ 保存为PDF/打印</button>
                ${html}
            </div>
        </body>
        </html>
        `);
      w.document.close();
    })
    .catch((e) => showToast("服务器错误，获取报告失败", "error"));
};
