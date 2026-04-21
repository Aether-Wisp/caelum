
import re
import os

filepath = r'd:\1-compitition\waibao\caelum\scripts\update_preview_full.py'

with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Inject API_BASE
text = text.replace(
    'const { useState, useEffect } = React;',
    'const { useState, useEffect } = React;\n        const API_BASE = "http://127.0.0.1:8888/api";'
)

# 2. Rewrite TasksContent
tasks_new = """
        function TasksContent() {
          const [target, setTarget] = useState('');
          const [targets, setTargets] = useState(['192.168.1.100']);
          const [model, setModel] = useState('deepseek');
          
          const [progressData, setProgressData] = useState({ percentage: 0, status: '等待就绪', message: '请在左侧配置任务', current_stage: 'none' });
          const [sessionId, setSessionId] = useState(null);
          const [logs, setLogs] = useState([{type: "INFO", time: new Date().toLocaleTimeString(), text: "系统初始化完成"}]);

          const handleAdd = () => {
              if (target && !targets.includes(target)) {
                 setTargets([...targets, target]);
                 setTarget('');
              }
          };
          const handleRemove = (t) => {
              setTargets(targets.filter(item => item !== t));
          };

          const handleStart = async () => {
              if (targets.length === 0) return;
              setProgressData({ ...progressData, status: 'initializing', message: '正在下发目标分配...', percentage: 5 });
              setLogs(prev => [...prev, {type: "WAIT", time: new Date().toLocaleTimeString(), text: `开始针对 ${targets.length} 个目标下发任务`}]);
              
              try {
                  const res = await fetch(`${API_BASE}/automated-test/run`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ target: targets.join(','), model })
                  });
                  const data = await res.json();
                  if (data.success && data.jobs && data.jobs.length > 0) {
                      const sid = data.jobs[0].session_id; // Watch primary target
                      setSessionId(sid);
                      setLogs(prev => [...prev, {type: "INFO", time: new Date().toLocaleTimeString(), text: `任务已创建: ${sid}`}]);
                  } else {
                      setLogs(prev => [...prev, {type: "ERROR", time: new Date().toLocaleTimeString(), text: `启动失败: ${data.error || '未知错误'}`}]);
                  }
              } catch(e) {
                  setLogs(prev => [...prev, {type: "ERROR", time: new Date().toLocaleTimeString(), text: `网络请求失败: ${e.message}`}]);
              }
          };

          useEffect(() => {
              if (!sessionId) return;
              const timer = setInterval(async () => {
                  try {
                      const res = await fetch(`${API_BASE}/automated-test/progress/${sessionId}`);
                      const data = await res.json();
                      if (data.success && data.progress) {
                          setProgressData(data.progress);
                          const { status, message, percentage, current_stage } = data.progress;
                          
                          setLogs(prev => {
                              const lastLog = prev[prev.length - 1];
                              if (lastLog.text !== message) {
                                  return [...prev, { type: status === 'failed' ? 'ERROR' : 'INFO', time: new Date().toLocaleTimeString(), text: `[${current_stage}] ${message}` }];
                              }
                              return prev;
                          });

                          if (status === 'completed' || status === 'failed') {
                              clearInterval(timer);
                          }
                      }
                  } catch(e) {}
              }, 1500);
              return () => clearInterval(timer);
          }, [sessionId]);

          return (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full fade-in">
              {/* Left Column: New Task Card */}
              <div className="lg:col-span-4 space-y-6">
                <div className="linear-card p-6">
                  <h2 style={{ fontSize: 'var(--text-base)' }} className="font-semibold text-[var(--color-text-pri)] mb-6 flex items-center tracking-tight">
                    <Icon name="plus-circle" size={20} className="mr-3 text-[var(--color-text-sec)]" />
                    新建安全测试任务
                  </h2>

                  <div className="mb-6">
                    <label style={{ fontSize: 'var(--text-sm)' }} className="block font-medium text-[var(--color-text-pri)] mb-2">
                        测试目标 <span className="text-[var(--color-error)] ml-1">*</span>
                    </label>
                    <div className="flex space-x-2">
                        <input 
                            type="text" 
                            placeholder="如: example.com"
                            className="linear-input flex-1"
                            value={target}
                            onChange={e => setTarget(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleAdd()}
                        />
                        <button onClick={handleAdd} className="linear-btn-primary px-4 py-2">
                            <Icon name="plus" size={16} className="mr-1" />添加
                        </button>
                    </div>

                    <div className="mt-3 space-y-2 max-h-[120px] overflow-y-auto">
                        {targets.map((t, idx) => (
                           <div key={idx} style={{ backgroundColor: 'var(--color-secondary)', borderRadius: '6px', fontSize: 'var(--text-sm)' }} className="flex items-center justify-between px-3 py-2">
                               <span className="text-[var(--color-text-pri)]">{t}</span>
                               <button onClick={() => handleRemove(t)} className="text-[var(--color-text-ter)] hover:text-[var(--color-error)] transition-colors flex">
                                   <Icon name="x" size={14} />
                               </button>
                           </div>
                        ))}
                    </div>
                  </div>

                  <div className="mb-8">
                    <label style={{ fontSize: 'var(--text-sm)' }} className="block font-medium text-[var(--color-text-pri)] mb-3">
                        测试模型选择 <span className="text-[var(--color-error)] ml-1">*</span>
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
                          className={`p-3 text-center cursor-pointer transition-all ${model === m.id ? 'ring-1 ring-[var(--color-text-pri)] bg-gray-50' : 'hover:border-[var(--color-border-focus)] bg-white'}`}
                        >
                          <Icon name={m.icon} size={20} className={`mx-auto mb-2 ${model === m.id ? 'text-[var(--color-text-pri)]' : 'text-[var(--color-text-sec)]'}`} />
                          <div style={{ fontSize: 'var(--text-sm)' }} className={`font-semibold ${model === m.id ? 'text-[var(--color-text-pri)]' : 'text-[var(--color-text-sec)]'}`}>{m.label}</div>
                          <div style={{ fontSize: '11px' }} className="text-[var(--color-text-ter)] mt-1">{m.sub}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button onClick={handleStart} disabled={!!sessionId && progressData.status === 'running'} className="linear-btn-primary w-full py-3">
                      <Icon name={progressData.status === 'running' ? 'loader-2' : 'play'} size={18} className={`mr-2 ${progressData.status === 'running' ? 'animate-spin' : ''}`} /> 
                      {progressData.status === 'running' ? '测试进行中' : '开始自动化测试'}
                  </button>
                </div>
              </div>

              {/* Right Column */}
              <div className="lg:col-span-8 space-y-6 flex flex-col h-full">
                <div className="linear-card p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 style={{ fontSize: 'var(--text-base)' }} className="font-semibold text-[var(--color-text-pri)] flex items-center">
                            <Icon name="activity" size={20} className="mr-3 text-[var(--color-text-sec)]" />
                            任务状态监控
                        </h3>
                        <Badge type={progressData.status === 'completed' ? 'success' : progressData.status === 'failed' ? 'error' : progressData.status === 'running' ? 'warning' : 'default'}>
                            {progressData.status === 'completed' ? '已完成' : progressData.status === 'failed' ? '失败' : progressData.status === 'running' ? '运行中' : '等待就绪'}
                        </Badge>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span style={{ fontSize: 'var(--text-sm)' }} className="text-[var(--color-text-sec)]">测试进度 </span>
                                <span style={{ fontSize: 'var(--text-sm)' }} className="font-medium text-[var(--color-text-pri)]">{progressData.percentage}%</span>
                            </div>
                            <div style={{ backgroundColor: 'var(--color-secondary)', borderRadius: '4px', height: '6px' }} className="w-full overflow-hidden">
                                <div style={{ backgroundColor: 'var(--color-text-pri)', width: `${progressData.percentage}%`, height: '100%', borderRadius: '4px', transition: 'width 0.3s ease' }}></div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div style={{ border: '1px solid var(--color-border)', borderRadius: '6px' }} className="p-4 bg-gray-50 flex items-center justify-between">
                                <div>
                                  <div style={{ fontSize: '13px' }} className="text-[var(--color-text-sec)] mb-1">当前阶段检测</div>
                                  <div style={{ fontSize: '14px' }} className="font-semibold text-[var(--color-text-pri)]">{progressData.current_stage === 'none' ? '--' : progressData.current_stage}</div>
                                </div>
                                <Icon name="crosshair" size={24} className="text-[var(--color-text-ter)]" />
                            </div>
                            <div style={{ border: '1px solid var(--color-border)', borderRadius: '6px' }} className="p-4 bg-gray-50 flex items-center justify-between">
                                <div>
                                  <div style={{ fontSize: '13px' }} className="text-[var(--color-text-sec)] mb-1">执行状态信息</div>
                                  <div style={{ fontSize: '14px' }} className="font-semibold text-[var(--color-text-pri)] truncate max-w-[120px]">{progressData.message}</div>
                                </div>
                                <Icon name="check-circle" size={24} className="text-[var(--color-text-ter)]" />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="linear-card p-6 flex-1 flex flex-col">
                    <h3 style={{ fontSize: 'var(--text-base)' }} className="font-semibold text-[var(--color-text-pri)] mb-4 flex items-center">
                        <Icon name="file-text" size={20} className="mr-3 text-[var(--color-text-sec)]" />
                        测试报告日志
                    </h3>
                    
                    <div style={{ backgroundColor: '#111827', borderRadius: '6px', border: '1px solid var(--color-border)' }} className="flex-1 p-4 overflow-y-auto mb-5 min-h-[200px]">
                        <div style={{ fontSize: '13px' }} className="font-mono text-[#9ca3af] space-y-2">
                            {logs.map((log, i) => (
                                <div key={i}>
                                    <span className="text-[#6b7280] mr-2">[{log.time}]</span>
                                    <span className={log.type === 'ERROR' ? 'text-[var(--color-error)]' : log.type === 'INFO' ? 'text-[var(--color-success)]' : 'text-[#3b82f6]'}>[{log.type}]</span> 
                                    <span className="ml-2">{log.text}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex space-x-4">
                        <button className="linear-btn-secondary flex-1 py-2">
                          查看详细报告 ({sessionId ? sessionId.substr(0,8) : '暂无'}...)
                        </button>
                        <button className="linear-btn-secondary flex-1 py-2" onClick={() => window.open(`${API_BASE}/automated-test/report/${sessionId}`)}>
                          <Icon name="download" size={16} className="mr-2" />下载 PDF
                        </button>
                    </div>
                </div>
              </div>
            </div>
          );
        }
"""

