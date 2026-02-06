import React, { useState, useEffect } from 'react';
import { Shield, Lock, Eye, Smartphone, MessageSquare, Globe, Brain, Check, X } from 'lucide-react';

interface Permission {
  type: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  enabled: boolean;
  askEveryTime: boolean;
}

interface AuditLog {
  timestamp: string;
  action: string;
  permission_type: string;
  status: string;
  details: any;
}

const Permissions: React.FC = () => {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [selectedFilter, setSelectedFilter] = useState<string>('all');

  useEffect(() => {
    fetchPermissions();
    fetchAuditLogs();
  }, []);

  const fetchPermissions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/permissions');
      const data = await response.json();
      
      if (data.success) {
        const perms: Permission[] = [
          {
            type: 'files',
            label: 'File Access',
            description: 'Read, write, and manage files and folders',
            icon: <Lock className="w-6 h-6" />,
            enabled: data.permissions.files.enabled,
            askEveryTime: data.permissions.files.ask_every_time
          },
          {
            type: 'keyboard_mouse',
            label: 'Keyboard & Mouse Control',
            description: 'Control keyboard input and mouse movements',
            icon: <Eye className="w-6 h-6" />,
            enabled: data.permissions.keyboard_mouse.enabled,
            askEveryTime: data.permissions.keyboard_mouse.ask_every_time
          },
          {
            type: 'screen_capture',
            label: 'Screen Capture',
            description: 'Take screenshots of your screen',
            icon: <Eye className="w-6 h-6" />,
            enabled: data.permissions.screen_capture.enabled,
            askEveryTime: data.permissions.screen_capture.ask_every_time
          },
          {
            type: 'android',
            label: 'Android Control',
            description: 'Control connected Android devices via ADB',
            icon: <Smartphone className="w-6 h-6" />,
            enabled: data.permissions.android.enabled,
            askEveryTime: data.permissions.android.ask_every_time
          },
          {
            type: 'enterchat',
            label: 'EnterChat Integration',
            description: 'Access and control messaging apps',
            icon: <MessageSquare className="w-6 h-6" />,
            enabled: data.permissions.enterchat.enabled,
            askEveryTime: data.permissions.enterchat.ask_every_time
          },
          {
            type: 'network',
            label: 'Network Access',
            description: 'Make network requests and API calls',
            icon: <Globe className="w-6 h-6" />,
            enabled: data.permissions.network.enabled,
            askEveryTime: false
          },
          {
            type: 'ai_remote',
            label: 'Remote AI Services',
            description: 'Use cloud-based AI models',
            icon: <Brain className="w-6 h-6" />,
            enabled: data.permissions.ai_remote.enabled,
            askEveryTime: false
          }
        ];
        
        setPermissions(perms);
      }
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/audit-log?limit=50');
      const data = await response.json();
      
      if (data.success) {
        setAuditLogs(data.logs);
      }
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    }
  };

  const togglePermission = async (type: string, enabled: boolean) => {
    try {
      await fetch('http://localhost:8000/api/permissions/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ permission_type: type, enabled })
      });
      
      fetchPermissions();
    } catch (error) {
      console.error('Failed to update permission:', error);
    }
  };

  const toggleAskEveryTime = async (type: string, askEveryTime: boolean) => {
    try {
      await fetch('http://localhost:8000/api/permissions/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ permission_type: type, enabled: true, ask_every_time: askEveryTime })
      });
      
      fetchPermissions();
    } catch (error) {
      console.error('Failed to update ask_every_time:', error);
    }
  };

  const filteredLogs = selectedFilter === 'all' 
    ? auditLogs 
    : auditLogs.filter(log => log.permission_type === selectedFilter);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="w-8 h-8 text-purple-400" />
            <h1 className="text-3xl font-bold text-white">Permissions & Security</h1>
          </div>
          <p className="text-gray-400">Control what ShivAI Atlas can access on your system</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Permissions List */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4">System Permissions</h2>
              
              <div className="space-y-4">
                {permissions.map((perm) => (
                  <PermissionCard
                    key={perm.type}
                    permission={perm}
                    onToggle={(enabled) => togglePermission(perm.type, enabled)}
                    onToggleAsk={(askEveryTime) => toggleAskEveryTime(perm.type, askEveryTime)}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Audit Log */}
          <div className="space-y-4">
            <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4">Activity Log</h2>
              
              <div className="mb-4">
                <select
                  value={selectedFilter}
                  onChange={(e) => setSelectedFilter(e.target.value)}
                  className="w-full bg-black/30 text-white rounded-lg p-2 border border-white/10"
                >
                  <option value="all">All Actions</option>
                  <option value="files">Files</option>
                  <option value="keyboard_mouse">Keyboard/Mouse</option>
                  <option value="screen_capture">Screen Capture</option>
                  <option value="android">Android</option>
                  <option value="enterchat">EnterChat</option>
                </select>
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
                {filteredLogs.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    No activity yet
                  </div>
                ) : (
                  filteredLogs.map((log, index) => (
                    <LogEntry key={index} log={log} />
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
        }
      `}</style>
    </div>
  );
};

const PermissionCard: React.FC<{
  permission: Permission;
  onToggle: (enabled: boolean) => void;
  onToggleAsk: (askEveryTime: boolean) => void;
}> = ({ permission, onToggle, onToggleAsk }) => {
  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/10">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${permission.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
            {permission.icon}
          </div>
          <div>
            <h3 className="text-white font-semibold">{permission.label}</h3>
            <p className="text-sm text-gray-400">{permission.description}</p>
          </div>
        </div>
        
        <button
          onClick={() => onToggle(!permission.enabled)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            permission.enabled ? 'bg-green-500' : 'bg-gray-600'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              permission.enabled ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>
      
      {permission.askEveryTime !== undefined && (
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/10">
          <span className="text-sm text-gray-300">Ask every time</span>
          <button
            onClick={() => onToggleAsk(!permission.askEveryTime)}
            disabled={!permission.enabled}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
              permission.askEveryTime && permission.enabled ? 'bg-purple-500' : 'bg-gray-600'
            } ${!permission.enabled && 'opacity-50 cursor-not-allowed'}`}
          >
            <span
              className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                permission.askEveryTime ? 'translate-x-5' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      )}
    </div>
  );
};

const LogEntry: React.FC<{ log: AuditLog }> = ({ log }) => {
  const statusColors = {
    granted: 'text-green-400',
    denied: 'text-red-400',
    approved: 'text-blue-400',
    executed: 'text-purple-400'
  };

  const statusIcons = {
    granted: <Check className="w-4 h-4" />,
    denied: <X className="w-4 h-4" />,
    approved: <Check className="w-4 h-4" />,
    executed: <Check className="w-4 h-4" />
  };

  return (
    <div className="bg-white/5 rounded-lg p-3 border border-white/5">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-2">
          <div className={statusColors[log.status as keyof typeof statusColors] || 'text-gray-400'}>
            {statusIcons[log.status as keyof typeof statusIcons]}
          </div>
          <div>
            <p className="text-sm text-white font-medium">{log.action}</p>
            <p className="text-xs text-gray-400 mt-1">
              {new Date(log.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
        <span className={`text-xs px-2 py-1 rounded ${
          statusColors[log.status as keyof typeof statusColors] || 'text-gray-400'
        } bg-white/5`}>
          {log.status}
        </span>
      </div>
    </div>
  );
};

export default Permissions;
