import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  MapPin,
  Smartphone,
  Calendar,
  X,
  CreditCard,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { RiskLevel, Transaction } from '../types';
import { api } from '../api';
import { RiskBadge, ActionBadge } from '../components/RiskBadge';

export const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [page, setPage] = useState(0);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);

  const limit = 15;

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const res = await api.getTransactions(limit, page * limit, riskFilter);
      setTransactions(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error('Failed to load transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, [page, riskFilter]);

  const filtered = transactions.filter((t) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      t.transaction_id.toLowerCase().includes(q) ||
      t.user_id.toLowerCase().includes(q) ||
      (t.merchant && t.merchant.toLowerCase().includes(q))
    );
  });

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Transaction History</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Audit log of simulated e-commerce transactions and risk evaluations
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-2.5" />
          <input
            type="text"
            placeholder="Search TX ID or User..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all shadow-sm"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
        {(['ALL', 'LOW', 'MEDIUM', 'HIGH'] as const).map((filter) => (
          <button
            key={filter}
            onClick={() => {
              setRiskFilter(filter);
              setPage(0);
            }}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              riskFilter === filter
                ? 'bg-slate-900 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            {filter === 'ALL' ? 'All Transactions' : `${filter} Risk`}
          </button>
        ))}
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/75 text-slate-500 text-[11px] font-semibold uppercase tracking-wider border-b border-slate-200/80">
                <th className="py-3 px-6">Transaction ID</th>
                <th className="py-3 px-4">User ID</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Merchant</th>
                <th className="py-3 px-4">Location & Device</th>
                <th className="py-3 px-4">Score</th>
                <th className="py-3 px-4">Decision</th>
                <th className="py-3 px-6 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400 text-xs">
                    Loading records from storage...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400 text-xs">
                    No transactions match the selected criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((tx) => (
                  <tr key={tx.transaction_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-6 font-mono font-medium text-slate-900 text-xs">
                      {tx.transaction_id}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-600 text-xs">
                      {tx.user_id}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900">
                      ₹{tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-medium text-slate-700">
                      {tx.merchant || 'General Merchant'}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        <span>{tx.location || 'Unknown'}</span>
                      </div>
                      <div className="flex items-center gap-1 text-[11px] text-slate-400 mt-0.5">
                        <Smartphone className="w-3 h-3" />
                        <span className="font-mono truncate max-w-[120px]">{tx.device_id}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono font-bold text-xs">
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
                        onClick={() => setSelectedTx(tx)}
                        className="px-2.5 py-1 text-xs font-semibold text-cyan-700 hover:text-cyan-900 bg-cyan-50 hover:bg-cyan-100 rounded-lg transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <div>
            Showing <span className="font-semibold text-slate-700">{filtered.length}</span> of{' '}
            <span className="font-semibold text-slate-700">{total}</span> transactions
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 0))}
              disabled={page === 0 || loading}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-medium text-slate-700">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(p + 1, totalPages - 1))}
              disabled={page >= totalPages - 1 || loading}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Transaction Detail Slide-Over Modal */}
      {selectedTx && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex justify-end">
          <div className="w-full max-w-md bg-white h-full shadow-2xl p-6 flex flex-col justify-between overflow-y-auto">
            <div>
              <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-5">
                <div>
                  <h3 className="text-base font-bold text-slate-900">Transaction Details</h3>
                  <span className="text-xs font-mono text-cyan-600">{selectedTx.transaction_id}</span>
                </div>
                <button
                  onClick={() => setSelectedTx(null)}
                  className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Score Block */}
              <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200/90 text-center mb-6">
                <div className="text-xs text-slate-500 uppercase font-semibold">Model Probability</div>
                <div className="text-4xl font-extrabold font-mono text-slate-900 my-1.5">
                  {(selectedTx.risk_score * 100).toFixed(1)}%
                </div>
                <div className="flex items-center justify-center gap-2 mt-2">
                  <RiskBadge level={selectedTx.risk_level} />
                  <ActionBadge action={selectedTx.recommended_action} />
                </div>
              </div>

              {/* Attributes List */}
              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Customer Account</span>
                  <span className="font-mono font-semibold text-slate-900">{selectedTx.user_id}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Amount</span>
                  <span className="font-semibold text-slate-900">₹{selectedTx.amount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Merchant</span>
                  <span className="font-medium text-slate-800">{selectedTx.merchant || 'N/A'}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Location</span>
                  <span className="font-medium text-slate-800">{selectedTx.location || 'N/A'}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Device Fingerprint</span>
                  <span className="font-mono text-slate-800 truncate max-w-[200px]">{selectedTx.device_id}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 font-medium">Timestamp</span>
                  <span className="font-mono text-slate-600">{new Date(selectedTx.timestamp).toLocaleString()}</span>
                </div>
              </div>

              {/* Triggered Signals */}
              <div className="mt-6">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                  Signal Indicators
                </h4>
                {selectedTx.risk_factors.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No anomaly triggers detected.</p>
                ) : (
                  <ul className="space-y-2">
                    {selectedTx.risk_factors.map((f, idx) => (
                      <li key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700">
                        {f}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <button
              onClick={() => setSelectedTx(null)}
              className="mt-6 w-full py-2.5 text-xs font-semibold bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
