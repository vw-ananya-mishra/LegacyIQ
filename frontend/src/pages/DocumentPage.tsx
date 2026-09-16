// src/pages/DocumentPage.tsx
import React, { useState } from 'react';
import { Workbook } from '../types';
import { agentAPI } from '../utils/api';

export default function DocumentPage({ workbook }: { workbook: Workbook }) {
  const [functionalSpecLoading, setFunctionalSpecLoading] = useState(false);
  const [apiSpecLoading, setApiSpecLoading] = useState(false);
  const [functionalSpecResult, setFunctionalSpecResult] = useState<any>(null);
  const [apiSpecResult, setApiSpecResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateFunctionalSpec = async () => {
    try {
      setFunctionalSpecLoading(true);
      setError(null);
      const result = await agentAPI.analyzeWithAgent(
        workbook.workbook_id,
        'documentation_architect',
        { doc_type: 'functional_specification' }
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
        { doc_type: 'api_specification' }
      );
      setApiSpecResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate specification');
    } finally {
      setApiSpecLoading(false);
    }
  };

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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Functional Specification */}
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
            <h3 className="text-xl font-bold text-slate-50 mb-2">Functional Specification</h3>
            <p className="text-slate-400 mb-6">Auto-generated from application metadata</p>
            
            <button
              onClick={handleGenerateFunctionalSpec}
              disabled={functionalSpecLoading}
              className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all"
            >
              {functionalSpecLoading ? 'Generating...' : 'Generate'}
            </button>

            {functionalSpecResult && (
              <div className="mt-6 bg-slate-800 p-4 rounded-lg max-h-64 overflow-y-auto">
                <h4 className="font-bold text-slate-50 mb-3">Generated Specification:</h4>
                <pre className="text-slate-300 text-xs whitespace-pre-wrap">
                  {typeof functionalSpecResult === 'string'
                    ? functionalSpecResult
                    : JSON.stringify(functionalSpecResult, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {/* API Specification */}
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
            <h3 className="text-xl font-bold text-slate-50 mb-2">API Specification</h3>
            <p className="text-slate-400 mb-6">Extract from integrations and data flows</p>
            
            <button
              onClick={handleGenerateApiSpec}
              disabled={apiSpecLoading}
              className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all"
            >
              {apiSpecLoading ? 'Generating...' : 'Generate'}
            </button>

            {apiSpecResult && (
              <div className="mt-6 bg-slate-800 p-4 rounded-lg max-h-64 overflow-y-auto">
                <h4 className="font-bold text-slate-50 mb-3">Generated Specification:</h4>
                <pre className="text-slate-300 text-xs whitespace-pre-wrap">
                  {typeof apiSpecResult === 'string'
                    ? apiSpecResult
                    : JSON.stringify(apiSpecResult, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-8 bg-slate-900 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-bold text-slate-50 mb-4">Documentation Agent Features</h3>
          <ul className="space-y-2 text-slate-400">
            <li>✓ Automated extraction of functional requirements from business rules</li>
            <li>✓ API contract generation from integration definitions</li>
            <li>✓ Cross-reference mapping between applications and modules</li>
            <li>✓ Coverage analysis for undocumented components</li>
            <li>✓ Export-ready specification formats</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
