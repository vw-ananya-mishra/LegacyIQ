// Stub pages for LegacyIQ

// src/pages/UnderstandPage.tsx
import React from 'react';
import { Workbook } from '../types';

export default function UnderstandPage({ workbook }: { workbook: Workbook }) {
  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Understand the Estate</h1>
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
          <p className="text-slate-400">
            Deep-dive analysis of applications, modules, business rules, and complexity hotspots.
          </p>
          <div className="mt-6 space-y-4">
            <div className="bg-slate-800 p-4 rounded-lg">
              <h3 className="font-bold text-slate-50">Application Explorer</h3>
              <p className="text-slate-400 text-sm">View all applications with metadata</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <h3 className="font-bold text-slate-50">Module Analysis</h3>
              <p className="text-slate-400 text-sm">Complexity hotspots and coverage gaps</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <h3 className="font-bold text-slate-50">Business Logic</h3>
              <p className="text-slate-400 text-sm">Critical rules and test coverage</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

---

// src/pages/DocumentPage.tsx
import React from 'react';
import { Workbook } from '../types';

export default function DocumentPage({ workbook }: { workbook: Workbook }) {
  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Documentation Architect</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
            <h3 className="text-xl font-bold text-slate-50 mb-4">Functional Specification</h3>
            <p className="text-slate-400 mb-4">Auto-generated from application metadata</p>
            <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg">
              Generate
            </button>
          </div>
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
            <h3 className="text-xl font-bold text-slate-50 mb-4">API Specification</h3>
            <p className="text-slate-400 mb-4">Extract from integrations and data flows</p>
            <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg">
              Generate
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

---

// src/pages/DependencyMapPage.tsx
import React from 'react';
import { Workbook } from '../types';

export default function DependencyMapPage({ workbook }: { workbook: Workbook }) {
  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Dependency Graph</h1>
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
          <p className="text-slate-400 mb-6">
            Interactive visualization of dependencies across applications, modules, data stores, integrations, and APIs.
          </p>
          <div className="bg-slate-800 rounded-lg h-96 flex items-center justify-center">
            <p className="text-slate-500">Graph visualization loading...</p>
          </div>
          <div className="mt-6 flex gap-2">
            <button className="px-3 py-1 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700">All</button>
            <button className="px-3 py-1 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700">Modules</button>
            <button className="px-3 py-1 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700">Orphans</button>
            <button className="px-3 py-1 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700">Cycles</button>
          </div>
        </div>
      </div>
    </div>
  );
}

---

// src/pages/ParityLabPage.tsx
import React from 'react';
import { Workbook } from '../types';

export default function ParityLabPage({ workbook }: { workbook: Workbook }) {
  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Parity Lab</h1>
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div>
              <p className="text-slate-400 text-sm">Total Tests</p>
              <p className="text-3xl font-bold text-slate-50">0</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Passed</p>
              <p className="text-3xl font-bold text-green-400">0</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Failed</p>
              <p className="text-3xl font-bold text-red-400">0</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Mismatches</p>
              <p className="text-3xl font-bold text-yellow-400">0</p>
            </div>
          </div>
          <p className="text-slate-400">Generate parity tests from business rules...</p>
        </div>
      </div>
    </div>
  );
}

---

// src/pages/ModernizationPage.tsx
import React from 'react';
import { Workbook } from '../types';

export default function ModernizationPage({ workbook }: { workbook: Workbook }) {
  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Modernization Strategy</h1>
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
          <div className="mb-8">
            <h3 className="text-lg font-bold text-slate-50 mb-4">Modernization Roadmap</h3>
            <div className="flex gap-4">
              {['Protect', 'Understand', 'Isolate', 'Migrate', 'Retire'].map((stage) => (
                <div key={stage} className="flex-1 p-4 bg-slate-800 rounded-lg text-center">
                  <p className="font-semibold text-slate-300">{stage}</p>
                </div>
              ))}
            </div>
          </div>
          <p className="text-slate-400">Evidence-based recommendations with risk and continuity analysis...</p>
        </div>
      </div>
    </div>
  );
}

---

// src/pages/TraceabilityPage.tsx
import React from 'react';
import { Workbook } from '../types';

export default function TraceabilityPage({ workbook }: { workbook: Workbook }) {
  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Traceability Center</h1>
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
          <p className="text-slate-400 mb-6">
            Complete audit trail for every finding, recommendation, and risk.
          </p>
          <p className="text-slate-500">
            Select any finding from the dashboard to trace it back to source data:
            Finding → Rule/Module → Dependency → Source Sheet → Source Record
          </p>
        </div>
      </div>
    </div>
  );
}
