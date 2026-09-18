// src/pages/ModernizationPage.tsx
import React, { useState, useEffect, useMemo } from 'react';
import { Workbook } from '../types';
import { workbookAPI, agentAPI } from '../utils/api';
import AIInsightPanel from '../components/common/AIInsightPanel';
import ArchitectureDiagramModal from '../components/common/ArchitectureDiagramModal';

export default function ModernizationPage({ workbook }: { workbook: Workbook }) {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [risks, setRisks] = useState<any[]>([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [selectedAppId, setSelectedAppId] = useState<string>('');
  const [aiNarrative, setAiNarrative] = useState<string | null>(null);
  const [aiGenerated, setAiGenerated] = useState<boolean | undefined>(undefined);
  const [aiFallbackReason, setAiFallbackReason] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [diagramRec, setDiagramRec] = useState<{ id: string; title: string } | null>(null);
  const [riskAiInsight, setRiskAiInsight] = useState<{ narrative: string | null; generated?: boolean; reason?: string | null } | null>(null);
  const [riskAiLoading, setRiskAiLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [riskData, apps] = await Promise.all([
          workbookAPI.getRisks(workbook.workbook_id),
          workbookAPI.getApplications(workbook.workbook_id)
        ]);
        setRisks(riskData);
        setApplications(apps);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [workbook.workbook_id]);

  const filteredRecommendations = useMemo(() => {
    if (!selectedAppId) return recommendations;
    return recommendations.filter((rec: any) => rec.applicationId === selectedAppId);
  }, [recommendations, selectedAppId]);

  const handlePrioritizeRisks = async () => {
    try {
      setRiskAiLoading(true);
      const result = await agentAPI.analyzeWithAgent(workbook.workbook_id, 'security_continuity_guardian', {});
      const f = result?.findings || {};
      const notesById: Record<string, string> = {};
      [...(f.security_risks || []), ...(f.continuity_risks || [])].forEach((r: any) => {
        if (r.id && r.ai_priority_note) notesById[r.id] = r.ai_priority_note;
      });
      if (Object.keys(notesById).length > 0) {
        setRisks((prev) => prev.map((r) => (notesById[r.id] ? { ...r, ai_priority_note: notesById[r.id] } : r)));
      }
      setRiskAiInsight({ narrative: f.ai_narrative || f.summary || null, generated: f.ai_generated, reason: f.ai_fallback_reason });
    } catch (err) {
      setRiskAiInsight({ narrative: null, generated: false, reason: err instanceof Error ? err.message : 'Failed to prioritize risks with AI' });
    } finally {
      setRiskAiLoading(false);
    }
  };

  const handleGenerateRecommendations = async () => {
    try {
      setGenerating(true);
      setError(null);
      const result = await agentAPI.analyzeWithAgent(
        workbook.workbook_id,
        'modernization_strategist',
        { include_risks: true, include_dependencies: true }
      );
      setAiNarrative(result?.findings?.ai_narrative || null);
      setAiGenerated(result?.findings?.ai_generated);
      setAiFallbackReason(result?.findings?.ai_fallback_reason || null);

      // Use actual recommendations from API response
      if (result?.findings?.recommendations && Array.isArray(result.findings.recommendations)) {
        const recsFromAPI = result.findings.recommendations.map((rec: any) => ({
          id: rec.id,
          title: rec.recommendation || rec.title,
          priority: rec.priority || 'P3',
          strategy: rec.strategy || 'Modernize',
          targetTech: rec.target_tech,
          effort: rec.effort_estimate || rec.effort || 'Unknown',
          riskLevel: rec.risk_level || 'Medium',
          preservesContinuity: rec.preserves_continuity,
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

  const priorityColors: Record<string, string> = {
    'P1': 'text-red-400',
    'P2': 'text-yellow-400',
    'P3': 'text-blue-400',
    'P4': 'text-slate-400',
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
            <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
              <h2 className="text-2xl font-bold text-slate-50">Identified Risks ({risks.length})</h2>
              <button
                onClick={handlePrioritizeRisks}
                disabled={riskAiLoading}
                className="px-4 py-2 rounded-lg text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 text-white transition-all"
              >
                {riskAiLoading ? 'Prioritizing...' : '✨ AI-Prioritize Security/Continuity Risks'}
              </button>
            </div>
            {riskAiInsight && (
              <AIInsightPanel narrative={riskAiInsight.narrative} aiGenerated={riskAiInsight.generated} fallbackReason={riskAiInsight.reason} />
            )}
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {risks.slice(0, 10).map((risk) => (
                <div key={risk.id} className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="font-semibold text-slate-50">{risk.entity_id} <span className="text-slate-500 font-normal">({risk.risk_type})</span></p>
                      <p className="text-slate-400 text-sm">{risk.risk_description}</p>
                      {(risk.severity === 'critical' || risk.severity === 'high') && risk.remediation && (
                        <div className="mt-2 pt-2 border-t border-slate-700/70">
                          <p className="text-xs text-slate-500 uppercase tracking-wide font-semibold mb-0.5">
                            Why this matters &amp; how to fix it
                          </p>
                          <p className="text-slate-300 text-xs">
                            Entity type: <span className="text-slate-200">{risk.entity_type || 'unknown'}</span> ·
                            Risk category: <span className="text-slate-200">{risk.risk_type}</span>
                          </p>
                          <p className="text-cyan-300/90 text-xs mt-1">✓ Recommended remediation: {risk.remediation}</p>
                        </div>
                      )}
                      {risk.ai_priority_note && (
                        <p className="text-indigo-300/90 text-xs mt-2 italic">✨ {risk.ai_priority_note}</p>
                      )}
                    </div>
                    <span className={`text-sm font-semibold px-3 py-1 rounded ${
                      risk.severity === 'critical' ? 'bg-red-900/30 text-red-300' :
                      risk.severity === 'high' ? 'bg-orange-900/30 text-orange-300' :
                      risk.severity === 'medium' ? 'bg-yellow-900/30 text-yellow-300' :
                      'bg-green-900/30 text-green-300'
                    }`}>
                      {risk.severity?.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Generate Recommendations */}
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
            <h2 className="text-2xl font-bold text-slate-50">Strategic Recommendations</h2>
            {recommendations.length > 0 && (
              <select
                value={selectedAppId}
                onChange={(e) => setSelectedAppId(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-50 text-sm focus:outline-none focus:border-cyan-600"
              >
                <option value="">All Applications</option>
                {applications.map((app: any) => (
                  <option key={app.id} value={app.id}>{app.name}</option>
                ))}
              </select>
            )}
          </div>
          <button
            onClick={handleGenerateRecommendations}
            disabled={generating}
            className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all mb-6"
          >
            {generating ? 'Analyzing Risks...' : 'Generate Recommendations'}
          </button>

          <AIInsightPanel narrative={aiNarrative} aiGenerated={aiGenerated} fallbackReason={aiFallbackReason} />

          {filteredRecommendations.length > 0 && (
            <div className="space-y-4">
              {filteredRecommendations.map((rec: any) => (
                <div
                  key={rec.id || `rec-${rec.rule_id || rec.title}`}
                  className="bg-slate-800 p-6 rounded-lg border border-slate-700 cursor-pointer hover:border-cyan-600 transition-colors"
                  onClick={() => setDiagramRec({ id: rec.id, title: rec.title })}
                  title="Click to view before/after architecture diagram"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-lg font-bold text-slate-50">{rec.title}</h3>
                      <div className="flex gap-2 mt-2 flex-wrap">
                        {rec.targetTech && (
                          <span className="text-xs font-semibold px-2 py-1 rounded bg-green-900/40 text-green-300 border border-green-700/50">
                            🎯 {rec.targetTech}
                          </span>
                        )}
                        {rec.strategy && (
                          <span className="text-xs font-semibold px-2 py-1 rounded bg-indigo-900/40 text-indigo-300 border border-indigo-700/50">
                            {rec.strategy}
                          </span>
                        )}
                      </div>
                      <p className="text-slate-400 text-sm mt-2">{rec.description}</p>
                    </div>
                    <span className={`px-3 py-1 rounded text-sm font-semibold ${priorityColors[rec.priority] || 'text-slate-300'}`}>
                      {rec.priority}
                    </span>
                  </div>

                  <div className="grid grid-cols-4 gap-4 mt-4">
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Target Tech</p>
                      <span className="text-sm font-semibold px-3 py-1 rounded bg-slate-700 text-slate-200">
                        {rec.targetTech || 'N/A'}
                      </span>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Effort Points</p>
                      <p className="font-bold text-slate-50">{rec.effort}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Risk Level</p>
                      <p className="font-bold text-yellow-400">{rec.riskLevel}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Preserves Continuity</p>
                      <p className={`font-bold ${rec.preservesContinuity === 'N' ? 'text-red-400' : 'text-green-400'}`}>
                        {rec.preservesContinuity === 'Y' ? 'Yes' : rec.preservesContinuity === 'N' ? 'No' : 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {recommendations.length > 0 && filteredRecommendations.length === 0 && (
            <p className="text-slate-500">No recommendations for the selected application</p>
          )}

          {recommendations.length === 0 && !generating && (
            <p className="text-slate-500">Click "Generate Recommendations" to create a modernization strategy</p>
          )}
        </div>
      </div>

      <ArchitectureDiagramModal
        workbookId={workbook.workbook_id}
        recommendationId={diagramRec?.id || null}
        recommendationTitle={diagramRec?.title}
        onClose={() => setDiagramRec(null)}
      />
    </div>
  );
}