text = re.sub(r'function TasksContent\(\) \{.*?(?=\s+// 2\. Payload Content)', tasks_new, text, flags=re.DOTALL)

# 3. Rewrite Payload Content
payload_new = """
        function PayloadContent() {
          const [generating, setGenerating] = useState(false);
          const [payloadType, setPayloadType] = useState('xss');
          const [paramsFormat, setParamsFormat] = useState('{\\n  "difficulty": "advanced",\\n  "count": 3\\n}');
          const [payloadResult, setPayloadResult] = useState('');

          const handleGenerate = async () => {
             setGenerating(true);
             try {
                // Parse optional params
                let payloadParams = { difficulty: "basic", count: 1 };
                try { payloadParams = JSON.parse(paramsFormat); } catch(e) {}

                const res = await fetch(`${API_BASE}/payloads/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: payloadType, ...payloadParams })
                });
                const data = await res.json();
                if (data.success && data.payloads) {
                    setPayloadResult(data.payloads.join("\\n\\n"));
                } else {
                    setPayloadResult(`Error: ${data.error}`);
                }
             } catch(e) {
                 setPayloadResult(`Network Error: ${e.message}`);
             }
             setGenerating(false);
          };

          return (
            <div className="linear-card p-8 max-w-[1000px] mx-auto fade-in">
              <h2 style={{ fontSize: 'var(--text-lg)' }} className="font-semibold text-[var(--color-text-pri)] mb-8 flex items-center tracking-tight">
                  <Icon name="terminal-square" size={24} className="mr-3 text-[var(--color-text-sec)]" />
                  Payload 智能生成器
              </h2>
              
              <div className="space-y-8">
                  <div>
                      <label style={{ fontSize: 'var(--text-sm)' }} className="block font-medium text-[var(--color-text-pri)] mb-3">目标 Payload 类型</label>
                      <div className="relative">
                          <select value={payloadType} onChange={e => setPayloadType(e.target.value)} className="linear-input w-full appearance-none pr-10 bg-white cursor-pointer py-3">
                              <option value="sqli">SQL Injection (SQLi)</option>
                              <option value="xss">Cross-Site Scripting (XSS)</option>
                              <option value="rce">Command Injection (RCE)</option>
                              <option value="lfi">Local File Inclusion (LFI)</option>
                          </select>
                          <Icon name="chevron-down" size={18} className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--color-text-ter)] pointer-events-none" />
                      </div>
                  </div>

                  <div>
                      <label style={{ fontSize: 'var(--text-sm)' }} className="block font-medium text-[var(--color-text-pri)] mb-3">特征参数配置 (JSON)</label>
                      <textarea 
                          rows="6" 
                          className="linear-input w-full font-mono py-3" 
                          value={paramsFormat}
                          onChange={e => setParamsFormat(e.target.value)}
                      ></textarea>
                      <p style={{ fontSize: '12px' }} className="text-[var(--color-text-ter)] mt-2">填写 JSON 格式以配置服务端生成难度与数量（支持 basic/advanced, count）</p>
                  </div>

                  <div>
                      <button onClick={handleGenerate} disabled={generating} className="linear-btn-primary w-full py-3 text-base">
                          {generating ? <Icon name="loader-2" className="mr-2 animate-spin" /> : <Icon name="rocket" className="mr-2" />}
                          {generating ? '模型生成中...' : '通过后端 API 生成'}
                      </button>
                  </div>

                  <div className="pt-8 border-t border-[var(--color-border)]">
                      <label style={{ fontSize: 'var(--text-sm)' }} className="block font-medium text-[var(--color-text-pri)] mb-3">生成结果回显</label>
                      <div className="relative">
                          <textarea 
                              value={payloadResult}
                              readOnly
                              rows="8" 
                              className="linear-input w-full font-mono bg-[#f9fafb] py-3 text-[#111827]"
                              placeholder="点击上方生成按钮获取结果..."
                          ></textarea>
                          <button onClick={() => navigator.clipboard.writeText(payloadResult)} className="linear-btn-secondary absolute top-2 right-2 p-2 min-w-0" title="复制">
                              <Icon name="copy" size={16} />
                          </button>
                      </div>
                  </div>
              </div>
            </div>
          );
        }
"""
text = re.sub(r'function PayloadContent\(\) \{.*?(?=\s+// 3\. History Content)', payload_new, text, flags=re.DOTALL)

