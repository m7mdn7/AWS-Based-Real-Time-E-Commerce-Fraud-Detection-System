import React from 'react';
import {
  Shield,
  LayoutDashboard,
  Cpu,
  Sparkles,
  History,
  AlertOctagon,
  Cloud,
  ExternalLink
} from 'lucide-react';

export type NavTab = 'dashboard' | 'simulator' | 'scenarios' | 'history' | 'alerts' | 'architecture';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  alertCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, alertCount }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'simulator', label: 'Tx Simulator', icon: Cpu },
    { id: 'scenarios', label: 'Attack Scenarios', icon: Sparkles },
    { id: 'history', label: 'Transaction Logs', icon: History },
    { id: 'alerts', label: 'Alert Queue', icon: AlertOctagon, badge: alertCount },
    { id: 'architecture', label: 'AWS Architecture', icon: Cloud },
  ];

  return (
    <aside className="w-64 bg-[#0B1120] text-slate-300 flex flex-col border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-slate-800/80">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-base tracking-tight text-white">AWS FraudShield</span>
          </div>
          <span className="text-[10px] font-medium text-cyan-400 uppercase tracking-wider block">
            Real-Time ML Defense
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="px-3 py-6 flex-1 space-y-1">
        <div className="px-3 mb-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Monitoring & Detection
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id as NavTab)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/25 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Cloud Status Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium">Inference Engine</span>
            <span className="inline-flex items-center gap-1 text-emerald-400 font-mono text-[11px]">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Scikit / Tree
            </span>
          </div>
          <div className="flex items-center justify-between text-slate-400">
            <span>Storage Adapter</span>
            <span className="text-slate-200 font-mono text-[11px]">SQLite (Local)</span>
          </div>
        </div>
        <div className="mt-3 text-[11px] text-center text-slate-400">
          Simulated Financial Environment
        </div>
      </div>
    </aside>
  );
};
