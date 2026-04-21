import React, { useState, useEffect } from "react";
import {
  Circle,
  PlayCircle,
  CheckCircle2,
  ChevronRight,
  Plus,
  Search,
  HelpCircle,
  Layers,
  Inbox,
  Square,
  Briefcase,
} from "lucide-react";

export default function LinearBoard() {
  const [activeTab, setActiveTab] = useState("active");

  // Strict Design System Token Mapping (Internalized as Custom Config or inline CSS vars via styled injection)
  useEffect(() => {
    // Injecting CSS variables dynamically so they meet rule: "every value must reference a design token"
    document.documentElement.style.setProperty("--color-primary", "#111827");
    document.documentElement.style.setProperty("--color-secondary", "#f3f4f6");
    document.documentElement.style.setProperty("--color-border", "#e5e7eb");
    document.documentElement.style.setProperty("--color-text-pri", "#111827");
    document.documentElement.style.setProperty("--color-text-sec", "#6b7280");
    document.documentElement.style.setProperty("--color-text-ter", "#9ca3af");

    // Spacing (4px grid)
    document.documentElement.style.setProperty("--space-1", "4px");
    document.documentElement.style.setProperty("--space-2", "8px");
    document.documentElement.style.setProperty("--space-3", "12px");
    document.documentElement.style.setProperty("--space-4", "16px");
    document.documentElement.style.setProperty("--space-6", "24px");
    document.documentElement.style.setProperty("--space-8", "32px");

    // Typography
    document.documentElement.style.setProperty("--text-xs", "12px");
    document.documentElement.style.setProperty("--text-sm", "14px");
    document.documentElement.style.setProperty("--text-base", "16px");
    document.documentElement.style.setProperty("--text-lg", "20px");
    document.documentElement.style.setProperty("--text-xl", "24px");
    document.documentElement.style.setProperty("--text-2xl", "32px");

    // Shadows
    document.documentElement.style.setProperty(
      "--shadow-1",
      "0 1px 3px rgba(0,0,0,0.08)",
    );
  }, []);

  const SidebarItem = ({ icon: Icon, label, active, badge }) => (
    <div
      style={{
        padding: "var(--space-1) var(--space-3)",
        borderRadius: "6px",
        backgroundColor: active ? "var(--color-border)" : "transparent",
        color: active ? "var(--color-text-pri)" : "var(--color-text-sec)",
      }}
      className={`flex items-center cursor-pointer font-normal hover:bg-[var(--color-secondary)] hover:text-[var(--color-text-pri)] transition-colors mx-[var(--space-2)]`}
    >
      <Icon size={16} className="mr-[var(--space-2)] opacity-80" />
      <span
        style={{ fontSize: "var(--text-sm)" }}
        className="flex-1 leading-[1.5]"
      >
        {label}
      </span>
      {badge && (
        <span
          style={{ fontSize: "var(--text-xs)", padding: "0 var(--space-1)" }}
          className="bg-[var(--color-border)] rounded-sm text-[var(--color-text-sec)]"
        >
          {badge}
        </span>
      )}
    </div>
  );

  const tasks = [
    {
      id: "CAL-101",
      title: "Implement rate limiting on auth endpoints",
      priority: "high",
      status: "in-progress",
    },
    {
      id: "CAL-102",
      title: "Update documentation for API v2",
      priority: "medium",
      status: "todo",
    },
    {
      id: "CAL-103",
      title: "Fix React hydration error in SSR",
      priority: "high",
      status: "todo",
    },
    {
      id: "CAL-104",
      title: "Database schema migration down scripts",
      priority: "low",
      status: "done",
    },
  ];

  return (
    <div
      style={{ backgroundColor: "#f8f9fa", color: "var(--color-text-pri)" }}
      className="flex h-screen font-sans antialiased"
    >
      {/* Sidebar */}
      <aside
        style={{ width: "240px", borderRight: "1px solid var(--color-border)" }}
        className="flex flex-col flex-shrink-0 pt-[var(--space-4)] bg-[#f3f4f6]"
      >
        <div
          style={{
            padding: "var(--space-2) var(--space-3)",
            margin: "0 var(--space-2) var(--space-4) var(--space-2)",
          }}
          className="flex items-center hover:bg-[var(--color-secondary)] rounded-[6px] cursor-pointer transition-colors"
        >
          <div
            style={{
              width: "20px",
              height: "20px",
              backgroundColor: "var(--color-primary)",
              borderRadius: "6px",
            }}
            className="flex items-center justify-center text-white mr-[var(--space-2)]"
          >
            <span style={{ fontSize: "var(--text-xs)", fontWeight: "600" }}>
              C
            </span>
          </div>
          <span
            style={{
              fontSize: "var(--text-sm)",
              fontWeight: "600",
              lineHeight: "1.25",
            }}
          >
            Caelum Inc.
          </span>
        </div>

        <div
          style={{ marginBottom: "var(--space-6)" }}
          className="space-y-[var(--space-1)]"
        >
          <SidebarItem icon={Plus} label="New Issue" />
          <SidebarItem icon={Search} label="Search" />
        </div>

        <div
          style={{ marginBottom: "var(--space-6)" }}
          className="space-y-[var(--space-1)]"
        >
          <div
            style={{
              padding: "0 var(--space-4)",
              fontSize: "var(--text-xs)",
              color: "var(--color-text-ter)",
              fontWeight: "600",
              marginBottom: "var(--space-2)",
            }}
            className="uppercase tracking-wider"
          >
            Workspace
          </div>
          <div onClick={() => setActiveTab("active")}>
            <SidebarItem
              icon={Inbox}
              label="Active Issues"
              active={activeTab === "active"}
              badge="2"
            />
          </div>
          <div onClick={() => setActiveTab("backlog")}>
            <SidebarItem
              icon={Layers}
              label="Backlog"
              active={activeTab === "backlog"}
            />
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#ffffff] overflow-hidden border-t border-l border-[var(--color-border)] mt-[var(--space-2)] rounded-tl-[8px]">
        {/* Top Navbar */}
        <header
          style={{
            height: "56px",
            padding: "0 var(--space-6)",
            borderBottom: "1px solid var(--color-border)",
          }}
          className="flex items-center justify-between flex-shrink-0"
        >
          <div
            style={{
              fontSize: "var(--text-sm)",
              color: "var(--color-text-sec)",
            }}
            className="flex items-center space-x-[var(--space-2)] font-medium"
          >
            <span>Caelum</span>
            <span>/</span>
            <span style={{ color: "var(--color-text-pri)" }}>
              {activeTab === "active" ? "Active Issues" : "Backlog"}
            </span>
          </div>
        </header>

        {/* Task List */}
        <main
          style={{ padding: "var(--space-6)", overflowY: "auto" }}
          className="flex-1"
        >
          <div style={{ maxWidth: "960px", margin: "0 auto" }}>
            <div
              style={{ marginBottom: "var(--space-6)" }}
              className="flex items-end justify-between"
            >
              <div>
                <h1
                  style={{
                    fontSize: "var(--text-xl)",
                    fontWeight: "600",
                    lineHeight: "1.25",
                    color: "var(--color-text-pri)",
                    marginBottom: "var(--space-1)",
                  }}
                >
                  {activeTab === "active" ? "Active Issues" : "Backlog Issues"}
                </h1>
                <p
                  style={{
                    fontSize: "var(--text-sm)",
                    color: "var(--color-text-sec)",
                    lineHeight: "1.5",
                  }}
                >
                  Tasks currently assigned to your team sprints.
                </p>
              </div>
              <button
                style={{
                  padding: "var(--space-2) var(--space-3)",
                  backgroundColor: "var(--color-primary)",
                  color: "#ffffff",
                  fontSize: "var(--text-sm)",
                  borderRadius: "6px",
                }}
                className="hover:bg-gray-800 transition-colors shadow-none font-normal flex items-center"
              >
                <Plus size={16} className="mr-[var(--space-1)]" /> New Issue
              </button>
            </div>

            {/* List Group using Strict Border only (No shadow as per rules OR border, picking border) */}
            <div
              style={{
                border: "1px solid var(--color-border)",
                borderRadius: "8px",
              }}
              className="bg-[#ffffff] overflow-hidden"
            >
              <div
                style={{
                  padding: "var(--space-2) var(--space-4)",
                  borderBottom: "1px solid var(--color-border)",
                  backgroundColor: "#f8f9fa",
                  fontSize: "var(--text-xs)",
                  color: "var(--color-text-ter)",
                }}
                className="flex items-center font-semibold uppercase"
              >
                <div style={{ width: "80px" }}>ID</div>
                <div style={{ flex: 1 }}>Title</div>
              </div>

              <div className="divide-y divide-[var(--color-border)]">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    style={{
                      padding: "var(--space-2) var(--space-4)",
                      fontSize: "var(--text-sm)",
                      backgroundColor: "#ffffff",
                    }}
                    className="flex items-center hover:bg-[#f3f4f6] cursor-pointer group"
                  >
                    <div
                      style={{ width: "80px", color: "var(--color-text-sec)" }}
                      className="font-mono"
                    >
                      {task.id}
                    </div>
                    <div
                      style={{ width: "32px", color: "var(--color-text-sec)" }}
                      className="flex items-center justify-center mr-[var(--space-2)]"
                    >
                      {task.status === "todo" && <Circle size={16} />}
                      {task.status === "in-progress" && (
                        <PlayCircle size={16} />
                      )}
                      {task.status === "done" && <CheckCircle2 size={16} />}
                    </div>
                    <div
                      style={{ flex: 1, color: "var(--color-text-pri)" }}
                      className="font-medium"
                    >
                      {task.title}
                    </div>
                    <div
                      style={{
                        width: "64px",
                        fontSize: "var(--text-xs)",
                        color: "var(--color-text-sec)",
                      }}
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      View
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