# 4. Rewrite History Content
history_new = """
        function HistoryContent() {
           const [logs, setLogs] = useState([]);
           const [loading, setLoading] = useState(true);

           // Fetch exactly on component mount
           useEffect(() => {
               const loadHistory = async () => {
                   setLoading(true);
                   try {
                       const res = await fetch(`${API_BASE}/automated-test/history`);
                       const data = await res.json();
                       if (data.success && data.history) {
                           // Map backend fields to UI fields
                           const formatted = data.history.map(item => ({
                               ip: item.target || item.session_id.substring(0, 15),
                               time: new Date(item.start_time).toLocaleString('zh-CN'),
                               level: item.status === 'completed' ? 'success' : item.status === 'failed' ? 'severe' : 'high',
                               statusText: item.status,
                               sid: item.session_id
                           }));
                           setLogs(formatted.reverse());
                       }
                   } catch(e) {
                       console.error("Failed to load history", e);
                   }
                   setLoading(false);
               };
               loadHistory();
           }, []);

           return (
             <div className="linear-card p-6 flex flex-col h-full min-h-[600px] fade-in max-w-[1200px] mx-auto">
                <div className="flex justify-between items-center mb-6 border-b border-[var(--color-border)] pb-6">
                    <h2 style={{ fontSize: 'var(--text-lg)' }} className="font-semibold text-[var(--color-text-pri)] flex items-center tracking-tight">
                        <Icon name="clipboard-list" size={24} className="mr-3 text-[var(--color-text-sec)]" />
                        后端 API 测试记录同步
                    </h2>
                    
                    <div className="flex space-x-3">
                        <div className="relative w-[280px]">
                            <Icon name="search" size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-ter)]" />
                            <input type="text" placeholder="搜索目标或 Session ID..." className="linear-input w-full pl-9 py-2" />
                        </div>
                        <button className="linear-btn-secondary px-4 py-2 text-[var(--color-text-sec)]" onClick={() => window.location.reload()}>
                            <Icon name="refresh-cw" size={16} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
                            强制刷新
                        </button>
                        <button className="linear-btn-primary px-4 py-2">
                            <Icon name="download" size={16} className="mr-2" />
                            导出全部
                        </button>
                    </div>
                </div>

                <div className="flex-1 w-full overflow-hidden flex flex-col border border-[var(--color-border)] rounded-lg">
                    <div className="flex-1 overflow-x-auto overflow-y-auto w-full bg-white">
                        <table className="w-full text-left whitespace-nowrap">
                            <thead className="bg-[#f9fafb] text-[var(--color-text-sec)] sticky top-0 z-10 border-b border-[var(--color-border)]">
                                <tr>
                                    <th style={{ fontSize: '13px' }} className="font-medium px-6 py-4">检测目标 / ID</th>
                                    <th style={{ fontSize: '13px' }} className="font-medium px-6 py-4">任务启动时间</th>
                                    <th style={{ fontSize: '13px' }} className="font-medium px-6 py-4">运行状态</th>
                                    <th style={{ fontSize: '13px' }} className="font-medium px-6 py-4 text-center">操作集</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[var(--color-border)]">
                                {logs.length === 0 && !loading && (
                                   <tr><td colSpan="4" className="text-center py-10 text-gray-400">目前暂无任务记录，请通过「测试任务」发起测试以生成后端数据</td></tr>
                                )}
                                {loading && logs.length === 0 && (
                                   <tr><td colSpan="4" className="text-center py-10 text-gray-400"><Icon name="loader" className="animate-spin inline mr-2" /> 正在从后端拉取记录...</td></tr>
                                )}
                                {logs.map((log, i) => (
                                    <tr key={i} className="hover:bg-[#f9fafb] transition-colors group cursor-pointer text-[var(--text-sm)]">
                                        <td className="px-6 py-4 font-medium text-[var(--color-text-pri)] flex items-center">
                                           <Icon name="server" size={16} className="mr-2 text-[var(--color-text-ter)] group-hover:text-[var(--color-text-pri)] transition-colors" /> {log.ip}
                                        </td>
                                        <td className="px-6 py-4 text-[var(--color-text-sec)]">{log.time}</td>
                                        <td className="px-6 py-4">
                                            <Badge type={log.level}>{log.statusText || 'unknown'}</Badge>
                                        </td>
                                        <td className="px-6 py-4 text-center space-x-3">
                                            <button className="text-[var(--color-text-sec)] hover:text-[var(--color-text-pri)] font-medium transition-colors" title={`SID: ${log.sid}`}>会话详情</button>
                                            <a href={`${API_BASE}/automated-test/report/${log.sid}`} target="_blank" className="text-[var(--color-text-sec)] hover:text-[var(--color-text-pri)] font-medium transition-colors inline-block">JSON 报表</a>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="flex items-center justify-between pt-4 mt-4 border-t border-[var(--color-border)]">
                    <span style={{ fontSize: '13px' }} className="text-[var(--color-text-sec)] font-medium">
                        共从后端同步到 <span className="text-[var(--color-text-pri)] font-semibold mx-1">{logs.length}</span> 项记录
                    </span>
                    
                    <div className="flex items-center space-x-2">
                        <button className="linear-btn-secondary px-2 py-1" disabled>
                            <Icon name="chevron-left" size={16} />
                        </button>
                        <div style={{ fontSize: '13px' }} className="px-3 py-1 font-medium bg-[#f3f4f6] rounded border border-[var(--color-border)]">
                            1 / 1
                        </div>
                        <button className="linear-btn-secondary px-2 py-1" disabled>
                            <Icon name="chevron-right" size={16} />
                        </button>
                    </div>
                </div>
             </div>
           );
        }
"""
text = re.sub(r'function HistoryContent\(\) \{.*?(?=\s+// Main App)', history_new, text, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch applied.")
