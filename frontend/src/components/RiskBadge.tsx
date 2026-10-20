import React from 'react';
import { RiskLevel, RecommendedAction } from '../types';
import { CheckCircle2, AlertTriangle, ShieldAlert, ShieldCheck } from 'lucide-react';

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, className = '' }) => {
  switch (level) {
    case 'HIGH':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200/80 ${className}`}>
          <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
          HIGH RISK
        </span>
      );
    case 'MEDIUM':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200/80 ${className}`}>
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
          MEDIUM RISK
        </span>
      );
    case 'LOW':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80 ${className}`}>
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          LOW RISK
        </span>
      );
  }
};

interface ActionBadgeProps {
  action: RecommendedAction;
  className?: string;
}

export const ActionBadge: React.FC<ActionBadgeProps> = ({ action, className = '' }) => {
  switch (action) {
    case 'FLAG_FOR_REVIEW':
      return (
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium bg-rose-100 text-rose-800 ${className}`}>
          Flag For Review
        </span>
      );
    case 'VERIFY_MFA':
      return (
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium bg-amber-100 text-amber-800 ${className}`}>
          Trigger MFA
        </span>
      );
    case 'APPROVE':
    default:
      return (
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium bg-emerald-100 text-emerald-800 ${className}`}>
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          Approved
        </span>
      );
  }
};
