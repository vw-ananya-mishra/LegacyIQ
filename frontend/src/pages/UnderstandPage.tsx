// src/pages/UnderstandPage.tsx
import React, { useState, useEffect, useMemo } from 'react';
import { Workbook, Application, CodeModule } from '../types';
import { workbookAPI, agentAPI, cobolAPI } from '../utils/api';
import AIInsightPanel from '../components/common/AIInsightPanel';

export default function UnderstandPage({ workbook }: { workbook: Workbook }) {
  const [activeTab, setActiveTab] = useState<'applications' | 'modules' | 'rules' | 'cobol'>('applications');
  const [applications, setApplications] = useState<Application[]>([]);
  const [modules, setModules] = useState<CodeModule[]>([]);
  const [businessRules, setBusinessRules] = useState<any[]>([]);
  const [selectedAppId, setSelectedAppId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aiInsight, setAiInsight] = useState<{ narrative: string | null; generated?: boolean; reason?: string | null } | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiAppId, setAiAppId] = useState<string>('');
  const [cobolFile, setCobolFile] = useState<File | null>(null);
  const [cobolResult, setCobolResult] = useState<any>(null);
  const [cobolLoading, setCobolLoading] = useState(false);
  const [cobolError, setCobolError] = useState<string | null>(null);

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

  // Map module_id -> application_id so Business Rules (linked only to a module)
  // can still be filtered by application
  const moduleAppMap = useMemo(() => {
    const map: Record<string, string> = {};
    modules.forEach((m: any) => { map[m.id] = m.application_id; });
    return map;
  }, [modules]);

  const filteredModules = useMemo(() => {
    if (!selectedAppId) return modules;
    return modules.filter((m: any) => m.application_id === selectedAppId);
  }, [modules, selectedAppId]);

  const filteredRules = useMemo(() => {
    if (!selectedAppId) return businessRules;
    return businessRules.filter((r: any) => moduleAppMap[r.module_id] === selectedAppId);
  }, [businessRules, selectedAppId, moduleAppMap]);

  const handleAnalyzeCobol = async () => {
    if (!cobolFile) return;
    try {
      setCobolLoading(true);
      setCobolError(null);
      const result = await cobolAPI.analyze(cobolFile);
      setCobolResult(result);
    } catch (err) {
      setCobolError(err instanceof Error ? err.message : 'Failed to analyze COBOL file');
    } finally {
      setCobolLoading(false);
    }
  };

  const handleGenerateAiInsight = async (appId: string) => {
    try {
      setAiLoading(true);
      setAiAppId(appId);
      const result = await agentAPI.analyzeWithAgent(workbook.workbook_id, 'legacy_archaeologist', { application_id: appId });
      const f = result?.findings || {};
      setAiInsight({ narrative: f.ai_narrative || null, generated: f.ai_generated, reason: f.ai_fallback_reason });
    } catch (err) {
      setAiInsight({ narrative: null, generated: false, reason: err instanceof Error ? err.message : 'Failed to generate AI insight' });
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Understand the Estate</h1>
        <p className="text-slate-400 mb-8">
          Deep-dive analysis of applications, modules, business rules, and complexity hotspots.
        </p>

        {/* Tab Buttons */}
        <div className="flex gap-4 mb-6 items-center flex-wrap">
          <button
            onClick={() => setActiveTab('applications')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'applications'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Application Explorer ({applications.length})
          </button>
          <button
            onClick={() => setActiveTab('modules')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'modules'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Module Analysis ({filteredModules.length})
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'rules'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Business Logic ({filteredRules.length})
          </button>
          <button
            onClick={() => setActiveTab('cobol')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'cobol'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            COBOL Source Analysis
          </button>

          {activeTab !== 'applications' && activeTab !== 'cobol' && (
            <select
              value={selectedAppId}
              onChange={(e) => setSelectedAppId(e.target.value)}
              className="ml-auto bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-50 text-sm focus:outline-none focus:border-cyan-600"
            >
              <option value="">All Applications</option>
              {applications.map((app: any) => (
                <option key={app.id} value={app.id}>{app.name}</option>
              ))}
            </select>
          )}
        </div>

        {/* Content Area */}
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
          {loading && <p className="text-slate-400">Loading data...</p>}
          {error && <p className="text-red-400">Error: {error}</p>}

          {!loading && !error && activeTab === 'applications' && (
            <div>
              <h2 className="text-2xl font-bold text-slate-50 mb-4">Application Explorer</h2>
              <p className="text-slate-400 mb-4">View all applications with metadata</p>
              {applications.length === 0 ? (
                <p className="text-slate-500">No applications found</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {applications.map((app: any) => (
                    <div key={app.id} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                      <h3 className="font-bold text-slate-50 mb-2">{app.name}</h3>
                      <p className="text-slate-400 text-sm mb-3">{app.business_domain || 'No domain'} · Owner: {app.owner || 'Unknown'}</p>
                      <div className="text-xs text-slate-500 space-y-1">
                        <p>Language: {app.primary_language || 'N/A'}</p>
                        <p>Platform: {app.platform || 'N/A'}</p>
                        <p>Criticality: {app.criticality || 'N/A'}</p>
                        <p>Doc Coverage: {app.doc_coverage_pct != null ? `${app.doc_coverage_pct}%` : 'N/A'}</p>
                        <p>Annual Maint. Cost: {app.annual_maint_cost_eur != null ? `€${Number(app.annual_maint_cost_eur).toLocaleString()}` : 'N/A'}</p>
                      </div>
                      <button
                        onClick={() => handleGenerateAiInsight(app.id)}
                        disabled={aiLoading && aiAppId === app.id}
                        className="mt-3 w-full px-3 py-1.5 rounded text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 text-white transition-all"
                      >
                        {aiLoading && aiAppId === app.id ? 'Analyzing...' : '✨ AI Insight'}
                      </button>
                      {aiAppId === app.id && aiInsight && (
                        <div className="mt-3">
                          <AIInsightPanel narrative={aiInsight.narrative} aiGenerated={aiInsight.generated} fallbackReason={aiInsight.reason} />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {!loading && !error && activeTab === 'modules' && (
            <div>
              <h2 className="text-2xl font-bold text-slate-50 mb-4">Module Analysis</h2>
              <p className="text-slate-400 mb-4">Complexity hotspots and coverage gaps</p>
              {filteredModules.length === 0 ? (
                <p className="text-slate-500">No modules found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-slate-300">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-2 px-4">Module Name</th>
                        <th className="text-left py-2 px-4">Type</th>
                        <th className="text-left py-2 px-4">Lines of Code</th>
                        <th className="text-left py-2 px-4">Complexity</th>
                        <th className="text-left py-2 px-4">Unit Tests</th>
                        <th className="text-left py-2 px-4">Dead Code</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredModules.slice(0, 20).map((mod: any) => (
                        <tr key={mod.id} className="border-b border-slate-800 hover:bg-slate-800">
                          <td className="py-2 px-4">{mod.name || 'Unknown'}</td>
                          <td className="py-2 px-4">{mod.module_type || 'N/A'}</td>
                          <td className="py-2 px-4">{mod.lines_of_code || 0}</td>
                          <td className="py-2 px-4">
                            <span className={`px-2 py-1 rounded text-xs ${
                              (mod.complexity_score || 0) >= 38 ? 'bg-red-900/30 text-red-300' :
                              (mod.complexity_score || 0) >= 20 ? 'bg-yellow-900/30 text-yellow-300' :
                              'bg-green-900/30 text-green-300'
                            }`}>
                              {mod.complexity_score || 0}
                            </span>
                          </td>
                          <td className="py-2 px-4">{mod.has_unit_tests === 'Y' ? 'Yes' : 'No'}</td>
                          <td className="py-2 px-4">{mod.is_dead_code === 'Y' ? 'Yes' : 'No'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {filteredModules.length > 20 && <p className="text-slate-500 mt-2">Showing 20 of {filteredModules.length} modules</p>}
                </div>
              )}
            </div>
          )}

          {!loading && !error && activeTab === 'rules' && (
            <div>
              <h2 className="text-2xl font-bold text-slate-50 mb-4">Business Logic</h2>
              <p className="text-slate-400 mb-4">Critical rules and test coverage</p>
              {filteredRules.length === 0 ? (
                <p className="text-slate-500">No business rules found</p>
              ) : (
                <div className="space-y-3">
                  {filteredRules.slice(0, 20).map((rule: any) => (
                    <div key={rule.id} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-bold text-slate-50">{rule.rule_name}</h3>
                          <p className="text-slate-400 text-xs mt-1">ID: {rule.id} · Module: {rule.module_id}</p>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${
                          rule.criticality === 'High' ? 'bg-red-900/30 text-red-300' :
                          rule.criticality === 'Medium' ? 'bg-yellow-900/30 text-yellow-300' :
                          'bg-cyan-900/30 text-cyan-300'
                        }`}>
                          {rule.criticality || 'Unknown'}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 space-y-1">
                        <p>Domain: {rule.business_domain || 'N/A'}</p>
                        <p>Has Test Case: {rule.has_test_case === 'Y' ? 'Yes' : 'No'} | Extraction Confidence: {rule.extraction_confidence != null ? `${Math.round(rule.extraction_confidence * 100)}%` : 'N/A'}</p>
                        {rule.duplicate_of && <p>Duplicate of: {rule.duplicate_of}</p>}
                      </div>
                    </div>
                  ))}
                  {filteredRules.length > 20 && <p className="text-slate-500 mt-2">Showing 20 of {filteredRules.length} rules</p>}
                </div>
              )}
            </div>
          )}

          {!loading && !error && activeTab === 'cobol' && (
            <div>
              <h2 className="text-2xl font-bold text-slate-50 mb-4">COBOL Source Analysis</h2>
              <p className="text-slate-400 mb-4">
                Upload a single .cbl COBOL source file for structural analysis (divisions, data items,
                paragraphs, CALLs, copybooks, file I/O, embedded SQL, complexity) — a demo companion to
                the spreadsheet-based ingestion, working directly from real legacy source code.
              </p>

              <div className="flex items-center gap-3 mb-6">
                <input
                  type="file"
                  accept=".cbl"
                  onChange={(e) => setCobolFile(e.target.files?.[0] || null)}
                  className="text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-slate-700 file:text-slate-100 file:font-semibold hover:file:bg-slate-600"
                />
                <button
                  onClick={handleAnalyzeCobol}
                  disabled={!cobolFile || cobolLoading}
                  className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all whitespace-nowrap"
                >
                  {cobolLoading ? 'Analyzing...' : 'Analyze .cbl File'}
                </button>
              </div>

              {cobolError && <p className="text-red-400 text-sm mb-4">{cobolError}</p>}

              {cobolResult && (
                <div>
                  <AIInsightPanel
                    narrative={cobolResult?.findings?.ai_narrative}
                    aiGenerated={cobolResult?.findings?.ai_generated}
                    fallbackReason={cobolResult?.findings?.ai_fallback_reason}
                  />

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <p className="text-slate-400 text-xs">Program ID</p>
                      <p className="font-bold text-slate-50">{cobolResult.findings.program_id || 'Unknown'}</p>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <p className="text-slate-400 text-xs">Lines of Code</p>
                      <p className="font-bold text-slate-50">{cobolResult.findings.total_lines}</p>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <p className="text-slate-400 text-xs">Data Items</p>
                      <p className="font-bold text-slate-50">{cobolResult.findings.data_item_count}</p>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <p className="text-slate-400 text-xs">Complexity Estimate</p>
                      <p className={`font-bold ${cobolResult.findings.complexity_estimate >= 15 ? 'text-red-400' : cobolResult.findings.complexity_estimate >= 8 ? 'text-yellow-400' : 'text-green-400'}`}>
                        {cobolResult.findings.complexity_estimate}
                      </p>
                    </div>
                  </div>

                  {cobolResult.findings.summary && (
                    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-4">
                      <p className="text-xs text-slate-500 uppercase tracking-wide font-semibold mb-1">Business Purpose (AI)</p>
                      <p className="text-slate-300 text-sm">{cobolResult.findings.summary}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                      <h4 className="font-semibold text-slate-200 text-sm mb-2">Structure</h4>
                      <p className="text-slate-400 text-xs">Divisions: {cobolResult.findings.divisions_found?.join(', ') || 'None found'}</p>
                      <p className="text-slate-400 text-xs">Paragraphs ({cobolResult.findings.paragraph_count}): {cobolResult.findings.paragraphs?.join(', ') || 'None found'}</p>
                      <p className="text-slate-400 text-xs">Control flow: {cobolResult.findings.control_flow?.if_count} IF · {cobolResult.findings.control_flow?.evaluate_count} EVALUATE · {cobolResult.findings.control_flow?.perform_count} PERFORM · {cobolResult.findings.control_flow?.goto_count} GOTO</p>
                    </div>
                    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                      <h4 className="font-semibold text-slate-200 text-sm mb-2">Dependencies &amp; I/O</h4>
                      <p className="text-slate-400 text-xs">External CALLs: {cobolResult.findings.external_calls?.join(', ') || 'None'}</p>
                      <p className="text-slate-400 text-xs">Copybooks: {cobolResult.findings.copybooks?.join(', ') || 'None'}</p>
                      <p className="text-slate-400 text-xs">Files: {cobolResult.findings.file_io?.map((f: any) => `${f.file_name} → ${f.assigned_to}`).join(', ') || 'None'}</p>
                      <p className="text-slate-400 text-xs">Embedded SQL blocks: {cobolResult.findings.embedded_sql_blocks}</p>
                    </div>
                  </div>

                  {cobolResult.findings.modernization_notes?.length > 0 && (
                    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-4">
                      <h4 className="font-semibold text-cyan-300 text-sm mb-2">Modernization Notes (AI)</h4>
                      <ul className="list-disc list-inside text-slate-300 text-xs space-y-1">
                        {cobolResult.findings.modernization_notes.map((n: string, idx: number) => <li key={idx}>{n}</li>)}
                      </ul>
                    </div>
                  )}

                  {cobolResult.findings.risk_notes?.length > 0 && (
                    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                      <h4 className="font-semibold text-amber-300 text-sm mb-2">Risk Notes (AI)</h4>
                      <ul className="list-disc list-inside text-slate-300 text-xs space-y-1">
                        {cobolResult.findings.risk_notes.map((n: string, idx: number) => <li key={idx}>{n}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
