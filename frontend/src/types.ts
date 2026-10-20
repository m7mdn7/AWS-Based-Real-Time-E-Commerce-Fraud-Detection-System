export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type RecommendedAction = 'APPROVE' | 'VERIFY_MFA' | 'FLAG_FOR_REVIEW';
export type ReviewStatus = 'PENDING_REVIEW' | 'FLAGGED_FOR_REVIEW' | 'AUTOMATICALLY_CLEARED' | 'CONFIRMED_FRAUD' | 'FALSE_POSITIVE' | 'WHITELISTED';

export interface Transaction {
  transaction_id: string;
  user_id: string;
  amount: number;
  merchant?: string;
  merchant_category?: string;
  location?: string;
  device_id?: string;
  ip_address?: string;
  timestamp: string;
  risk_score: number;
  risk_level: RiskLevel;
  prediction: string;
  recommended_action: RecommendedAction;
  risk_factors: string[];
  engine_info?: string;
  review_status?: ReviewStatus;
  review_notes?: string;
  created_at?: string;
}

export interface DashboardStats {
  total_transactions: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  alert_count: number;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  payload: {
    transaction_id: string;
    user_id: string;
    amount: number;
    merchant: string;
    merchant_category: string;
    location: string;
    device_id: string;
    ip_address: string;
  };
}

export interface AnalyzeRequest {
  transaction_id: string;
  user_id: string;
  amount: number;
  merchant?: string;
  merchant_category?: string;
  location?: string;
  device_id?: string;
  ip_address?: string;
  timestamp?: string;
}
