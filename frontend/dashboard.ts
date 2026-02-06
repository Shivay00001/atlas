import React, { useState, useEffect, useRef } from 'react';
import { Play, Mic, Send, Activity, Zap, Shield, Smartphone } from 'lucide-react';

interface CommandLog {
  timestamp: string;
  command: string;
  status: 'success' | 'error' | 'running';
  message: string;
  duration?: number;
}

interface SystemStatus {
  permissions: Record<string, boolean>;
  services: {
    android_connected: boolean;
    enterchat_connected: boolean;
  };
}

const Dashboard: React.FC = () => {
  const [command, setCommand] = useState('');
  const [logs, setLogs] = useState<CommandLog[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isListening, setIsListening] = useState(false);
  
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Auto-scroll logs
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/status');
      const data = await response.json();
      if (data.success) {
        setStatus(data.status);
      }
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  };

  const executeCommand = async (dryRun = false) => {
    if (!command.trim()) return;

    setIsExecuting(true);
    
    const newLog: CommandLog = {
      timestamp: new Date().toISOString(),
      command: command,
      status: 'running',
      message: 'Processing...'
    };
    
    setLogs(prev => [...prev, newLog]);

    try {
      const response = await fetch('http://localhost:8000/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, dry_run: dryRun })
      });

      const data = await response.json();

      setLogs(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...newLog,
          status: data.success ? 'success' : 'error',
          message: data.message || JSON.stringify(data),
          duration: data.execution?.duration_ms
        };
        return updated;
      });

      if (!dryRun) {
        setCommand('');
      }
    } catch (error: any) {
      setLogs(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...newLog,
          status: 'error',
          message: error.message || 'Execution failed'
        };
        return updated;
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const startVoiceInput = () => {
    setIsListening(true);
    // In production, implement Web Speech API
    setTimeout(() => {
      setIsListening(false);
      setCommand('Screenshot lena aur desktop organize karna');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/30 backdrop-blur border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">ShivAI Atlas</h1>
                <p className="text-xs text-gray-400">Local AI Agent OS</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <StatusIndicator
                icon={<Shield className="w-4 h-4" />}
                label="Permissions"
                active={status?.permissions?.files}
              />
              <StatusIndicator
                icon={<Smartphone className="w-4 h-4" />}
                label="Android"
                active={status?.services?.android_connected}
              />
              <StatusIndicator
                icon={<Activity className="w-4 h-4" />}
                label="EnterChat"
                active={status?.services?.enterchat_connected}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Command Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Command Input */}
            <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4">Command Center</h2>
              
              <div className="space-y-4">
                <div className="relative">
                  <textarea
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey) {
                        executeCommand(false);
                      }
                    }}
                    placeholder="Enter command in Hindi or English... (Ctrl+Enter to execute)"
                    className="w-full bg-black/30 text-white rounded-xl p-4 pr-12 border border-white/10 focus:border-purple-500 focus:outline-none resize-none"
                    rows={3}
                    disabled={isExecuting}
                  />
                  
                  <button
                    onClick={startVoiceInput}
                    disabled={isListening || isExecuting}
                    className={`absolute right-3 top-3 p-2 rounded-lg transition-all ${
                      isListening
                        ? 'bg-red-500 animate-pulse'
                        : 'bg-white/10 hover:bg-white/20'
                    }`}
                  >
                    <Mic className={`w-5 h-5 ${isListening ? 'text-white' : 'text-gray-300'}`} />
                  </button>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => executeCommand(false)}
                    disabled={isExecuting || !command.trim()}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl flex items-center justify-center gap-2 transition-all"
                  >
                    <Play className="w-5 h-5" />
                    Execute
                  </button>
                  
                  <button
                    onClick={() => executeCommand(true)}
                    disabled={isExecuting || !command.trim()}
                    className="bg-white/10 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-all"
                  >
                    Dry Run
                  </button>
                </div>
              </div>
            </div>

            {/* Activity Log */}
            <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4">Activity Log</h2>
              
              <div
                ref={logContainerRef}
                className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar"
              >
                {logs.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    No commands executed yet
                  </div>
                ) : (
                  logs.map((log, index) => (
                    <LogEntry key={index} log={log} />
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
              
              <div className="space-y-2">
                <QuickAction
                  label="Take Screenshot"
                  onClick={() => setCommand('Screenshot lo')}
                />
                <QuickAction
                  label="Organize Desktop"
                  onClick={() => setCommand('Desktop organize karo')}
                />
                <QuickAction
                  label="Open Calculator"
                  onClick={() => setCommand('Calculator kholo')}
                />
                <QuickAction
                  label="System Info"
                  onClick={() => setCommand('System info dikao')}
                />
                <QuickAction
                  label="Check Messages"
                  onClick={() => setCommand('Messages check karo')}
                />
              </div>
            </div>

            {/* Recent Workflows */}
            <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Workflows</h3>
              
              <div className="space-y-2">
                <WorkflowItem name="Morning Routine" usage={12} />
                <WorkflowItem name="Backup Workflow" usage={8} />
                <WorkflowItem name="Productivity Setup" usage={15} />
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </div>
  );
};

const StatusIndicator: React.FC<{
  icon: React.ReactNode;
  label: string;
  active?: boolean;
}> = ({ icon, label, active }) => (
  <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded-lg">
    <div className={`${active ? 'text-green-400' : 'text-gray-500'}`}>
      {icon}
    </div>
    <span className="text-sm text-gray-300">{label}</span>
    <div className={`w-2 h-2 rounded-full ${active ? 'bg-green-400' : 'bg-gray-600'}`} />
  </div>
);

const LogEntry: React.FC<{ log: CommandLog }> = ({ log }) => {
  const statusColors = {
    running: 'border-yellow-500 bg-yellow-500/10',
    success: 'border-green-500 bg-green-500/10',
    error: 'border-red-500 bg-red-500/10'
  };

  return (
    <div className={`p-4 rounded-lg border ${statusColors[log.status]}`}>
      <div className="flex items-start justify-between mb-2">
        <span className="text-sm font-mono text-white">{log.command}</span>
        <span className="text-xs text-gray-400">
          {new Date(log.timestamp).toLocaleTimeString()}
        </span>
      </div>
      <div className="text-sm text-gray-300">{log.message}</div>
      {log.duration && (
        <div className="text-xs text-gray-400 mt-1">Duration: {log.duration}ms</div>
      )}
    </div>
  );
};

const QuickAction: React.FC<{ label: string; onClick: () => void }> = ({ label, onClick }) => (
  <button
    onClick={onClick}
    className="w-full text-left px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg text-white transition-all"
  >
    {label}
  </button>
);

const WorkflowItem: React.FC<{ name: string; usage: number }> = ({ name, usage }) => (
  <div className="flex items-center justify-between px-4 py-3 bg-white/5 rounded-lg">
    <span className="text-white">{name}</span>
    <span className="text-sm text-gray-400">{usage}x</span>
  </div>
);

export default Dashboard;
