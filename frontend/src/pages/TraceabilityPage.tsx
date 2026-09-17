// src/pages/TraceabilityPage.tsx
import React, { useState, useEffect } from 'react';
import { Workbook } from '../types';
import { workbookAPI, traceabilityAPI } from '../utils/api';
import AIInsightPanel from '../components/common/AIInsightPanel';

type TabType = 'applications' | 'modules' | 'rules' | 'dependencies';
type ItemType = 'application' | 'module' | 'rule' | 'dependency';

function itemLabel(item: any, itemType: string): string {
  if (itemType === 'application') return item.name;
  if (itemType === 'module') return item.name;
  if (itemType === 'rule') return item.rule_name;
  if (itemType === 'dependency') return `${item.source_id} → ${item.target_id}`;
  return item.id;
}

export default function TraceabilityPage({ workbook }: { workbook: Workbook }) {
  const [activeTab, setActiveTab] = useState<TabType>('applications');
  const [applications, setApplications] = useState<any[]>([]);
  const [modules, setModules] = useState<any[]>([]);
  const [businessRules, setBusinessRules] = useState<any[]>([]);
  const [dependencies, setDependencies] = useState<any[]>([]);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [traceData, setTraceData] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [tracing, setTracing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiInsight, setAiInsight] = useState<{ narrative: string | null; generated?: boolean; reason?: string | null } | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [apps, mods, rules, deps] = await Promise.all([
          workbookAPI.getApplications(workbook.workbook_id),
          workbookAPI.getModules(workbook.workbook_id),
          workbookAPI.getBusinessRules(workbook.workbook_id),
          workbookAPI.getDependencies(workbook.workbook_id),
        ]);
        setApplications(apps);
        setModules(mods);
        setBusinessRules(rules);
        setDependencies(deps);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [workbook.workbook_id]);

  const handleTraceItem = async (item: any, itemType: ItemType) => {
    try {
      setTracing(true);
      setError(null);
      setSelectedItem({ ...item, itemType });
      setAiInsight(null);
      const trace = await traceabilityAPI.traceFinding(workbook.workbook_id, item.id, itemType);
      setTraceData(Array.isArray(trace) ? trace : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trace item');
      setTraceData([]);
    } finally {
      setTracing(false);
    }
  };

  const handleExplainTrace = async () => {
    if (!selectedItem || !traceData) return;
    try {
      setAiLoading(true);
      const result = await traceabilityAPI.explainTrace(workbook.workbook_id, selectedItem.id, selectedItem.itemType, traceData);
      setAiInsight({ narrative: result?.ai_narrative || null, generated: result?.ai_generated, reason: result?.ai_generated === false ? 'AI provider unavailable — showing evidence chain only, not AI-generated.' : null });
    } catch (err) {
      setAiInsight({ narrative: null, generated: false, reason: err instanceof Error ? err.message : 'Failed to generate AI explanation' });
    } finally {
      setAiLoading(false);
    }
  };

  const renderList = (items: any[], itemType: ItemType, subtitleFn: (item: any) => string) => (
    <div className="space-y-2">
      {items.slice(0, 30).map((item: any) => (
        <button
          key={item.id}
          onClick={() => handleTraceItem(item, itemType)}
          className={`w-full text-left p-3 rounded-lg border transition-all ${
            selectedItem?.id === item.id && selectedItem?.itemType === itemType
              ? 'bg-cyan-900/30 border-cyan-600'
              : 'bg-slate-800 border-slate-700 hover:border-slate-600'
          }`}
        >
          <p className="font-semibold text-slate-50 text-sm">{itemLabel(item, itemType)}</p>
          <p className="text-slate-400 text-xs">{subtitleFn(item)}</p>
        </button>
      ))}
      {items.length > 30 && <p className="text-slate-500 text-xs mt-2">Showing 30 of {items.length}</p>}
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Traceability Center</h1>
        <p className="text-slate-400 mb-8">
          Complete audit trail for every finding, recommendation, and risk.
          Select any item to trace it back to source data.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Item List */}
          <div className="lg:col-span-1">
            {/* Tab Buttons */}
            <div className="flex gap-2 mb-4 flex-wrap">
              {(['applications', 'modules', 'rules', 'dependencies'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-3 py-2 rounded text-sm font-semibold transition-all ${
                    activeTab === tab
                      ? 'bg-cyan-600 text-white'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Items List */}
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 max-h-[600px] overflow-y-auto">
              {loading ? (
                <p className="text-slate-500">Loading...</p>
              ) : activeTab === 'applications' ? (
                renderList(applications, 'application', (app) => `${app.primary_language || 'N/A'} · ${app.criticality || 'N/A'}`)
              ) : activeTab === 'modules' ? (
                renderList(modules, 'module', (mod) => `${mod.module_type || 'N/A'} · complexity ${mod.complexity_score ?? 'N/A'}`)
              ) : activeTab === 'rules' ? (
                renderList(businessRules, 'rule', (rule) => `${rule.business_domain || 'N/A'} · ${rule.criticality || 'N/A'}`)
              ) : (
                renderList(dependencies, 'dependency', (dep) => `${dep.relationship_type || 'depends_on'} · ${dep.criticality || 'medium'}`)
              )}
            </div>
          </div>

          {/* Right Panel - Trace Information */}
          <div className="lg:col-span-2">
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
              {selectedItem ? (
                <div>
                  <h2 className="text-xl font-bold text-slate-50 mb-4 flex items-center justify-between">
                    <span>{itemLabel(selectedItem, selectedItem.itemType)}</span>
                    {tracing && <span className="text-sm text-slate-400">Tracing...</span>}
                  </h2>

                  {/* Trace Chain */}
                  {traceData && traceData.length > 0 ? (
                    <div className="space-y-4">
                      <div>
                        <button
                          onClick={handleExplainTrace}
                          disabled={aiLoading}
                          className="px-4 py-2 rounded-lg text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 text-white transition-all mb-3"
                        >
                          {aiLoading ? 'Explaining...' : '✨ Explain with AI'}
                        </button>
                        {aiInsight && (
                          <AIInsightPanel narrative={aiInsight.narrative} aiGenerated={aiInsight.generated} fallbackReason={aiInsight.reason} />
                        )}
                      </div>
                      <div className="space-y-3">
                        {traceData.map((step: any, idx: number) => (
                          <div key={`step-${idx}`} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                            <div className="flex items-start gap-3">
                              <div className="bg-cyan-600/20 text-cyan-400 rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm flex-shrink-0">
                                {idx + 1}
                              </div>
                              <div className="flex-1">
                                <p className="font-semibold text-slate-50">{step.type}</p>
                                <p className="text-slate-400 text-sm">{step.name || JSON.stringify(step.data)}</p>
                                {step.details && (
                                  <p className="text-slate-500 text-xs mt-1">{step.details}</p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Metadata */}
                      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                        <h3 className="font-bold text-slate-50 mb-2">Source Information</h3>
                        <div className="space-y-1 text-sm text-slate-400">
                          <p>Type: <span className="text-slate-50">{selectedItem.itemType}</span></p>
                          <p>ID: <span className="text-slate-50 font-mono text-xs">{selectedItem.id}</span></p>
                          {selectedItem.trace_id && (
                            <p>Trace ID: <span className="text-slate-50 font-mono text-xs">{selectedItem.trace_id}</span></p>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : traceData && traceData.length === 0 ? (
                    <p className="text-slate-500">No trace data found for this item.</p>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-slate-500 mb-4">Loading trace...</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-slate-400 mb-2">Select an item from the left panel to view its complete trace</p>
                  <p className="text-slate-500 text-sm">
                    Traceability shows: Finding → Rule/Module → Dependency → Source Sheet → Source Record
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
