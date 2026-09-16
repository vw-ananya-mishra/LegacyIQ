// Dashboard Page - Command Center
// src/pages/DashboardPage.tsx

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Workbook, DashboardSummary } from '../types';
import { workbookAPI } from '../utils/api';
import { AlertTriangle, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';

interface DashboardPageProps {
  workbook: Workbook;
}

export default function DashboardPage({ workbook }: DashboardPageProps) {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, [workbook.workbook_id]);

  const loadDashboard = async () => {
    try {
      const data = await workbookAPI.getDashboardSummary(workbook.workbook_id);
      setSummary(data);
      setLoading(false);
    } catch (err) {
      setError(`Failed to load dashboard: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
          <p className="mt-4 text-slate-300">Loading Command Center...</p>
        </div>
      </div>
    );
  }

  if (!summary || error) {
    return (
      <div className="p-8">
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
          <p className="text-red-200">{error}</p>
        </div>
      </div>
    );
  }

  const stages = [
    { key: 'understand', label: 'UNDERSTAND', icon: '🔍', path: '/understand' },
    { key: 'document', label: 'DOCUMENT', icon: '📋', path: '/document' },
    { key: 'map', label: 'MAP', icon: '🗺️', path: '/dependencies' },
    { key: 'test', label: 'TEST', icon: '✅', path: '/parity' },
    { key: 'modernize', label: 'MODERNIZE', icon: '🚀', path: '/modernize' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-2 text-slate-50">
            Command Center
          </h1>
          <p className="text-slate-400">
            {summary.applications} Applications | {summary.modules} Modules | {summary.business_rules} Rules | {summary.dependencies} Dependencies
          </p>
        </div>

        {/* Modernization Pipeline */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-slate-50">
            Modernization Pipeline
          </h2>
          
          <div className="grid grid-cols-5 gap-4">
            {stages.map((stage, idx) => {
              const stageData = summary.pipeline[stage.key as keyof typeof summary.pipeline];
              const isCompleted = stageData.completion === 100;
              const isInProgress = stageData.completion > 0 && stageData.completion < 100;
              
              return (
                <div key={stage.key} className="relative">
                  {idx < stages.length - 1 && (
                    <div className="absolute top-20 -right-2 w-4 h-1 bg-slate-700"></div>
                  )}
                  
                  <button
                    onClick={() => navigate(stage.path)}
                    className={`w-full p-6 rounded-lg border-2 transition-all cursor-pointer hover:scale-105 ${
                      isCompleted
                        ? 'bg-green-900/20 border-green-600 hover:border-green-500'
                        : isInProgress
                        ? 'bg-blue-900/20 border-blue-600 hover:border-blue-500'
                        : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                    }`}
                  >
                    <div className="text-3xl mb-2">{stage.icon}</div>
                    <h3 className="font-bold text-sm text-slate-50">{stage.label}</h3>
                    
                    <div className="mt-3 w-full bg-slate-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          isCompleted
                            ? 'bg-green-500'
                            : isInProgress
                            ? 'bg-blue-500'
                            : 'bg-slate-600'
                        }`}
                        style={{ width: `${stageData.completion}%` }}
                      ></div>
                    </div>
                    
                    <p className="text-xs text-slate-400 mt-2">
                      {Math.round(stageData.completion)}%
                    </p>
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <MetricCard title="Applications" value={summary.applications} icon={<TrendingUp className="w-6 h-6" />} />
          <MetricCard title="Code Modules" value={summary.modules} icon={<TrendingUp className="w-6 h-6" />} />
          <MetricCard title="Business Rules" value={summary.business_rules} icon={<TrendingUp className="w-6 h-6" />} />
          <MetricCard title="Dependencies" value={summary.dependencies} icon={<TrendingUp className="w-6 h-6" />} />
        </div>

        {/* Coverage Metrics */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-slate-50">Coverage Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <CoverageCard title="Rule Test Coverage" percentage={summary.metrics.rule_test_coverage} description="Business rules with test cases" />
            <CoverageCard title="Module Test Coverage" percentage={summary.metrics.module_test_coverage} description="Modules with test coverage" />
            <CoverageCard title="Documentation Coverage" percentage={summary.metrics.module_documentation_coverage} description="Documented modules" />
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-4 text-slate-50">Recommended Next Steps</h3>
          <div className="space-y-3">
            <Step number={1} title="Understand the Estate" status="ready" description="Analyze applications, modules, and business rules" onAction={() => navigate('/understand')} />
            <Step number={2} title="Generate Documentation" status="ready" description="Create functional specs and API documentation" onAction={() => navigate('/document')} />
            <Step number={3} title="Map Dependencies" status="ready" description="Visualize dependency graph and identify risks" onAction={() => navigate('/dependencies')} />
            <Step number={4} title="Validate Parity" status="pending" description="Generate and execute parity tests" onAction={() => navigate('/parity')} />
            <Step number={5} title="Plan Modernization" status="pending" description="Create risk-aware modernization recommendations" onAction={() => navigate('/modernize')} />
          </div>
        </div>
      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
}

function MetricCard({ title, value, icon }: MetricCardProps) {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm">{title}</p>
          <p className="text-3xl font-bold text-slate-50">{value}</p>
        </div>
        <div className="text-cyan-400 opacity-50">{icon}</div>
      </div>
    </div>
  );
}

interface CoverageCardProps {
  title: string;
  percentage: number;
  description: string;
}

function CoverageCard({ title, percentage, description }: CoverageCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
      <h4 className="font-semibold text-slate-50 mb-2">{title}</h4>
      <p className="text-slate-400 text-sm mb-4">{description}</p>
      <div className="mb-3">
        <div className="w-full bg-slate-700 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${
              percentage >= 75 ? 'bg-green-500' : percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          ></div>
        </div>
      </div>
      <p className="text-2xl font-bold text-cyan-400">{percentage.toFixed(1)}%</p>
    </div>
  );
}

interface StepProps {
  number: number;
  title: string;
  status: 'ready' | 'pending' | 'completed';
  description: string;
  onAction?: () => void;
}

function Step({ number, title, status, description, onAction }: StepProps) {
  const statusIcon = {
    ready: <CheckCircle className="w-5 h-5 text-green-400" />,
    pending: <AlertCircle className="w-5 h-5 text-yellow-400" />,
    completed: <CheckCircle className="w-5 h-5 text-blue-400" />,
  };

  return (
    <button
      onClick={onAction}
      className="w-full flex items-start gap-4 p-3 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors cursor-pointer text-left"
    >
      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-700 text-slate-300 font-bold flex-shrink-0">
        {number}
      </div>
      <div className="flex-1">
        <p className="font-semibold text-slate-50">{title}</p>
        <p className="text-slate-400 text-sm">{description}</p>
      </div>
      {statusIcon[status]}
    </button>
  );
}
