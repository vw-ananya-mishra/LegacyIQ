// src/pages/ModernizationPage.tsx
import React, { useState, useEffect } from 'react';
import { Workbook } from '../types';
import { workbookAPI, agentAPI } from '../utils/api';

export default function ModernizationPage({ workbook }: { workbook: Workbook }) {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [risks, setRisks] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const riskData = await workbookAPI.getRisks(workbook.workbook_id);
        setRisks(riskData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [workbook.workbook_id]);

  const handleGenerateRecommendations = async () => {
    try {
      setGenerating(true);
      setError(null);
      const result = await agentAPI.analyzeWithAgent(
        workbook.workbook_id,
        'modernization_strategist',
        { include_risks: true, include_dependencies: true }
      );

      // Use actual recommendations from API response
      if (result?.findings?.recommendations && Array.isArray(result.findings.recommendations)) {
        const recsFromAPI = result.findings.recommendations.map((rec: any) => ({
          id: rec.id,
          title: rec.recommendation || rec.title,
          priority: rec.priority || rec.priority_level || 'MEDIUM',
          strategy: rec.strategy || 'Modernize',
          effort: rec.effort_estimate || rec.effort || 'Medium',
          riskLevel: rec.risk_level || 'Medium',
          dependencies: Array.isArray(rec.dependencies) ? rec.dependencies.join(', ') : rec.dependencies || 'None',
          status: rec.status || 'draft',
          applicationId: rec.application_id,
          moduleId: rec.module_id,
          description: rec.recommendation || 'Modernization recommendation based on backlog analysis'
        }));
        setRecommendations(recsFromAPI);
      } else {
        // Fallback: mock recommendations
        const mockRecommendations = risks.slice(0, 5).map((risk, index) => ({
          id: `rec-${index}`,
          title: `Address ${risk.risk_description || 'Risk'}`,
          priority: risk.severity || 'MEDIUM',
          strategy: 'Modernize',
          effort: 'Medium',
          riskLevel: risk.severity || 'Medium',
          description: risk.remediation || 'Evidence-based recommendation'
        }));
        setRecommendations(mockRecommendations);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate recommendations');
    } finally {
      setGenerating(false);
    }
  };

  const strategyColors: Record<string, string> = {
    'Rehost': 'bg-blue-900/30 text-blue-300',
    'Replatform': 'bg-purple-900/30 text-purple-300',
    'Refactor': 'bg-green-900/30 text-green-300',
    'Re-architect': 'bg-red-900/30 text-red-300',
  };

  const priorityColors: Record<string, string> = {
    'CRITICAL': 'text-red-400',
    'HIGH': 'text-yellow-400',
    'MEDIUM': 'text-blue-400',
  };

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Modernization Strategy</h1>
        <p className="text-slate-400 mb-8">
          Evidence-based recommendations with risk and continuity analysis
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {/* Modernization Roadmap */}
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-slate-50 mb-6">Modernization Roadmap</h2>
          <div className="flex gap-4 overflow-x-auto pb-4">
            {['Protect', 'Understand', 'Isolate', 'Migrate', 'Retire'].map((stage, index) => (
              <div
                key={stage}
                className="flex-shrink-0 p-6 bg-slate-800 rounded-lg border border-slate-700 text-center min-w-[150px]"
              >
                <div className="text-2xl font-bold text-cyan-400 mb-2">{index + 1}</div>
                <p className="font-semibold text-slate-50">{stage}</p>
                <p className="text-slate-400 text-xs mt-2">Phase {index + 1}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Identified Risks */}
        {risks.length > 0 && (
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-slate-50 mb-4">Identified Risks ({risks.length})</h2>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {risks.slice(0, 10).map((risk) => (
                <div key={risk.id} className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-slate-50">{risk.component}</p>
                      <p className="text-slate-400 text-sm">{risk.risk_description}</p>
                    </div>
                    <span className={`text-sm font-semibold px-3 py-1 rounded ${
                      risk.severity === 'HIGH' ? 'bg-red-900/30 text-red-300' :
                      risk.severity === 'MEDIUM' ? 'bg-yellow-900/30 text-yellow-300' :
                      'bg-green-900/30 text-green-300'
                    }`}>
                      {risk.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Generate Recommendations */}
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-slate-50 mb-4">Strategic Recommendations</h2>
          <button
            onClick={handleGenerateRecommendations}
            disabled={generating || risks.length === 0}
            className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all mb-6"
          >
            {generating ? 'Analyzing Risks...' : 'Generate Recommendations'}
          </button>

          {recommendations.length > 0 && (
            <div className="space-y-4">
              {recommendations.map((rec: any) => (
                <div key={rec.id || `rec-${rec.rule_id || rec.title}`} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-lg font-bold text-slate-50">{rec.title}</h3>
                      <p className="text-slate-400 text-sm mt-1">{rec.description}</p>
                    </div>
                    <span className={`px-3 py-1 rounded text-sm font-semibold ${priorityColors[rec.priority] || 'text-slate-300'}`}>
                      {rec.priority}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Strategy</p>
                      <span className={`text-sm font-semibold px-3 py-1 rounded ${strategyColors[rec.strategy] || ''}`}>
                        {rec.strategy}
                      </span>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Estimated Effort</p>
                      <p className="font-bold text-slate-50">{rec.effort} days</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Risk Reduction</p>
                      <p className="font-bold text-green-400">{rec.riskReduction}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {recommendations.length === 0 && !generating && (
            <p className="text-slate-500">Click "Generate Recommendations" to create a modernization strategy</p>
          )}
        </div>
      </div>
    </div>
  );
}
