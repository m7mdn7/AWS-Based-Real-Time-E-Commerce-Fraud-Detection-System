import React from 'react';
import {
  Cloud,
  Server,
  Database,
  Cpu,
  Layers,
  Shield,
  FileCode,
  Activity,
  Lock,
  ArrowRight
} from 'lucide-react';

export const ArchitectureView: React.FC = () => {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <div className="flex items-center gap-2 text-cyan-600 text-xs font-semibold uppercase tracking-wider">
          <Cloud className="w-4 h-4" />
          Cloud Native & Serverless Infrastructure
        </div>
        <h2 className="text-xl font-bold text-slate-900 mt-1">System Architecture & AWS Cloud Design</h2>
        <p className="text-xs text-slate-500 mt-0.5 max-w-3xl">
          AWS FraudShield is built on a hexagonal decoupled architecture. In development, it executes zero-cloud local
          SQLite and Scikit-Learn pipelines. In production, it scales seamlessly on AWS serverless primitives.
        </p>
      </div>

      {/* Cloud Topology Diagram */}
      <div className="bg-slate-950 text-white p-8 rounded-2xl border border-slate-800 shadow-xl overflow-hidden relative">
        <div className="absolute top-4 right-4 px-3 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-full text-[11px] font-mono">
          Architecture Reference
        </div>

        <div className="max-w-4xl mx-auto py-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center text-center">
            {/* React Frontend */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-2">
                <Layers className="w-5 h-5" />
              </div>
              <span className="text-xs font-bold text-white">React + Vite</span>
              <span className="text-[10px] text-slate-400 mt-0.5">TypeScript / Tailwind</span>
            </div>

            <div className="text-cyan-400 hidden md:flex justify-center">
              <ArrowRight className="w-5 h-5" />
            </div>

            {/* Amazon API Gateway */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center mb-2">
                <Server className="w-5 h-5" />
              </div>
              <span className="text-xs font-bold text-white">API Gateway</span>
              <span className="text-[10px] text-slate-400 mt-0.5">REST Proxy / CORS</span>
            </div>

            <div className="text-cyan-400 hidden md:flex justify-center">
              <ArrowRight className="w-5 h-5" />
            </div>

            {/* AWS Lambda */}
            <div className="p-5 rounded-xl bg-slate-900 border border-cyan-500/40 ring-1 ring-cyan-500/20 flex flex-col items-center">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/20 text-cyan-300 flex items-center justify-center mb-2">
                <Shield className="w-5 h-5" />
              </div>
              <span className="text-xs font-bold text-white">AWS Lambda</span>
              <span className="text-[10px] text-cyan-400 mt-0.5">fraudshield-analyzer</span>
            </div>
          </div>

          {/* Subsystem Tier */}
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 pt-8 border-t border-slate-800/80">
            {/* DynamoDB */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 shrink-0">
                <Database className="w-4 h-4" />
              </div>
              <div className="text-left">
                <span className="text-xs font-bold text-white block">Amazon DynamoDB</span>
                <span className="text-[11px] text-slate-400 leading-tight block mt-0.5">
                  Transactions & User Historical Baseline Profiles
                </span>
              </div>
            </div>

            {/* Amazon SageMaker */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
                <Cpu className="w-4 h-4" />
              </div>
              <div className="text-left">
                <span className="text-xs font-bold text-white">Amazon SageMaker</span>
                <span className="text-[11px] text-slate-400 leading-tight block mt-0.5">
                  Real-Time XGBoost Inference Endpoint
                </span>
              </div>
            </div>

            {/* CloudWatch Logs */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 shrink-0">
                <Activity className="w-4 h-4" />
              </div>
              <div className="text-left">
                <span className="text-xs font-bold text-white">Amazon CloudWatch</span>
                <span className="text-[11px] text-slate-400 leading-tight block mt-0.5">
                  Structured Latency & Audit Logging
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Component Details Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Local Dev vs Cloud Deployment */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-600" />
            Hexagonal Adapter Pattern
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            The core machine learning engine does not couple directly to cloud services. The abstraction layer allows
            the exact same business logic to run locally with zero credentials or on AWS:
          </p>
          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center">
              <span className="font-medium text-slate-700">Storage Layer</span>
              <span className="font-mono text-slate-600">SQLite (Local) ↔ DynamoDB (AWS)</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center">
              <span className="font-medium text-slate-700">Inference Engine</span>
              <span className="font-mono text-slate-600">Joblib Pipeline ↔ SageMaker Runtime</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center">
              <span className="font-medium text-slate-700">API Host</span>
              <span className="font-mono text-slate-600">FastAPI (Uvicorn) ↔ API Gateway + Lambda</span>
            </div>
          </div>
        </div>

        {/* Security & Least-Privilege IAM */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Lock className="w-4 h-4 text-emerald-600" />
            Security & Least-Privilege Governance
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Following AWS Well-Architected Security best practices:
          </p>
          <ul className="space-y-2 text-xs text-slate-600">
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
              <span><strong>No Hardcoded Credentials:</strong> IAM Roles assigned directly to AWS Lambda execution environments.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
              <span><strong>Restricted DynamoDB Actions:</strong> Read/Write scopes limited strictly to transactions and user tables.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
              <span><strong>Zero Data Leakage:</strong> Behavioral features only compute with data available at transaction time.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
