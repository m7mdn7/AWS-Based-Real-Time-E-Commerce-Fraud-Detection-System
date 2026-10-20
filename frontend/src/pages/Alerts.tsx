import React, { useEffect, useState } from 'react';
import {
  AlertOctagon,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  FileText,
  Clock,
  ShieldCheck,
  Send,
  Info
} from 'lucide-react';
import { Transaction } from '../types';
import { api } from '../api';
import { RiskBadge, ActionBadge } from '../components/RiskBadge';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlert, setSelectedAlert] = useState<Transaction | null>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const res = await api.getAlerts(100);
      setAlerts(res.alerts);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleReviewAction = async (status: string) => {
    if (!selectedAlert) return;
    setSubmitting(true);
    try {
      const updated = await api.reviewAlert(selectedAlert.transaction_id, status, reviewNotes);
      setAlerts((prev) =>
        prev.map((a) => (a.transaction_id === updated.transaction_id ? updated : a))
      );
      setSelectedAlert(updated);
      setMessage(`Transaction ${selectedAlert.transaction_id} marked as ${status}.`);
      setReviewNotes('');
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      console.error('Failed to update alert:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-rose-600 text-xs font-semibold uppercase tracking-wider">
            <AlertOctagon className="w-4 h-4" />
            Security Operations & Incident Response
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">Fraud Alerts Triage Center</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Active queue of suspicious and high-risk transactions requiring analyst verification
          </p>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Pending Reviews: <span className="font-bold text-rose-600">{alerts.length}</span>
        </div>
      </div>

      {message && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Alerts Queue */}
        <div className="lg:col-span-7 space-y-3">
          {loading ? (
            <div className="p-12 text-center text-slate-400 text-xs bg-white rounded-2xl border border-slate-200">
              Loading alert queue...
            </div>
          ) : alerts.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs bg-white rounded-2xl border border-slate-200">
              No flagged alerts in queue. All systems operating within normal parameters.
            </div>
          ) : (
            alerts.map((al) => {
              const isSelected = selectedAlert?.transaction_id === al.transaction_id;
              return (
                <div
                  key={al.transaction_id}
                  onClick={() => setSelectedAlert(al)}
                  className={`p-5 rounded-2xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-white border-cyan-500 ring-2 ring-cyan-500/10 shadow-md'
                      : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-xs text-slate-900">
                          {al.transaction_id}
                        </span>
                        <RiskBadge level={al.risk_level} />
                        <span className="text-[11px] font-mono text-slate-400">
                          {al.user_id}
                        </span>
                      </div>

                      <div className="mt-2 text-sm font-semibold text-slate-900">
                        ₹{al.amount.toLocaleString()} at {al.merchant || 'General Merchant'}
                      </div>

                      <div className="mt-2 text-xs text-slate-500 flex items-center gap-3">
                        <span>📍 {al.location || 'Unknown'}</span>
                        <span>•</span>
                        <span>📱 {al.device_id}</span>
                      </div>
                    </div>

                    <div className="text-right shrink-0">
                      <div className="font-mono font-bold text-base text-rose-600">
                        {(al.risk_score * 100).toFixed(0)}%
                      </div>
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mt-1">
                        {al.review_status?.replace(/_/g, ' ') || 'PENDING'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Action & Audit Review Panel */}
        <div className="lg:col-span-5">
          <div className="bg-white p-7 rounded-2xl border border-slate-200/90 shadow-sm sticky top-24 space-y-6">
            <h3 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-4">
              Analyst Decision Console
            </h3>

            {!selectedAlert ? (
              <div className="py-20 text-center text-slate-400">
                <ShieldAlert className="w-10 h-10 mx-auto text-slate-300 stroke-1 mb-2" />
                <p className="text-sm font-medium text-slate-600">Select an Alert</p>
                <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
                  Click on an alert in the queue to inspect anomaly signals and log a resolution.
                </p>
              </div>
            ) : (
              <div className="space-y-5">
                {/* Score Summary */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold uppercase text-slate-500">Risk Assessment</span>
                    <div className="text-2xl font-bold font-mono text-slate-900">
                      {(selectedAlert.risk_score * 100).toFixed(1)}%
                    </div>
                  </div>
                  <RiskBadge level={selectedAlert.risk_level} />
                </div>

                {/* Signals */}
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                    Flagged Anomaly Signals
                  </h4>
                  <ul className="space-y-1.5">
                    {selectedAlert.risk_factors.map((f, i) => (
                      <li key={i} className="text-xs text-slate-700 p-2.5 rounded-lg bg-rose-50/60 border border-rose-100 flex items-start gap-2">
                        <AlertOctagon className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Analyst Notes */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Investigation Notes (Optional)
                  </label>
                  <textarea
                    rows={3}
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                    placeholder="e.g. Cardholder confirmed overseas travel via SMS..."
                    className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all resize-none"
                  />
                </div>

                {/* Decision Actions */}
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <div className="text-xs font-semibold text-slate-700 mb-2">Resolve Incident:</div>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleReviewAction('CONFIRMED_FRAUD')}
                      disabled={submitting}
                      className="py-2.5 px-3 rounded-xl text-xs font-semibold bg-rose-600 hover:bg-rose-700 text-white flex items-center justify-center gap-1.5 shadow-sm transition-colors"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      Confirm Fraud
                    </button>
                    <button
                      onClick={() => handleReviewAction('FALSE_POSITIVE')}
                      disabled={submitting}
                      className="py-2.5 px-3 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center gap-1.5 shadow-sm transition-colors"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      False Positive
                    </button>
                  </div>
                  <button
                    onClick={() => handleReviewAction('WHITELISTED')}
                    disabled={submitting}
                    className="w-full py-2 px-3 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <ShieldCheck className="w-3.5 h-3.5 text-cyan-600" />
                    Whitelist Device & Location
                  </button>
                </div>

                {/* Disclaimer */}
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-500 flex items-start gap-2">
                  <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                  <span>
                    Analyst reviews provide ground-truth feedback used for iterative model re-training and feature calibration.
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
