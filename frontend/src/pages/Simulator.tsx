import React, { useState } from 'react';
import {
  Play,
  RotateCcw,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Info,
  CheckCircle,
  HelpCircle,
  Code2,
  Terminal,
  Cpu
} from 'lucide-react';
import { AnalyzeRequest, Transaction } from '../types';
import { api } from '../api';
import { RiskBadge, ActionBadge } from '../components/RiskBadge';

export const Simulator: React.FC = () => {
  const [formData, setFormData] = useState<AnalyzeRequest>({
    transaction_id: `TX-${Math.floor(100000 + Math.random() * 900000)}`,
    user_id: 'USR-1001',
    amount: 10000.0,
    merchant: 'Crypto Voucher Hub',
    merchant_category: 'digital_goods',
    location: 'Lagos, Nigeria',
    device_id: 'DEV-ATTACK-9999',
    ip_address: '185.220.101.5',
    timestamp: new Date().toISOString()
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Transaction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showJson, setShowJson] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'amount' ? (value === '' ? '' : parseFloat(value)) : value
    }));
  };

  const handleRunAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Ensure numeric amount
      const payload: AnalyzeRequest = {
        ...formData,
        amount: Number(formData.amount) || 0,
        transaction_id: formData.transaction_id || `TX-${Math.floor(100000 + Math.random() * 900000)}`
      };
      const response = await api.analyzeTransaction(payload);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Please check backend status.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      transaction_id: `TX-${Math.floor(100000 + Math.random() * 900000)}`,
      user_id: 'USR-1001',
      amount: 750.0,
      merchant: 'Amazon India',
      merchant_category: 'electronics',
      location: 'Bengaluru',
      device_id: 'DEV-ANDR-1001',
      ip_address: '103.21.244.1',
      timestamp: new Date().toISOString()
    });
    setResult(null);
    setError(null);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Overview Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-[#111827] text-white p-6 rounded-2xl shadow-sm border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
            <Cpu className="w-4 h-4" />
            Interactive Transaction Testing Sandbox
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Simulate Real-Time E-Commerce Transactions</h2>
          <p className="text-sm text-slate-300 mt-1 max-w-2xl">
            Input synthetic transaction parameters to test behavioral deviations against user baseline history,
            trigger ML model inference, and evaluate calibrated risk decisions.
          </p>
        </div>
        <button
          onClick={handleReset}
          className="self-start md:self-auto px-4 py-2 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 flex items-center gap-2 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Form
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Form: Transaction Attributes */}
        <div className="lg:col-span-7 bg-white p-7 rounded-2xl border border-slate-200/90 shadow-sm">
          <h3 className="text-base font-bold text-slate-900 mb-1">Transaction Parameters</h3>
          <p className="text-xs text-slate-500 mb-6">
            All fields are evaluated in real time against customer baseline history.
          </p>

          {error && (
            <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-3">
              <ShieldAlert className="w-5 h-5 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleRunAnalysis} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Transaction ID
                </label>
                <input
                  type="text"
                  name="transaction_id"
                  value={formData.transaction_id}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-mono focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Customer User ID
                </label>
                <input
                  type="text"
                  name="user_id"
                  value={formData.user_id}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g. USR-1001"
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-mono focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Amount (₹ INR)
                </label>
                <div className="relative">
                  <span className="absolute left-3.5 top-2.5 text-slate-400 font-bold text-sm">₹</span>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    name="amount"
                    value={formData.amount}
                    onChange={handleInputChange}
                    required
                    className="w-full pl-8 pr-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-semibold text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Merchant Category
                </label>
                <select
                  name="merchant_category"
                  value={formData.merchant_category}
                  onChange={handleInputChange}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all"
                >
                  <option value="electronics">Electronics</option>
                  <option value="groceries">Groceries</option>
                  <option value="fashion">Fashion & Apparel</option>
                  <option value="travel">Travel & Airlines</option>
                  <option value="digital_goods">Digital Goods / Vouchers</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Merchant Name
                </label>
                <input
                  type="text"
                  name="merchant"
                  value={formData.merchant}
                  onChange={handleInputChange}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Geographic Location (City)
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="e.g. Bengaluru or Lagos, Nigeria"
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Device ID / Fingerprint
                </label>
                <input
                  type="text"
                  name="device_id"
                  value={formData.device_id}
                  onChange={handleInputChange}
                  placeholder="e.g. DEV-ANDR-1001"
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-mono focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Client IP Address
                </label>
                <input
                  type="text"
                  name="ip_address"
                  value={formData.ip_address}
                  onChange={handleInputChange}
                  placeholder="e.g. 103.21.244.1"
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-mono focus:bg-white focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 transition-all"
                />
              </div>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-xl shadow-md shadow-cyan-600/20 flex items-center justify-center gap-2 transition-all duration-150 disabled:opacity-60"
              >
                <Play className="w-4 h-4 fill-white" />
                {loading ? 'Evaluating Risk Pipeline...' : 'Analyze Transaction'}
              </button>
            </div>
          </form>
        </div>

        {/* Right Output: Real-Time Fraud Assessment */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white p-7 rounded-2xl border border-slate-200/90 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-5">
              <div>
                <h3 className="text-base font-bold text-slate-900">Analysis Result</h3>
                <span className="text-xs text-slate-500">Multidimensional Model Assessment</span>
              </div>
              {result && (
                <button
                  onClick={() => setShowJson(!showJson)}
                  className="px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 rounded-md flex items-center gap-1.5 transition-colors"
                >
                  <Code2 className="w-3.5 h-3.5" />
                  {showJson ? 'Card View' : 'Raw JSON'}
                </button>
              )}
            </div>

            {!result ? (
              <div className="py-16 text-center text-slate-400">
                <HelpCircle className="w-10 h-10 mx-auto text-slate-300 stroke-1 mb-2" />
                <p className="text-sm font-medium text-slate-600">Awaiting Simulation</p>
                <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
                  Click 'Analyze Transaction' or select a preset scenario to view the risk score and factors.
                </p>
              </div>
            ) : showJson ? (
              <div className="bg-slate-950 text-slate-200 p-4 rounded-xl font-mono text-xs overflow-x-auto max-h-96">
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Score Dial & Badges */}
                <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-50 to-slate-100/60 border border-slate-200/80 text-center">
                  <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                    Fraud Risk Probability
                  </div>
                  <div className="text-5xl font-extrabold tracking-tight font-mono text-slate-900 my-2">
                    {(result.risk_score * 100).toFixed(1)}%
                  </div>

                  {/* Visual Progress Bar */}
                  <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden my-3">
                    <div
                      className={`h-full transition-all duration-500 ${
                        result.risk_level === 'HIGH'
                          ? 'bg-rose-500'
                          : result.risk_level === 'MEDIUM'
                          ? 'bg-amber-500'
                          : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(result.risk_score * 100, 100)}%` }}
                    ></div>
                  </div>

                  <div className="flex items-center justify-center gap-3 mt-3">
                    <RiskBadge level={result.risk_level} />
                    <ActionBadge action={result.recommended_action} />
                  </div>
                </div>

                {/* Explainable Risk Factors */}
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">
                    Signal Explanations & Triggers
                  </h4>
                  {result.risk_factors.length === 0 ? (
                    <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-100 text-emerald-800 text-xs flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>Consistent with known user spending history and device fingerprint.</span>
                    </div>
                  ) : (
                    <ul className="space-y-2">
                      {result.risk_factors.map((factor, idx) => (
                        <li
                          key={idx}
                          className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2.5"
                        >
                          <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Provenance Metadata */}
                <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-400 space-y-1">
                  <div className="flex justify-between">
                    <span>Scoring Engine:</span>
                    <span className="font-mono text-slate-600">{result.engine_info || 'local_model'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Policy Action:</span>
                    <span className="font-medium text-slate-700">{result.recommended_action}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Legal / Policy Disclaimer */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-slate-500 text-xs flex items-start gap-3">
            <Info className="w-4 h-4 text-cyan-600 shrink-0 mt-0.5" />
            <p>
              <strong>Important Notice:</strong> Predictions are statistical risk indicators, not definitive proof of fraud.
              A transaction amount spike or new device alone does not constitute fraud without corroborating signals.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
