import { AnalyzeRequest, DashboardStats, Scenario, Transaction } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const err = await response.json();
      errorDetail = err.detail || err.error || errorDetail;
    } catch {
      // Use fallback
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  async getHealth(): Promise<{ status: string; environment: string; inference_engine: string }> {
    return fetchJson(`${API_BASE_URL}/health`);
  },

  async analyzeTransaction(payload: AnalyzeRequest): Promise<Transaction> {
    return fetchJson<Transaction>(`${API_BASE_URL}/transactions/analyze`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getTransactions(
    limit = 20,
    offset = 0,
    riskLevel?: string
  ): Promise<{ items: Transaction[]; total: number; limit: number; offset: number }> {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (riskLevel && riskLevel !== 'ALL') {
      params.append('risk_level', riskLevel);
    }
    return fetchJson(`${API_BASE_URL}/transactions?${params.toString()}`);
  },

  async getTransaction(id: string): Promise<Transaction> {
    return fetchJson<Transaction>(`${API_BASE_URL}/transactions/${encodeURIComponent(id)}`);
  },

  async getAlerts(limit = 50): Promise<{ alerts: Transaction[]; count: number }> {
    return fetchJson(`${API_BASE_URL}/alerts?limit=${limit}`);
  },

  async reviewAlert(
    id: string,
    reviewStatus: string,
    notes = ''
  ): Promise<Transaction> {
    return fetchJson<Transaction>(`${API_BASE_URL}/alerts/${encodeURIComponent(id)}/review`, {
      method: 'POST',
      body: JSON.stringify({ review_status: reviewStatus, notes }),
    });
  },

  async getStats(): Promise<DashboardStats> {
    return fetchJson<DashboardStats>(`${API_BASE_URL}/stats`);
  },

  async getScenarios(): Promise<Scenario[]> {
    return fetchJson<Scenario[]>(`${API_BASE_URL}/scenarios`);
  },
};
