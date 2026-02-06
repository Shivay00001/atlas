import React, { useEffect, useState, useRef } from 'react';
import ReactDOM from 'react-dom/client';
import {
    Terminal,
    Cpu,
    HardDrive,
    Folder,
    File,
    MessageSquare,
    Send,
    Settings,
    Activity,
    Search,
    Menu,
    X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';

// --- Types ---
interface SystemInfo {
    platform: string;
    processor: string;
    ram_total: string;
    ram_available: string;
    ram_percent: number;
    disk_usage: string;
    disk_percent: number;
    cpu_percent: number;
}

interface FileItem {
    name: string;
    path: string;
    type: 'file' | 'directory';
    size?: number;
    modified?: number;
}

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

// --- Components ---

const Sidebar = ({ activeTab, setActiveTab }: { activeTab: string, setActiveTab: (t: string) => void }) => {
    const tabs = [
        { id: 'dashboard', icon: Activity, label: 'Dashboard' },
        { id: 'files', icon: Folder, label: 'File Explorer' },
        { id: 'chat', icon: MessageSquare, label: 'AI Chat' },
        { id: 'terminal', icon: Terminal, label: 'Task Manager' },
    ];

    return (
        <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-screen">
            <div className="p-6 flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <Cpu className="text-white w-5 h-5" />
                </div>
                <h1 className="text-xl font-bold text-white tracking-tight">Atlas Pro</h1>
            </div>

            <nav className="flex-1 px-4 space-y-2">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${activeTab === tab.id
                                ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20'
                                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                            }`}
                    >
                        <tab.icon className="w-5 h-5" />
                        <span className="font-medium">{tab.label}</span>
                    </button>
                ))}
            </nav>

            <div className="p-4 border-t border-gray-800">
                <div className="flex items-center gap-3 px-4 py-3">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-sm text-gray-400">System Online</span>
                </div>
            </div>
        </div>
    );
};

const Dashboard = () => {
    const [info, setInfo] = useState<SystemInfo | null>(null);

    useEffect(() => {
        const fetchInfo = async () => {
            try {
                const res = await fetch('http://localhost:8001/system-info');
                const data = await res.json();
                setInfo(data);
            } catch (e) {
                console.error(e);
            }
        };
        fetchInfo();
        const interval = setInterval(fetchInfo, 2000);
        return () => clearInterval(interval);
    }, []);

    if (!info) return <div className="p-8 text-gray-400">Loading system metrics...</div>;

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white mb-6">System Overview</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* CPU Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gray-800/50 border border-gray-700 p-6 rounded-2xl backdrop-blur-sm"
                >
                    <div className="flex justify-between items-start mb-4">
                        <div className="p-3 bg-purple-500/10 rounded-lg">
                            <Cpu className="w-6 h-6 text-purple-400" />
                        </div>
                        <span className="text-2xl font-bold text-white">{info.cpu_percent}%</span>
                    </div>
                    <h3 className="text-gray-400 font-medium">CPU Usage</h3>
                    <div className="mt-4 w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-purple-500 transition-all duration-500"
                            style={{ width: `${info.cpu_percent}%` }}
                        />
                    </div>
                    <p className="mt-2 text-xs text-gray-500 truncate">{info.processor}</p>
                </motion.div>

                {/* RAM Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-gray-800/50 border border-gray-700 p-6 rounded-2xl backdrop-blur-sm"
                >
                    <div className="flex justify-between items-start mb-4">
                        <div className="p-3 bg-blue-500/10 rounded-lg">
                            <Activity className="w-6 h-6 text-blue-400" />
                        </div>
                        <span className="text-2xl font-bold text-white">{info.ram_percent}%</span>
                    </div>
                    <h3 className="text-gray-400 font-medium">Memory Usage</h3>
                    <div className="mt-4 w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-blue-500 transition-all duration-500"
                            style={{ width: `${info.ram_percent}%` }}
                        />
                    </div>
                    <p className="mt-2 text-xs text-gray-500">{info.ram_available} available of {info.ram_total}</p>
                </motion.div>

                {/* Disk Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-gray-800/50 border border-gray-700 p-6 rounded-2xl backdrop-blur-sm"
                >
                    <div className="flex justify-between items-start mb-4">
                        <div className="p-3 bg-green-500/10 rounded-lg">
                            <HardDrive className="w-6 h-6 text-green-400" />
                        </div>
                        <span className="text-2xl font-bold text-white">{info.disk_percent}%</span>
                    </div>
                    <h3 className="text-gray-400 font-medium">Disk Usage</h3>
                    <div className="mt-4 w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-green-500 transition-all duration-500"
                            style={{ width: `${info.disk_percent}%` }}
                        />
                    </div>
                    <p className="mt-2 text-xs text-gray-500">{info.disk_usage}</p>
                </motion.div>
            </div>

            <div className="bg-gray-800/30 border border-gray-700 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">System Details</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-4 bg-gray-800/50 rounded-xl">
                        <p className="text-gray-400 mb-1">OS Platform</p>
                        <p className="text-white font-medium">{info.platform}</p>
                    </div>
                    <div className="p-4 bg-gray-800/50 rounded-xl">
                        <p className="text-gray-400 mb-1">Processor Architecture</p>
                        <p className="text-white font-medium">{info.processor}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

const FileExplorer = () => {
    const [path, setPath] = useState('.');
    const [files, setFiles] = useState<FileItem[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchFiles = async (dirPath: string) => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8001/files?path=${encodeURIComponent(dirPath)}`);
            if (res.ok) {
                const data = await res.json();
                setFiles(data);
                setPath(dirPath);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFiles('.');
    }, []);

    return (
        <div className="h-full flex flex-col">
            <div className="flex items-center gap-4 mb-6">
                <h2 className="text-2xl font-bold text-white">File Explorer</h2>
                <div className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 flex items-center gap-2">
                    <span className="text-gray-400 text-sm font-mono">{path}</span>
                </div>
                <button
                    onClick={() => fetchFiles('.')}
                    className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-300"
                >
                    Home
                </button>
            </div>

            <div className="flex-1 bg-gray-800/30 border border-gray-700 rounded-2xl overflow-hidden flex flex-col">
                <div className="grid grid-cols-12 gap-4 p-4 border-b border-gray-700 text-sm font-medium text-gray-400">
                    <div className="col-span-6">Name</div>
                    <div className="col-span-3">Size</div>
                    <div className="col-span-3">Modified</div>
                </div>

                <div className="flex-1 overflow-y-auto p-2">
                    {loading ? (
                        <div className="flex justify-center p-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-blue-500" />
                        </div>
                    ) : (
                        files.map((file, i) => (
                            <motion.div
                                key={file.path}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.03 }}
                                onClick={() => file.type === 'directory' && fetchFiles(file.path)}
                                className={`grid grid-cols-12 gap-4 p-3 rounded-lg cursor-pointer transition-colors ${file.type === 'directory'
                                        ? 'hover:bg-blue-500/10 text-blue-300'
                                        : 'hover:bg-gray-700/50 text-gray-300'
                                    }`}
                            >
                                <div className="col-span-6 flex items-center gap-3">
                                    {file.type === 'directory' ? <Folder className="w-4 h-4" /> : <File className="w-4 h-4" />}
                                    <span className="truncate font-mono text-sm">{file.name}</span>
                                </div>
                                <div className="col-span-3 text-sm text-gray-500">
                                    {file.size ? (file.size / 1024).toFixed(1) + ' KB' : '-'}
                                </div>
                                <div className="col-span-3 text-sm text-gray-500">
                                    {new Date(file.modified! * 1000).toLocaleDateString()}
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

const Chat = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([
        { role: 'assistant', content: 'Hello! I am Atlas. I can help you monitor your system, browse files, or execute commands. How can I assist you today?' }
    ]);
    const [input, setInput] = useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const newMsgs = [...messages, { role: 'user', content: input } as ChatMessage];
        setMessages(newMsgs);
        setInput('');

        try {
            const res = await fetch('http://localhost:8001/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newMsgs)
            });
            const data = await res.json();
            setMessages([...newMsgs, data]);
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="h-full flex flex-col bg-gray-800/30 border border-gray-700 rounded-2xl overflow-hidden">
            <div className="p-4 border-b border-gray-700 bg-gray-900/50">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-blue-400" />
                    Atlas AI Assistant
                </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {messages.map((msg, i) => (
                    <div
                        key={i}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user'
                                    ? 'bg-blue-600 text-white rounded-tr-none'
                                    : 'bg-gray-700 text-gray-200 rounded-tl-none'
                                }`}
                        >
                            <p className="text-sm leading-relaxed">{msg.content}</p>
                        </div>
                    </div>
                ))}
            </div>

            <div className="p-4 bg-gray-900/50 border-t border-gray-700">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Type a message..."
                        className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
                    />
                    <button
                        onClick={sendMessage}
                        className="p-3 bg-blue-600 hover:bg-blue-700 rounded-xl text-white transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
};

const ProcessManager = () => {
    const [processes, setProcesses] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchProcesses = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8001/processes');
            const data = await res.json();
            setProcesses(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const killProcess = async (pid: number) => {
        if (!confirm(`Are you sure you want to kill process ${pid}?`)) return;
        try {
            const res = await fetch(`http://localhost:8001/processes/${pid}/kill`, { method: 'POST' });
            if (res.ok) {
                fetchProcesses();
            } else {
                alert('Failed to kill process. Permission denied?');
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchProcesses();
        const interval = setInterval(fetchProcesses, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="h-full flex flex-col bg-gray-800/30 border border-gray-700 rounded-2xl overflow-hidden">
            <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Activity className="w-5 h-5 text-red-400" />
                    Task Manager
                </h2>
                <button onClick={fetchProcesses} className="p-2 hover:bg-gray-700 rounded-lg">
                    <Activity className="w-4 h-4 text-gray-400" />
                </button>
            </div>

            <div className="grid grid-cols-12 gap-4 p-4 border-b border-gray-700 text-sm font-medium text-gray-400 bg-gray-900/50">
                <div className="col-span-4">Name</div>
                <div className="col-span-2">PID</div>
                <div className="col-span-2">CPU %</div>
                <div className="col-span-2">Mem %</div>
                <div className="col-span-2">Action</div>
            </div>

            <div className="flex-1 overflow-y-auto p-2">
                {processes.map((proc) => (
                    <div key={proc.pid} className="grid grid-cols-12 gap-4 p-3 hover:bg-gray-700/30 rounded-lg items-center text-sm border-b border-gray-800 last:border-0">
                        <div className="col-span-4 font-medium text-white truncate">{proc.name}</div>
                        <div className="col-span-2 text-gray-400 font-mono">{proc.pid}</div>
                        <div className="col-span-2 text-purple-400">{proc.cpu_percent?.toFixed(1)}%</div>
                        <div className="col-span-2 text-blue-400">{proc.memory_percent?.toFixed(1)}%</div>
                        <div className="col-span-2">
                            <button
                                onClick={() => killProcess(proc.pid)}
                                className="px-3 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-md text-xs font-medium transition-colors"
                            >
                                Kill
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');

    return (
        <div className="flex h-screen bg-[#0B1120] text-gray-100 font-sans overflow-hidden">
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

            <main className="flex-1 p-8 overflow-hidden">
                <AnimatePresence mode="wait">
                    {activeTab === 'dashboard' && (
                        <motion.div
                            key="dashboard"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="h-full"
                        >
                            <Dashboard />
                        </motion.div>
                    )}
                    {activeTab === 'files' && (
                        <motion.div
                            key="files"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="h-full"
                        >
                            <FileExplorer />
                        </motion.div>
                    )}
                    {activeTab === 'chat' && (
                        <motion.div
                            key="chat"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="h-full"
                        >
                            <Chat />
                        </motion.div>
                    )}
                    {activeTab === 'terminal' && (
                        <motion.div key="terminal" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full">
                            <ProcessManager />
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
