// src/components/common/AIInsightPanel.tsx
// Displays the LLM-generated narrative attached to an agent's findings, and/or
// a clear warning when the agent could not reach the LLM and fell back to
// deterministic template output instead (so the user is never misled into
// thinking non-AI content is AI-generated).
import React from 'react';
import { AlertCircle } from 'lucide-react';

interface AIInsightPanelProps {
  narrative?: string | null;
  aiGenerated?: boolean;
  fallbackReason?: string | null;
}

export default function AIInsightPanel({ narrative, aiGenerated, fallbackReason }: AIInsightPanelProps) {
  if (aiGenerated === false) {
    return (
      <div className="mb-6 p-4 rounded-lg border border-amber-700/50 bg-gradient-to-br from-amber-950/40 to-slate-900">
        <div className="flex items-center gap-2 mb-1">
          <AlertCircle size={18} className="text-amber-400" />
          <h4 className="font-semibold text-amber-300 text-sm">Not AI-Generated</h4>
        </div>
        <p className="text-amber-200/80 text-xs">
          {fallbackReason || 'AI provider unavailable — showing deterministic fallback data, not AI-generated.'}
        </p>
      </div>
    );
  }

  if (!narrative) return null;

  return (
    <div className="mb-6 p-4 rounded-lg border border-indigo-700/50 bg-gradient-to-br from-indigo-950/60 to-slate-900">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">✨</span>
        <h4 className="font-semibold text-indigo-300 text-sm">Agentic AI Analysis</h4>
        <span className="text-xs text-slate-500">Live LLM output · grounded in the real data above, not templated</span>
      </div>
      <p className="text-slate-300 text-sm whitespace-pre-wrap">{narrative}</p>
    </div>
  );
}
