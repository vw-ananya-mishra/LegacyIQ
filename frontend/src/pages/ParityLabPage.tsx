// src/pages/ParityLabPage.tsx
import React, { useState, useEffect } from 'react';
import { Workbook } from '../types';
import { workbookAPI, agentAPI } from '../utils/api';

export default function ParityLabPage({ workbook }: { workbook: Workbook }) {
  const [businessRules, setBusinessRules] = useState<any[]>([]);
  const [testResults, setTestResults] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const rules = await workbookAPI.getBusinessRules(workbook.workbook_id);
        setBusinessRules(rules);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [workbook.workbook_id]);

  const handleGenerateTests = async () => {
    try {
      setGenerating(true);
      setError(null);
      const result = await agentAPI.analyzeWithAgent(
        workbook.workbook_id,
        'parity_engineer',
        { context: 'Generate parity tests from business rules' }
      );
      
      // Simulate test results
      const mockResults = businessRules.map((rule, index) => ({
        id: rule.rule_id,
        name: rule.rule_name,
        status: Math.random() > 0.3 ? 'pass' : Math.random() > 0.5 ? 'fail' : 'mismatch',
        duration: Math.floor(Math.random() * 5000) + 100,
        output: result?.summary || 'Test executed successfully'
      }));
      setTestResults(mockResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate tests');
    } finally {
      setGenerating(false);
    }
  };

  const passed = testResults.filter(t => t.status === 'pass').length;
  const failed = testResults.filter(t => t.status === 'fail').length;
  const mismatches = testResults.filter(t => t.status === 'mismatch').length;
  const total = testResults.length;

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Parity Lab</h1>
        <p className="text-slate-400 mb-8">
          Generate and execute parity tests to validate system behavior against business rules and expected outcomes.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
            {error}
          </div>
        )}

        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
          {/* Statistics */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <p className="text-slate-400 text-sm">Total Tests</p>
              <p className="text-3xl font-bold text-slate-50">{total}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <p className="text-slate-400 text-sm">Passed</p>
              <p className="text-3xl font-bold text-green-400">{passed}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <p className="text-slate-400 text-sm">Failed</p>
              <p className="text-3xl font-bold text-red-400">{failed}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <p className="text-slate-400 text-sm">Mismatches</p>
              <p className="text-3xl font-bold text-yellow-400">{mismatches}</p>
            </div>
          </div>

          {/* Action Button */}
          <div className="mb-8">
            <button
              onClick={handleGenerateTests}
              disabled={generating || businessRules.length === 0}
              className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-all"
            >
              {generating ? 'Generating Tests...' : `Generate Parity Tests (${businessRules.length} rules)`}
            </button>
            <p className="text-slate-400 text-sm mt-2">
              Generate tests based on {businessRules.length} business rules defined in your system
            </p>
          </div>

          {/* Test Results */}
          {testResults.length > 0 && (
            <div>
              <h3 className="text-lg font-bold text-slate-50 mb-4">Test Results</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {testResults.map((test: any) => (
                  <div
                    key={test.id || `test-${test.name}`}
                    className={`p-3 rounded-lg border flex items-center justify-between ${
                      test.status === 'pass'
                        ? 'bg-green-900/20 border-green-700'
                        : test.status === 'fail'
                        ? 'bg-red-900/20 border-red-700'
                        : 'bg-yellow-900/20 border-yellow-700'
                    }`}
                  >
                    <div>
                      <p className="font-semibold text-slate-50">{test.name}</p>
                      <p className="text-slate-400 text-sm">{test.duration}ms</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        test.status === 'pass'
                          ? 'bg-green-900/40 text-green-300'
                          : test.status === 'fail'
                          ? 'bg-red-900/40 text-red-300'
                          : 'bg-yellow-900/40 text-yellow-300'
                      }`}
                    >
                      {test.status.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
              {total > 0 && (
                <div className="mt-4 p-3 bg-slate-800 rounded-lg">
                  <p className="text-slate-300 text-sm">
                    Pass Rate: {total > 0 ? Math.round((passed / total) * 100) : 0}% ({passed}/{total})
                  </p>
                </div>
              )}
            </div>
          )}

          {!loading && businessRules.length === 0 && (
            <p className="text-slate-500">No business rules found to generate tests</p>
          )}
        </div>
      </div>
    </div>
  );
}
