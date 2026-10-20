import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  Play,
  CheckCircle2,
  AlertOctagon,
  Laptop,
  Plane,
  ShoppingBag,
  Bot,
  ArrowRight,
  ShieldCheck,
  ShieldAlert
} from 'lucide-react';
import { Scenario, Transaction } from '../types';
import { api } from '../api';
import { RiskBadge, ActionBadge } from '../components/RiskBadge';

export const Scenarios: React.FC = () => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeScenarioId, setActiveScenarioId] = useState<string | null>(null);
  const [executionResult, setExecutionResult] = useState<Transaction | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getScenarios()
      .then((data) => setScenarios(data))
      .catch((err) => console.error('Failed to load scenarios:', err));
  }, []);

  const handleRunScenario = async (scenario: Scenario) => {
    setActiveScenarioId(scenario.id);
    setLoading(true);
    try {
      // Append random suffix to tx_id to ensure fresh execution
      const payload = {
        ...scenario.payload,
        transaction_id: `${scenario.payload.transaction_id}-${Math.floor(100 + Math.random() * 900)}`,
        timestamp: new Date().toISOString()
      };
      const result = await api.analyzeTransaction(payload);
      setExecutionResult(result);
    } catch (err) {
      console.error('Scenario execution failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScenarioIcon = (id: string) => {
    if (id.includes('normal')) return <ShoppingBag className="w-5 h-5 text-emerald-600" />;
    if (id.includes('high')) return <Laptop className="w-5 h-5 text-blue-600" />;
    if (id.includes('ato')) return <AlertOctagon className="w-5 h-5 text-rose-600" />;
    if (id.includes('travel')) return <Plane className="w-5 h-5 text-cyan-600" />;
    return <Bot className="w-5 h-5 text-amber-600" />;
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <div className="flex items-center gap-2 text-cyan-600 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          Interactive Attack & Benign Demonstrations
        </div>
        <h2 className="text-xl font-bold text-slate-900 mt-1">Live Scenario Demonstrations</h2>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl">
          Test real-world e-commerce situations against the active FraudShield machine learning pipeline.
          Compare normal purchasing habits with targeted account takeover attacks and legitimate anomalies.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Scenario Selection Cards */}
        <div className="lg:col-span-7 space-y-4">
          {scenarios.map((sc) => {
            const isSelected = activeScenarioId === sc.id;
            return (
              <div
                key={sc.id}
                className={`p-5 rounded-2xl border transition-all duration-200 ${
                  isSelected
                    ? 'bg-white border-cyan-500 ring-2 ring-cyan-500/10 shadow-md'
                    : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3.5">
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 shrink-0 mt-0.5">
                      {getScenarioIcon(sc.id)}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">{sc.name}</h3>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{sc.description}</p>
                      
                      <div className="mt-3 flex flex-wrap gap-2 text-[11px] font-mono text-slate-500">
                        <span className="px-2 py-0.5 rounded bg-slate-100 font-semibold text-slate-700">
                          ₹{sc.payload.amount.toLocaleString()}
                        </span>
                        <span className="px-2 py-0.5 rounded bg-slate-100">
                          {sc.payload.merchant}
                        </span>
                        <span className="px-2 py-0.5 rounded bg-slate-100">
                          📍 {sc.payload.location}
                        </span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleRunScenario(sc)}
                    disabled={loading}
                    className={`shrink-0 px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                      isSelected
                        ? 'bg-cyan-600 text-white shadow-sm shadow-cyan-600/30'
                        : 'bg-slate-100 hover:bg-cyan-50 text-slate-700 hover:text-cyan-700 border border-slate-200'
                    }`}
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Run Test</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Execution Output Drawer */}
        <div className="lg:col-span-5">
          <div className="bg-white p-7 rounded-2xl border border-slate-200/90 shadow-sm sticky top-24">
            <h3 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-4 mb-5">
              Live Pipeline Output
            </h3>

            {!executionResult ? (
              <div className="py-20 text-center text-slate-400">
                <Sparkles className="w-10 h-10 mx-auto text-slate-300 stroke-1 mb-2" />
                <p className="text-sm font-medium text-slate-600">Select a Scenario</p>
                <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
                  Click 'Run Test' on any scenario to observe how FraudShield calculates behavioral risk.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Score Dial */}
                <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-50 to-slate-100/60 border border-slate-200/80 text-center">
                  <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                    Evaluated Fraud Score
                  </div>
                  <div className="text-5xl font-extrabold tracking-tight font-mono text-slate-900 my-2">
                    {(executionResult.risk_score * 100).toFixed(1)}%
                  </div>

                  <div className="flex items-center justify-center gap-3 mt-3">
                    <RiskBadge level={executionResult.risk_level} />
                    <ActionBadge action={executionResult.recommended_action} />
                  </div>
                </div>

                {/* Behavioral Observations */}
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">
                    Model Reasoning & Triggers
                  </h4>
                  {executionResult.risk_factors.length === 0 ? (
                    <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-100 text-emerald-800 text-xs flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>Consistent with known user spending history and device fingerprint.</span>
                    </div>
                  ) : (
                    <ul className="space-y-2">
                      {executionResult.risk_factors.map((f, idx) => (
                        <li key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2.5">
                          <ShieldAlert className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Key Architectural Principle */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-slate-600 text-xs space-y-1.5">
                  <div className="font-semibold text-slate-900">FraudShield Design Principle:</div>
                  <p>
                    {executionResult.risk_level === 'HIGH'
                      ? 'Account takeover attacks exhibit combined anomalies (unseen hardware + remote IP + spend ratio > 5x). Single signals do not dominate.'
                      : 'High purchase amounts alone do NOT result in fraud flags when initiated from verified devices and home locations.'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
