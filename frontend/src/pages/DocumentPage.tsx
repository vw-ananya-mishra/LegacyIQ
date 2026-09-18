// src/pages/DocumentPage.tsx
import React, { useState, useEffect } from 'react';
import { Workbook } from '../types';
import { agentAPI, workbookAPI, knowledgeAPI } from '../utils/api';
import AIInsightPanel from '../components/common/AIInsightPanel';

function downloadDocument(result: any, docType: string, appName: string) {
  const sections = result?.findings?.sections;
  if (!Array.isArray(sections)) return;
  const generatedBy = result?.findings?.ai_generated
    ? 'Agentic AI (VW LLMaaS / GPT-4o), grounded in real workbook data'
    : 'Deterministic fallback template (AI unavailable at generation time)';
  const lines = [
    `# ${docType} — ${appName}`,
    '',
    `_Generated: ${new Date().toLocaleString()}_`,
    `_Source: ${generatedBy}_`,
    '',
    '---',
    '',
    ...sections.flatMap((s: any) => [
      `## ${s.title}${s.requires_review ? ' [NEEDS REVIEW]' : ''}`,
      '',
      s.content || '',
      '',
    ]),
  ];
  const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${appName.replace(/\s+/g, '_')}_${docType.replace(/\s+/g, '_')}.md`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function SpecSections({ result }: { result: any }) {
  const sections = result?.findings?.sections;
  if (!Array.isArray(sections) || sections.length === 0) {
    return (
      <pre className="text-slate-300 text-xs whitespace-pre-wrap">
        {JSON.stringify(result, null, 2)}
      </pre>
    );
  }
  return (
    <div className="space-y-4">
      {sections.map((section: any, idx: number) => (
        <div key={idx}>
          <h5 className="text-slate-200 font-semibold text-sm mb-1">
            {section.title}
            {section.requires_review && (
              <span className="ml-2 text-xs font-normal text-yellow-400">needs review</span>
            )}
          </h5>
          <p className="text-slate-400 text-xs whitespace-pre-wrap">{section.content}</p>
        </div>
      ))}
    </div>
  );
}

export default function DocumentPage({ workbook }: { workbook: Workbook }) {
  const [applications, setApplications] = useState<any[]>([]);
  const [selectedAppId, setSelectedAppId] = useState<string>('');
  const [functionalSpecLoading, setFunctionalSpecLoading] = useState(false);
  const [apiSpecLoading, setApiSpecLoading] = useState(false);
  const [functionalSpecResult, setFunctionalSpecResult] = useState<any>(null);
  const [apiSpecResult, setApiSpecResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [kbQuery, setKbQuery] = useState('');
  const [kbLoading, setKbLoading] = useState(false);
  const [kbResult, setKbResult] = useState<any>(null);
  const [kbError, setKbError] = useState<string | null>(null);

  useEffect(() => {
    const loadApplications = async () => {
      try {
        const apps = await workbookAPI.getApplications(workbook.workbook_id);
        setApplications(apps);
        if (apps.length > 0) setSelectedAppId(apps[0].id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load applications');
      }
    };
    loadApplications();
  }, [workbook.workbook_id]);

  const handleGenerateFunctionalSpec = async () => {
    try {
      setFunctionalSpecLoading(true);
      setError(null);
      const result = await agentAPI.analyzeWithAgent(
        workbook.workbook_id,
        'documentation_architect',
        { doc_type: 'functional_specification', application_id: selectedAppId }
      );
      setFunctionalSpecResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate specification');
    } finally {
      setFunctionalSpecLoading(false);
    }
  };

  const handleGenerateApiSpec = async () => {
    try {
      setApiSpecLoading(true);
      setError(null);
      const result = await agentAPI.analyzeWithAgent(
        workbook.workbook_id,
        'documentation_architect',
        { doc_type: 'api_specification', application_id: selectedAppId }
      );
      setApiSpecResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate specification');
    } finally {
      setApiSpecLoading(false);
    }
  };

  const handleKnowledgeSearch = async () => {
    if (!kbQuery.trim()) return;
    try {
      setKbLoading(true);
      setKbError(null);
      const result = await knowledgeAPI.search(workbook.workbook_id, kbQuery.trim());
      setKbResult(result);
    } catch (err) {
      setKbError(err instanceof Error ? err.message : 'Knowledge search failed');
    } finally {
      setKbLoading(false);
    }
  };

  const selectedAppName = applications.find((a: any) => a.id === selectedAppId)?.name || selectedAppId || 'Application';

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Documentation Architect</h1>
        <p className="text-slate-400 mb-8">
          Auto-generate functional and API specifications from application metadata and integration analysis.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {/* Application Selector */}
        <div className="mb-6 bg-slate-900 border border-slate-700 rounded-lg p-6">
          <label className="block text-slate-400 text-sm mb-2">Application</label>
          <select
            value={selectedAppId}
            onChange={(e) => {
              setSelectedAppId(e.target.value);
              setFunctionalSpecResult(null);
              setApiSpecResult(null);
            }}
            className="w-full md:w-96 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-50 focus:outline-none focus:border-cyan-600"
          >
            {applications.length === 0 && <option value="">No applications found</option>}
            {applications.map((app: any) => (
              <option key={app.id} value={app.id}>
                {app.name} ({app.id})
              </option>
            ))}
          </select>
          <p className="text-slate-500 text-xs mt-2">
            Choose which application to generate the functional and API specifications for.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Functional Specification */}
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
            <h3 className="text-xl font-bold text-slate-50 mb-2">Functional Specification</h3>
            <p className="text-slate-400 mb-6">Auto-generated from application metadata</p>
            
            <button
              onClick={handleGenerateFunctionalSpec}
              disabled={functionalSpecLoading || !selectedAppId}
              className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all"
            >
              {functionalSpecLoading ? 'Generating...' : 'Generate'}
            </button>

            {functionalSpecResult && (
              <div className="mt-6 bg-slate-800 p-4 rounded-lg max-h-96 overflow-y-auto">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-bold text-slate-50">Generated Specification:</h4>
                  <button
                    onClick={() => downloadDocument(functionalSpecResult, 'Functional_Specification', selectedAppName)}
                    className="text-xs px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-100 font-semibold"
                  >
                    ⬇️ Download (.md)
                  </button>
                </div>
                <AIInsightPanel
                  narrative={functionalSpecResult?.findings?.ai_narrative}
                  aiGenerated={functionalSpecResult?.findings?.ai_generated}
                  fallbackReason={functionalSpecResult?.findings?.ai_fallback_reason}
                />
                <SpecSections result={functionalSpecResult} />
              </div>
            )}
          </div>

          {/* API Specification */}
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
            <h3 className="text-xl font-bold text-slate-50 mb-2">API Specification</h3>
            <p className="text-slate-400 mb-6">Extract from integrations and data flows</p>
            
            <button
              onClick={handleGenerateApiSpec}
              disabled={apiSpecLoading || !selectedAppId}
              className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all"
            >
              {apiSpecLoading ? 'Generating...' : 'Generate'}
            </button>

            {apiSpecResult && (
              <div className="mt-6 bg-slate-800 p-4 rounded-lg max-h-96 overflow-y-auto">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-bold text-slate-50">Generated Specification:</h4>
                  <button
                    onClick={() => downloadDocument(apiSpecResult, 'API_Specification', selectedAppName)}
                    className="text-xs px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-100 font-semibold"
                  >
                    ⬇️ Download (.md)
                  </button>
                </div>
                <AIInsightPanel
                  narrative={apiSpecResult?.findings?.ai_narrative}
                  aiGenerated={apiSpecResult?.findings?.ai_generated}
                  fallbackReason={apiSpecResult?.findings?.ai_fallback_reason}
                />
                <SpecSections result={apiSpecResult} />
              </div>
            )}
          </div>
        </div>

        {/* Knowledge Hub - vector-embedding RAG search */}
        <div className="mt-8 bg-slate-900 border border-slate-700 rounded-lg p-8">
          <h3 className="text-xl font-bold text-slate-50 mb-2">🔎 Knowledge Hub Search (Vector RAG)</h3>
          <p className="text-slate-400 mb-4">
            Semantically searches embedded Documentation Artifacts, Business Rules, and Modernization
            Backlog text — retrieves the most similar chunks by vector similarity, then asks the AI to
            answer grounded strictly in what was retrieved.
          </p>
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              value={kbQuery}
              onChange={(e) => setKbQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleKnowledgeSearch()}
              placeholder="e.g. what is documented about claims processing?"
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-50 focus:outline-none focus:border-cyan-600"
            />
            <button
              onClick={handleKnowledgeSearch}
              disabled={kbLoading || !kbQuery.trim()}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all whitespace-nowrap"
            >
              {kbLoading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {kbError && <p className="text-red-400 text-sm mb-4">{kbError}</p>}

          {kbResult && (
            <div>
              <AIInsightPanel
                narrative={kbResult?.findings?.answer}
                aiGenerated={kbResult?.findings?.ai_generated}
                fallbackReason={kbResult?.findings?.ai_fallback_reason}
              />
              {kbResult?.findings?.retrieved?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 mb-2">Retrieved chunks (by vector similarity)</h4>
                  <div className="space-y-2">
                    {kbResult.findings.retrieved.map((chunk: any) => (
                      <div key={chunk.id} className="bg-slate-800 p-3 rounded-lg border border-slate-700 text-sm">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-semibold text-cyan-400">{chunk.source_type} · {chunk.id}</span>
                          <span className="text-xs text-slate-500">similarity: {chunk.score}</span>
                        </div>
                        <p className="text-slate-400 text-xs">{chunk.text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="mt-8 bg-slate-900 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-bold text-slate-50 mb-4">Documentation Agent Features</h3>
          <ul className="space-y-2 text-slate-400">
            <li>✓ Automated extraction of functional requirements from business rules</li>
            <li>✓ API contract generation from integration definitions</li>
            <li>✓ Cross-reference mapping between applications and modules</li>
            <li>✓ Coverage analysis for undocumented components</li>
            <li>✓ Export-ready specification formats (Markdown download)</li>
            <li>✓ Vector-embedding semantic search across documentation, rules, and backlog</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
