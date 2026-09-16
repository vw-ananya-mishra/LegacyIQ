// src/pages/TraceabilityPage.tsx
import React, { useState, useEffect } from 'react';
import { Workbook } from '../types';
import { workbookAPI, traceabilityAPI } from '../utils/api';

export default function TraceabilityPage({ workbook }: { workbook: Workbook }) {
  const [activeTab, setActiveTab] = useState<'applications' | 'modules' | 'rules' | 'dependencies'>('applications');
  const [applications, setApplications] = useState<any[]>([]);
  const [modules, setModules] = useState<any[]>([]);
  const [businessRules, setBusinessRules] = useState<any[]>([]);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [traceData, setTraceData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tracing, setTracing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [apps, mods, rules] = await Promise.all([
          workbookAPI.getApplications(workbook.workbook_id),
          workbookAPI.getModules(workbook.workbook_id),
          workbookAPI.getBusinessRules(workbook.workbook_id),
        ]);
        setApplications(apps);
        setModules(mods);
        setBusinessRules(rules);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [workbook.workbook_id]);

  const handleTraceItem = async (item: any, itemType: string) => {
    try {
      setTracing(true);
      setError(null);
      const trace = await traceabilityAPI.traceFinding(workbook.workbook_id, item.id, itemType);
      setTraceData(trace);
      setSelectedItem({ ...item, itemType });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trace item');
    } finally {
      setTracing(false);
    }
  };

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
                <div className="space-y-2">
                  {applications.map((app: any) => (
                    <button
                      key={app.application_id || `app-${app.id}`}
                      onClick={() => handleTraceItem(app, 'application')}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        selectedItem?.application_id === app.application_id
                          ? 'bg-cyan-900/30 border-cyan-600'
                          : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <p className="font-semibold text-slate-50 text-sm">{app.application_name}</p>
                      <p className="text-slate-400 text-xs">{app.primary_technology}</p>
                    </button>
                  ))}
                </div>
              ) : activeTab === 'modules' ? (
                <div className="space-y-2">
                  {modules.slice(0, 20).map((mod: any) => (
                    <button
                      key={mod.module_id || `mod-${mod.id}`}
                      onClick={() => handleTraceItem(mod, 'module')}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        selectedItem?.module_id === mod.module_id
                          ? 'bg-cyan-900/30 border-cyan-600'
                          : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <p className="font-semibold text-slate-50 text-sm">{mod.module_name}</p>
                      <p className="text-slate-400 text-xs">{mod.language}</p>
                    </button>
                  ))}
                </div>
              ) : activeTab === 'rules' ? (
                <div className="space-y-2">
                  {businessRules.slice(0, 20).map((rule: any) => (
                    <button
                      key={rule.rule_id || `rule-${rule.id}`}
                      onClick={() => handleTraceItem(rule, 'rule')}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        selectedItem?.rule_id === rule.rule_id
                          ? 'bg-cyan-900/30 border-cyan-600'
                          : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <p className="font-semibold text-slate-50 text-sm">{rule.rule_name}</p>
                      <p className="text-slate-400 text-xs">{rule.rule_type}</p>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500">Dependencies view</p>
              )}
            </div>
          </div>

          {/* Right Panel - Trace Information */}
          <div className="lg:col-span-2">
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
              {selectedItem ? (
                <div>
                  <h2 className="text-xl font-bold text-slate-50 mb-4 flex items-center justify-between">
                    <span>{selectedItem.application_name || selectedItem.module_name || selectedItem.rule_name}</span>
                    {tracing && <span className="text-sm text-slate-400">Tracing...</span>}
                  </h2>

                  {/* Trace Chain */}
                  {traceData ? (
                    <div className="space-y-4">
                      {/* Trace Steps */}
                      <div className="space-y-3">
                        {traceData?.trace_chain ? (
                          traceData.trace_chain.map((step: any, idx: number) => (
                            <div key={`step-${idx}`} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                              <div className="flex items-start gap-3">
                                <div className="bg-cyan-600/20 text-cyan-400 rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm flex-shrink-0">
                                  {idx + 1}
                                </div>
                                <div className="flex-1">
                                  <p className="font-semibold text-slate-50">{step.type}</p>
                                  <p className="text-slate-400 text-sm">{step.name}</p>
                                  {step.details && (
                                    <p className="text-slate-500 text-xs mt-1">{step.details}</p>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                            <p className="text-slate-400">Trace data available</p>
                            <pre className="text-slate-300 text-xs mt-2 whitespace-pre-wrap">
                              {JSON.stringify(traceData, null, 2)}
                            </pre>
                          </div>
                        )}
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
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-slate-500 mb-4">Click "Trace Item" to view complete audit trail</p>
                      <button
                        onClick={() => handleTraceItem(selectedItem, selectedItem.itemType)}
                        disabled={tracing}
                        className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold"
                      >
                        {tracing ? 'Tracing...' : 'Trace Item'}
                      </button>
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
