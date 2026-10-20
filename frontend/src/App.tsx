import React, { useState, useEffect } from 'react';
import { Sidebar, NavTab } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { Simulator } from './pages/Simulator';
import { Scenarios } from './pages/Scenarios';
import { Transactions } from './pages/Transactions';
import { Alerts } from './pages/Alerts';
import { ArchitectureView } from './pages/ArchitectureView';
import { Transaction } from './types';
import { api } from './api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [alertCount, setAlertCount] = useState<number>(0);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchGlobalStats = async () => {
    try {
      setLoading(true);
      const stats = await api.getStats();
      setAlertCount(stats.alert_count || 0);
    } catch {
      // Backend might be offline during initial boot
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGlobalStats();
  }, [refreshTrigger]);

  const handleRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const getPageTitle = (): { title: string; subtitle: string } => {
    switch (currentTab) {
      case 'dashboard':
        return {
          title: 'Executive Fraud Monitoring Dashboard',
          subtitle: 'Real-time telemetry, transaction volumes, and intercepted threat patterns',
        };
      case 'simulator':
        return {
          title: 'Transaction Risk Scoring Simulator',
          subtitle: 'Evaluate custom behavioral payloads against the trained ML pipeline',
        };
      case 'scenarios':
        return {
          title: 'Simulated Fraud & Anomaly Scenarios',
          subtitle: 'Pre-configured test attacks demonstrating multidimensional signal verification',
        };
      case 'history':
        return {
          title: 'Evaluated Transaction Registry',
          subtitle: 'Comprehensive audit log of all scored transactions and customer profiles',
        };
      case 'alerts':
        return {
          title: 'Security Operations Alert Queue',
          subtitle: 'Prioritized investigation workbench for high & medium-risk flags',
        };
      case 'architecture':
        return {
          title: 'Cloud Infrastructure & Decoupled Design',
          subtitle: 'AWS Serverless topology, least-privilege IAM, and local mock interfaces',
        };
    }
  };

  const { title, subtitle } = getPageTitle();

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden text-slate-900">
      {/* Left Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        alertCount={alertCount}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <Header
          title={title}
          subtitle={subtitle}
          onRefresh={handleRefresh}
          isLoading={loading}
        />

        <main className="flex-1 pb-16">
          {currentTab === 'dashboard' && (
            <Dashboard
              onSelectTransaction={() => setCurrentTab('history')}
              onNavigateToSimulator={() => setCurrentTab('simulator')}
            />
          )}
          {currentTab === 'simulator' && <Simulator />}
          {currentTab === 'scenarios' && <Scenarios />}
          {currentTab === 'history' && <Transactions />}
          {currentTab === 'alerts' && <Alerts />}
          {currentTab === 'architecture' && <ArchitectureView />}
        </main>
      </div>
    </div>
  );
};

export default App;
