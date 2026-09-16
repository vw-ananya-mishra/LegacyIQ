// src/pages/UnderstandPage.tsx
import React, { useState, useEffect } from 'react';
import { Workbook, Application, CodeModule } from '../types';
import { workbookAPI } from '../utils/api';

export default function UnderstandPage({ workbook }: { workbook: Workbook }) {
  const [activeTab, setActiveTab] = useState<'applications' | 'modules' | 'rules'>('applications');
  const [applications, setApplications] = useState<Application[]>([]);
  const [modules, setModules] = useState<CodeModule[]>([]);
  const [businessRules, setBusinessRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
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

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Understand the Estate</h1>
        <p className="text-slate-400 mb-8">
          Deep-dive analysis of applications, modules, business rules, and complexity hotspots.
        </p>

        {/* Tab Buttons */}
        <div className="flex gap-4 mb-6">
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
            Module Analysis ({modules.length})
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'rules'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Business Logic ({businessRules.length})
          </button>
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
                    <div key={app.application_id || `app-${app.id}`} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                      <h3 className="font-bold text-slate-50 mb-2">{app.application_name}</h3>
                      <p className="text-slate-400 text-sm mb-3">{app.description}</p>
                      <div className="text-xs text-slate-500 space-y-1">
                        <p>Technology: {app.primary_technology}</p>
                        <p>Type: {app.application_type}</p>
                        <p>Status: {app.current_status}</p>
                      </div>
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
              {modules.length === 0 ? (
                <p className="text-slate-500">No modules found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-slate-300">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-2 px-4">Module Name</th>
                        <th className="text-left py-2 px-4">Application</th>
                        <th className="text-left py-2 px-4">Language</th>
                        <th className="text-left py-2 px-4">Lines of Code</th>
                        <th className="text-left py-2 px-4">Complexity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {modules.slice(0, 20).map((mod: any) => (
                        <tr key={mod.module_id || `mod-${mod.id}`} className="border-b border-slate-800 hover:bg-slate-800">
                          <td className="py-2 px-4">{mod.module_name}</td>
                          <td className="py-2 px-4 text-slate-400">{mod.application_name}</td>
                          <td className="py-2 px-4">{mod.language}</td>
                          <td className="py-2 px-4">{mod.lines_of_code}</td>
                          <td className="py-2 px-4">
                            <span className={`px-2 py-1 rounded text-xs ${
                              mod.complexity === 'HIGH' ? 'bg-red-900/30 text-red-300' :
                              mod.complexity === 'MEDIUM' ? 'bg-yellow-900/30 text-yellow-300' :
                              'bg-green-900/30 text-green-300'
                            }`}>
                              {mod.complexity}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {modules.length > 20 && <p className="text-slate-500 mt-2">Showing 20 of {modules.length} modules</p>}
                </div>
              )}
            </div>
          )}

          {!loading && !error && activeTab === 'rules' && (
            <div>
              <h2 className="text-2xl font-bold text-slate-50 mb-4">Business Logic</h2>
              <p className="text-slate-400 mb-4">Critical rules and test coverage</p>
              {businessRules.length === 0 ? (
                <p className="text-slate-500">No business rules found</p>
              ) : (
                <div className="space-y-3">
                  {businessRules.slice(0, 20).map((rule: any) => (
                    <div key={rule.rule_id || `rule-${rule.id}`} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-bold text-slate-50">{rule.rule_name}</h3>
                        <span className="text-xs bg-cyan-900/30 text-cyan-300 px-2 py-1 rounded">
                          {rule.rule_type}
                        </span>
                      </div>
                      <p className="text-slate-400 text-sm mb-2">{rule.description}</p>
                      <div className="text-xs text-slate-500">
                        Test Coverage: {rule.test_coverage ? '✓ Yes' : '✗ No'} | Complexity: {rule.complexity}
                      </div>
                    </div>
                  ))}
                  {businessRules.length > 20 && <p className="text-slate-500 mt-2">Showing 20 of {businessRules.length} rules</p>}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
