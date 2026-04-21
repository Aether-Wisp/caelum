import os

html_content = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Linear Board - React 实时预览</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- React & ReactDOM -->
    <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
    <!-- Babel for parsing JSX in browser -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
      /* 严格遵守设计的 CSS variables */
      :root {
        --color-primary: #111827;
        --color-secondary: #f3f4f6;
        --color-border: #e5e7eb;
        --color-text-pri: #111827;
        --color-text-sec: #6b7280;
        --color-text-ter: #9ca3af;
        --color-success: #10b981;
        
        --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px; --space-6: 24px; --space-8: 32px;
        --text-xs: 12px; --text-sm: 14px; --text-base: 16px; --text-lg: 20px; --text-xl: 24px; --text-2xl: 32px;
        
        --shadow-1: 0 1px 3px rgba(0,0,0,0.08);
      }
      body {
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      }
    </style>
</head>
<body class="bg-[#f8f9fa] m-0 p-0 overflow-hidden text-[#111827]">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;
        
        function Icon({ name, size = 16, className = "", style = {} }) {
          useEffect(() => {
            lucide.createIcons();
          }, [name]);
          return <i data-lucide={name} style={{ width: size, height: size, ...style }} className={className}></i>;
        }

        const SidebarItem = ({ iconName, label, active }) => (
            <div style={{ 
                padding: '10px var(--space-4)', 
                backgroundColor: active ? 'var(--color-secondary)' : 'transparent', 
                color: active ? 'var(--color-text-pri)' : 'var(--color-text-sec)' 
            }} className={`flex items-center cursor-pointer font-medium hover:bg-[#e5e7eb] transition-colors rounded-[6px] mx-[var(--space-2)] mb-[var(--space-1)]`}> 
              <Icon name={iconName} size={18} className="mr-[var(--space-3)] opacity-90" />
              <span style={{ fontSize: 'var(--text-sm)' }} className="flex-1 leading-[1.5]">{label}</span>
            </div>
        );

        // 结合后的卡片式主内容布局组件
        function DashboardContent() {
          const [target, setTarget] = useState('192.168.1.100');
          const [model, setModel] = useState('deepseek');

          return (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full fade-in">
              {/* Left Column: New Task Card */}
              <div className="lg:col-span-4 space-y-6">
                <div style={{ border: '1px solid var(--color-border)', borderRadius: '8px', boxShadow: 'var(--shadow-1)' }} className="bg-white p-6">
                  <h2 style={{ fontSize: 'var(--text-base)' }} className="font-semibold text-[var(--color-text-pri)] mb-6 flex items-center tracking-tight">
                    <Icon name="plus-circle" size={20} className="mr-3 text-[var(--color-text-sec)]" />
                    新建安全测试任务
                  </h2>

                  {/* Target Input */}
                  <div className="mb-6">
                    <label style={{ fontSize: 'var(--text-sm)' }} className="block font-medium text-[var(--color-text-pri)] mb-3">
                        测试目标 <span className="text-red-500 ml-1">*</span>
                    </label>
                    <div className="flex space-x-2">
                        <input 
                            type="text" 
                            placeholder="如: example.com"
                            style={{ border: '1px solid var(--color-border)', borderRadius: '6px', fontSize: 'var(--text-sm)' }}
                            className="flex-1 px-3 py-2 text-[var(--color-text-pri)] placeholder-[var(--color-text-ter)] outline-none focus:border-[var(--color-text-pri)] focus:ring-1 focus:ring-[var(--color-text-pri)] transition-all"
                        />
                        <button style={{ backgroundColor: 'var(--color-text-pri)', borderRadius: '6px', fontSize: 'var(--text-sm)' }} className="text-white px-4 py-2 font-medium hover:bg-gray-800 transition-colors flex items-center">
                            <Icon name="plus" size={16} className="mr-1" />添加
                        </button>
                    </div>

                    <div className="mt-4 space-y-2">
                        <div style={{ backgroundColor: 'var(--color-secondary)', borderRadius: '6px', fontSize: 'var(--text-sm)' }} className="flex items-center justify-between px-3 py-2 border border-transparent">
                            <span className="text-[var(--color-text-pri)]">{target}</span>
                            <button className="text-[var(--color-text-ter)] hover:text-red-500 transition-colors display-flex">
                                <Icon name="x" size={14} />
                            </button>
                        </div>
                    </div>
                  </div>

                  {/* Model Selection */}
                  <div className="mb-8">
                    <label style={{ fontSize: 'var(--text-sm)' }} className="block font-medium text-[var(--color-text-pri)] mb-3">
                        测试模型选择 <span className="text-red-500 ml-1">*</span>
                    </label>
                    <div className="grid grid-cols-3 gap-3">
                      {[
                        { id: 'deepseek', label: 'DeepSeek', sub: '深度推理', icon: 'brain' },
                        { id: 'chatgpt', label: 'ChatGPT', sub: '通用智能', icon: 'sparkles' },
                        { id: 'claude', label: 'Claude', sub: '安全专家', icon: 'zap' }
                      ].map(m => (
                        <div 
                          key={m.id} 
                          onClick={() => setModel(m.id)}
                          style={{ borderRadius: '6px', borderWidth: '1px', borderStyle: 'solid', borderColor: model === m.id ? 'var(--color-text-pri)' : 'var(--color-border)' }} 
                          className={`p-3 text-center cursor-pointer transition-all ${model === m.id ? 'ring-1 ring-[var(--color-text-pri)] bg-gray-50' : 'hover:border-gray-400 bg-white'}`}
                        >
                          <Icon name={m.icon} size={20} className={`mx-auto mb-2 ${model === m.id ? 'text-[var(--color-text-pri)]' : 'text-[var(--color-text-sec)]'}`} />
                          <div style={{ fontSize: 'var(--text-sm)' }} className={`font-semibold ${model === m.id ? 'text-[var(--color-text-pri)]' : 'text-[var(--color-text-sec)]'}`}>{m.label}</div>
                          <div style={{ fontSize: '11px' }} className="text-[var(--color-text-ter)] mt-1">{m.sub}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Start Button */}
                  <button style={{ backgroundColor: 'var(--color-text-pri)', borderRadius: '6px', fontSize: 'var(--text-base)' }} className="w-full text-white py-3 font-medium hover:bg-gray-800 transition-colors flex items-center justify-center">
                      <Icon name="play" size={18} className="mr-2" /> 开始测试
                  </button>
                </div>
              </div>

              {/* Right Column: Status & Logs */}
              <div className="lg:col-span-8 space-y-6 flex flex-col h-full">
                
                {/* Task Monitor */}
                <div style={{ border: '1px solid var(--color-border)', borderRadius: '8px', boxShadow: 'var(--shadow-1)' }} className="bg-white p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 style={{ fontSize: 'var(--text-base)' }} className="font-semibold text-[var(--color-text-pri)] flex items-center">
                            <Icon name="activity" size={20} className="mr-3 text-[var(--color-text-sec)]" />
                            任务状态监控
                        </h3>
                        <span style={{ fontSize: '12px', padding: '4px 10px', backgroundColor: 'var(--color-secondary)' }} className="rounded-full text-[var(--color-text-sec)] font-medium border border-[var(--color-border)]">
                            等待就绪
                        </span>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span style={{ fontSize: 'var(--text-sm)' }} className="text-[var(--color-text-sec)]">测试进度</span>
                                <span style={{ fontSize: 'var(--text-sm)' }} className="font-semibold text-[var(--color-text-pri)]">0%</span>
                            </div>
                            <div style={{ backgroundColor: 'var(--color-secondary)', borderRadius: '4px', height: '6px' }} className="w-full overflow-hidden">
                                <div style={{ backgroundColor: 'var(--color-text-pri)', width: '0%', height: '100%', borderRadius: '4px', transition: 'width 0.3s ease' }}></div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div style={{ border: '1px solid var(--color-border)', borderRadius: '6px' }} className="p-4 bg-gray-50 flex items-center justify-between">
                                <div>
                                  <div style={{ fontSize: '13px' }} className="text-[var(--color-text-sec)] mb-1">检测项总计</div>
                                  <div style={{ fontSize: 'var(--text-xl)' }} className="font-bold text-[var(--color-text-pri)]">0</div>
                                </div>
                                <Icon name="crosshair" size={24} className="text-[var(--color-border)]" />
                            </div>
                            <div style={{ border: '1px solid var(--color-border)', borderRadius: '6px' }} className="p-4 bg-gray-50 flex items-center justify-between">
                                <div>
                                  <div style={{ fontSize: '13px' }} className="text-[var(--color-text-sec)] mb-1">已完成项</div>
                                  <div style={{ fontSize: 'var(--text-xl)' }} className="font-bold text-[var(--color-text-pri)]">0</div>
                                </div>
                                <Icon name="check-circle" size={24} className="text-[var(--color-border)]" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Log Report */}
                <div style={{ border: '1px solid var(--color-border)', borderRadius: '8px', boxShadow: 'var(--shadow-1)' }} className="bg-white p-6 flex-1 flex flex-col">
                    <h3 style={{ fontSize: 'var(--text-base)' }} className="font-semibold text-[var(--color-text-pri)] mb-4 flex items-center">
                        <Icon name="file-text" size={20} className="mr-3 text-[var(--color-text-sec)]" />
                        测试报告日志
                    </h3>
                    
                    <div style={{ backgroundColor: '#1e1e1e', borderRadius: '6px' }} className="flex-1 p-4 overflow-y-auto mb-5 min-h-[200px]">
                        <div style={{ fontSize: '13px' }} className="font-mono text-[#a3a3a3] space-y-2">
                            <div><span className="text-[#10b981]">[INFO]</span> 正在初始化系统环境...</div>
                            <div><span className="text-[#3b82f6]">[WAIT]</span> 等待下发测试指令</div>
                        </div>
                    </div>

                    <div className="flex space-x-4">
                        <button style={{ border: '1px solid var(--color-border)', borderRadius: '6px', fontSize: 'var(--text-sm)' }} className="flex-1 py-2 font-medium bg-white hover:bg-gray-50 transition-colors text-[var(--color-text-pri)]">
                          查看详细报告
                        </button>
                        <button style={{ border: '1px solid var(--color-border)', borderRadius: '6px', fontSize: 'var(--text-sm)' }} className="flex-1 py-2 font-medium bg-white hover:bg-gray-50 transition-colors text-[var(--color-text-pri)] flex justify-center items-center">
                          <Icon name="download" size={16} className="mr-2" />下载 PDF
                        </button>
                    </div>
                </div>
              </div>
            </div>
          );
        }

        function App() {
          const [activeTab, setActiveTab] = useState('tasks');

          return (
            <div style={{ backgroundColor: '#f8f9fa' }} className="flex h-screen w-screen font-sans antialiased text-[#111827]">
              {/* Sidebar Layout */}
              <aside style={{ width: '260px', borderRight: '1px solid var(--color-border)' }} className="flex flex-col flex-shrink-0 bg-[#ffffff] z-10">
                <div className="h-[64px] flex items-center px-6 border-b border-[var(--color-border)] mb-4">
                  <div style={{ width: '28px', height: '28px', backgroundColor: 'var(--color-primary)', borderRadius: '6px' }} className="flex items-center justify-center text-white mr-3">
                    <span style={{ fontSize: 'var(--text-sm)', fontWeight: '700' }}>C</span>
                  </div>
                  <span style={{ fontSize: '18px', fontWeight: '700', letterSpacing: '-0.025em' }}>Caelum</span>
                </div>

                <div className="flex-1 overflow-y-auto px-2 space-y-1">
                  <div onClick={() => setActiveTab('tasks')}>
                    <SidebarItem iconName="shield-check" label="测试任务" active={activeTab === 'tasks'} />
                  </div>
                  <div onClick={() => setActiveTab('payload')}>
                    <SidebarItem iconName="terminal-square" label="Payload生成" active={activeTab === 'payload'} />
                  </div>
                  <div onClick={() => setActiveTab('history')}>
                    <SidebarItem iconName="history" label="历史日志" active={activeTab === 'history'} />
                  </div>
                </div>
              </aside>

              {/* Main App Area */}
              <div className="flex-1 flex flex-col min-w-0 bg-[#f8f9fa] overflow-hidden">
                {/* Header Navbar */}
                <header style={{ height: '64px', borderBottom: '1px solid var(--color-border)' }} className="bg-[#ffffff] flex items-center justify-between px-8 flex-shrink-0 z-10">
                  <h1 style={{ fontSize: 'var(--text-lg)' }} className="font-semibold text-[var(--color-text-pri)] tracking-tight">安全测试任务</h1>
                  
                  <div className="flex items-center space-x-5">
                    <button className="text-[var(--color-text-sec)] hover:text-[var(--color-text-pri)] transition-colors relative">
                        <Icon name="bell" size={20} />
                        <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                    </button>
                    <div style={{ padding: '4px 12px 4px 4px', border: '1px solid var(--color-border)', borderRadius: '24px' }} className="flex items-center cursor-pointer hover:bg-gray-50 transition-colors">
                        <div style={{ width: '28px', height: '28px', backgroundColor: 'var(--color-secondary)', borderRadius: '50%' }} className="flex items-center justify-center text-[var(--color-text-pri)] text-sm font-semibold mr-2 border border-[var(--color-border)]">
                            A
                        </div>
                        <span style={{ fontSize: 'var(--text-sm)' }} className="font-medium text-[var(--color-text-pri)]">Admin</span>
                    </div>
                  </div>
                </header>

                {/* Content Grid Area */}
                <main className="flex-1 overflow-y-auto p-6 md:p-8">
                  <div className="max-w-[1400px] mx-auto h-full">
                    {activeTab === 'tasks' && <DashboardContent />}
                    {activeTab !== 'tasks' && (
                      <div style={{ border: '1px solid var(--color-border)', borderRadius: '8px', boxShadow: 'var(--shadow-1)' }} className="bg-white p-12 text-center text-gray-500 mt-10">
                        <Icon name="layout-dashboard" size={48} className="mx-auto mb-4 text-gray-300" />
                        <p>内容占位符 - (受严格 Linear 规则控制的设计模板)</p>
                      </div>
                    )}
                  </div>
                </main>
              </div>
            </div>
          );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>'''

with open(r'd:\1-compitition\waibao\caelum\HTML\react-preview.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("react-preview.html replaced completely.")
