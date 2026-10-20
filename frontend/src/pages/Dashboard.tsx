import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  CreditCard,
  ArrowUpRight,
  TrendingUp,
  Clock,
  ChevronRight,
  MapPin,
  Smartphone
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { DashboardStats, Transaction } from '../types';
import { api } from '../api';
import { RiskBadge, ActionBadge } from '../components/RiskBadge';

interface DashboardProps {
  onSelectTransaction: (tx: Transaction) => void;
  onNavigateToSimulator: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onSelectTransaction, onNavigateToSimulator }) => {
  const [stats, setStats] = useState<DashboardStats>({
    total_transactions: 0,
    high_risk_count: 0,
    medium_risk_count: 0,
    low_risk_count: 0,
    alert_count: 0
  });
  const [recentAlerts, setRecentAlerts] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsRes, alertsRes] = await Promise.all([
        api.getStats(),
        api.getAlerts(6)
      ]);
      setStats(statsRes);
      setRecentAlerts(alertsRes.alerts);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Visual trend data
  const trendData = [
    { time: '00:00', volume: 140, fraud: 3 },
    { time: '04:00', volume: 85, fraud: 8 },
    { time: '08:00', volume: 320, fraud: 4 },
    { time: '12:00', volume: 680, fraud: 12 },
    { time: '16:00', volume: 590, fraud: 9 },
    { time: '20:00', volume: 720, fraud: 15 },
    { time: 'Now', volume: 410, fraud: 7 },
  ];

  const pieData = [
    { name: 'Low Risk (Approved)', value: Math.max(stats.low_risk_count, 1), color: '#10B981' },
    { name: 'Medium Risk (MFA)', value: stats.medium_risk_count, color: '#F59E0B' },
    { name: 'High Risk (Flagged)', value: stats.high_risk_count, color: '#EF4444' },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Metric Cards Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Analyzed */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Evaluated</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <CreditCard className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">{stats.total_transactions.toLocaleString()}</div>
            <div className="text-xs text-slate-500 mt-1 flex items-center gap-1 font-medium">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
              <span>Simulated transactions scored</span>
            </div>
          </div>
        </div>

        {/* High Risk (Flagged) */}
        <div className="bg-white p-5 rounded-xl border border-rose-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold text-rose-700 uppercase tracking-wider">High Risk Alerts</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-rose-600">{stats.high_risk_count.toLocaleString()}</div>
            <div className="text-xs text-rose-600/80 mt-1 font-medium">
              Score ≥ 0.70 (Flagged for review)
            </div>
          </div>
        </div>

        {/* Medium Risk (MFA) */}
        <div className="bg-white p-5 rounded-xl border border-amber-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold text-amber-700 uppercase tracking-wider">Medium Risk (MFA)</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-amber-600">{stats.medium_risk_count.toLocaleString()}</div>
            <div className="text-xs text-amber-600/80 mt-1 font-medium">
              0.30 ≤ Score &lt; 0.70 (2FA Challenge)
            </div>
          </div>
        </div>

        {/* Low Risk (Approved) */}
        <div className="bg-white p-5 rounded-xl border border-emerald-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">Low Risk Approved</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-emerald-600">{stats.low_risk_count.toLocaleString()}</div>
            <div className="text-xs text-emerald-600/80 mt-1 font-medium">
              Score &lt; 0.30 (Seamless checkout)
            </div>
          </div>
        </div>
      </div>

      {/* Visual Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Area Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200/90 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Transaction Volume & Fraud Anomalies</h2>
              <p className="text-xs text-slate-500">24-hour baseline velocity vs flagged suspicious spikes</p>
            </div>
            <span className="text-xs font-medium px-2.5 py-1 bg-slate-100 text-slate-600 rounded">
              Simulated Stream
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="fraudGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B1120', borderRadius: '8px', border: 'none', color: '#fff' }}
                  itemStyle={{ fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="volume" stroke="#06B6D4" strokeWidth={2} fillOpacity={1} fill="url(#volGrad)" name="Total Volume" />
                <Area type="monotone" dataKey="fraud" stroke="#EF4444" strokeWidth={2} fillOpacity={1} fill="url(#fraudGrad)" name="High Risk Alerts" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution Donut Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Decision Band Distribution</h2>
            <p className="text-xs text-slate-500">Configured policy threshold allocation</p>
          </div>

          <div className="h-56 w-full my-auto">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Low: &lt;0.30</span>
            <span>Med: 0.30–0.70</span>
            <span>High: ≥0.70</span>
          </div>
        </div>
      </div>

      {/* Recent Flagged Activity Table */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recent Flagged Transactions</h2>
            <p className="text-xs text-slate-500">Transactions automatically intercepted by ML risk scoring</p>
          </div>
          <button
            onClick={onNavigateToSimulator}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-cyan-600 bg-cyan-50 hover:bg-cyan-100 rounded-lg transition-colors"
          >
            Launch Simulator
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          {recentAlerts.length === 0 ? (
            <div className="p-10 text-center text-slate-400 text-sm">
              No flagged alerts currently in queue. Run a transaction simulation to test detection!
            </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/75 text-slate-500 text-[11px] font-semibold uppercase tracking-wider border-b border-slate-200/80">
                  <th className="py-3 px-6">Transaction ID</th>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Location & Device</th>
                  <th className="py-3 px-4">Risk Score</th>
                  <th className="py-3 px-4">Recommendation</th>
                  <th className="py-3 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
                {recentAlerts.map((tx) => (
                  <tr key={tx.transaction_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-6 font-mono font-medium text-slate-900">
                      {tx.transaction_id}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-600 text-xs">
                      {tx.user_id}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900">
                      ₹{tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        <span>{tx.location || 'Unknown'}</span>
                      </div>
                      <div className="flex items-center gap-1 text-[11px] text-slate-400 mt-0.5">
                        <Smartphone className="w-3 h-3" />
                        <span className="font-mono truncate max-w-[140px]">{tx.device_id}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-sm">
                          {(tx.risk_score * 100).toFixed(0)}%
                        </span>
                        <RiskBadge level={tx.risk_level} />
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <ActionBadge action={tx.recommended_action} />
                    </td>
                    <td className="py-3.5 px-6 text-right">
                      <button
                        onClick={() => onSelectTransaction(tx)}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-cyan-600 hover:text-cyan-800"
                      >
                        Inspect
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
