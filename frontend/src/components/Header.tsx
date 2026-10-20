import React from 'react';
import { Activity, Bell, RefreshCw, Server, Zap } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle: string;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle, onRefresh, isLoading }) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-10 shadow-[0_1px_3px_0_rgba(0,0,0,0.02)]">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">{title}</h1>
        <p className="text-xs text-slate-500 font-normal">{subtitle}</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Environment Badge */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200/80 text-xs font-medium text-slate-700">
          <Server className="w-3.5 h-3.5 text-cyan-600" />
          <span>Local Mock / Dev Mode</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
        </div>

        {/* Refresh Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors border border-slate-200"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-cyan-600' : ''}`} />
          </button>
        )}

        {/* Real-time Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-50 border border-cyan-100 text-xs font-semibold text-cyan-800">
          <Zap className="w-3.5 h-3.5 text-cyan-600 fill-cyan-600" />
          <span>Real-time Scoring</span>
        </div>
      </div>
    </header>
  );
};
