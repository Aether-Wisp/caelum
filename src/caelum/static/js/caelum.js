document.addEventListener("DOMContentLoaded", () => {
  const navItems = document.querySelectorAll(".nav-item");
  const mainContent = document.querySelector("main");
  const pageTitle = document.querySelector("#page-title");

  // --- Navigation ---
  navItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const page = item.getAttribute("href").substring(1);

      // Remove active class from all items
      navItems.forEach((i) =>
        i.classList.remove(
          "active",
          "bg-[#e6f7ff]",
          "text-[#1677ff]",
          "font-medium",
        ),
      );

      // Add active class to the clicked item
      item.classList.add(
        "active",
        "bg-[#e6f7ff]",
        "text-[#1677ff]",
        "font-medium",
      );

      // Load page content (mock)
      loadPageContent(page);
    });
  });

  async function loadPageContent(page) {
    try {
      let url = "";
      let title = "";
      switch (page) {
        case "test-tasks":
          url = "/HTML/01-test-tasks-content.html";
          title = "安全测试任务";
          break;
        case "payload-generator":
          url = "/HTML/02-payload-caelum.html";
          title = "Payload 生成器";
          break;
        case "history-logs":
          url = "/HTML/03-history-logs.html";
          title = "历史日志";
          break;
        default:
          // For dashboard or other pages
          mainContent.innerHTML = `<div class="p-6"><h1 class="text-2xl font-semibold">${page}</h1><p class="mt-4">此页面正在建设中...</p></div>`;
          pageTitle.textContent = "仪表盘";
          return;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const html = await response.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const newMainContent = doc.querySelector("main");

      if (newMainContent) {
        mainContent.innerHTML = newMainContent.innerHTML;
        pageTitle.textContent = title;
        // Re-initialize event listeners for the new content
        initializePageSpecificScript(page);
      }
    } catch (error) {
      console.error("Could not load page content:", error);
      mainContent.innerHTML = `<div class="p-6 text-red-500"><h1 class="text-2xl font-semibold">加载失败</h1><p class="mt-4">无法加载页面内容，请检查网络连接或文件路径。</p></div>`;
    }
  }

  function initializePageSpecificScript(page) {
    if (page === "test-tasks") {
      initTestTasksPage();
    } else if (page === "payload-generator") {
      initPayloadGeneratorPage();
    }
  }

  // --- Test Tasks Page Logic ---
  function initTestTasksPage() {
    const modelTabs = document.querySelectorAll(".model-tab");
    const startTestBtn = document.getElementById("start-test-btn");
    const modalOverlay = document.getElementById("task-completion-modal");
    const closeModalBtn = document.getElementById("close-modal-btn");
    const viewDetailsBtn = document.getElementById("modal-view-details");
    const downloadPdfBtn = document.getElementById("modal-download-pdf");

    modelTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        modelTabs.forEach((t) =>
          t.classList.remove("selected", "border-[#1677ff]", "bg-[#e6f7ff]"),
        );
        tab.classList.add("selected", "border-[#1677ff]", "bg-[#e6f7ff]");
      });
    });

    if (startTestBtn) {
      startTestBtn.addEventListener("click", () => {
        // Simulate test run and show modal after a delay
        startTestBtn.disabled = true;
        startTestBtn.innerHTML = `
                    <iconify-icon icon="lucide:loader-2" class="animate-spin text-lg mr-2"></iconify-icon>
                    测试中...
                `;
        setTimeout(() => {
          if (modalOverlay) modalOverlay.classList.add("visible");
          startTestBtn.disabled = false;
          startTestBtn.innerHTML = `
                        <iconify-icon icon="lucide:play" class="text-lg mr-2"></iconify-icon>
                        开始测试
                    `;
        }, 3000);
      });
    }

    if (closeModalBtn) {
      closeModalBtn.addEventListener("click", () => {
        if (modalOverlay) modalOverlay.classList.remove("visible");
      });
    }

    if (modalOverlay) {
      modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) {
          modalOverlay.classList.remove("visible");
        }
      });
    }
  }

  // --- Payload Generator Page Logic ---
  function initPayloadGeneratorPage() {
    const generateBtn = document.getElementById("generate-payload-btn");
    const payloadOutput = document.getElementById("payload-output");

    if (generateBtn) {
      generateBtn.addEventListener("click", () => {
        generateBtn.disabled = true;
        generateBtn.innerHTML = `
                    <iconify-icon icon="lucide:loader-2" class="animate-spin text-lg mr-2"></iconify-icon>
                    生成中...
                `;

        setTimeout(() => {
          const generatedPayload = `union select 1,2,3,user(),5,6,7,8,9,10--`;
          if (payloadOutput) {
            payloadOutput.value = generatedPayload;
          }

          generateBtn.disabled = false;
          generateBtn.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 mr-2"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm4 0h-2v-2h2v2zm-4-4H9V8h2v4zm4 0h-2V8h2v4z"/></svg>
                        生成Payload
                    `;
        }, 1500);
      });
    }
  }

  // --- Initial Page Load ---
  // Load the default page content on initial load
  const initialPage = window.location.hash
    ? window.location.hash.substring(1)
    : "test-tasks";
  loadPageContent(initialPage);

  // Set the correct active nav item on initial load
  const activeNavItem = document.querySelector(
    `.nav-item[href="#${initialPage}"]`,
  );
  if (activeNavItem) {
    navItems.forEach((i) =>
      i.classList.remove(
        "active",
        "bg-[#e6f7ff]",
        "text-[#1677ff]",
        "font-medium",
      ),
    );
    activeNavItem.classList.add(
      "active",
      "bg-[#e6f7ff]",
      "text-[#1677ff]",
      "font-medium",
    );
  } else {
    // Default to test-tasks if hash is invalid
    document
      .querySelector('.nav-item[href="#test-tasks"]')
      .classList.add("active", "bg-[#e6f7ff]", "text-[#1677ff]", "font-medium");
  }
});
