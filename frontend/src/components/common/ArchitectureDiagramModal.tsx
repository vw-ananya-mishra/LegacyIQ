// src/components/common/ArchitectureDiagramModal.tsx
// Modal showing a "before vs after" architecture diagram for a single
// modernization recommendation, rendered with ReactFlow. The topology
// (upstream deps, downstream dependents, data stores, integrations) is
// real dependency-graph data; only node labels for the "after" view and
// the key-changes/narrative are AI-authored.
import React, { useEffect, useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import ReactFlow, { Background, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import { agentAPI } from '../../utils/api';
import AIInsightPanel from './AIInsightPanel';

interface Props {
  workbookId: string;
  recommendationId: string | null;
  recommendationTitle?: string;
  onClose: () => void;
}

const NODE_TYPE_COLOR: Record<string, string> = {
  application: '#0e7490',
  module: '#6d28d9',
  data_store: '#15803d',
  integration: '#c2410c',
};

// Layered left-to-right layout: downstream dependents (callers) -> focus -> upstream deps/DB/integrations
function toFlow(arch: any, focusId: string): { nodes: Node[]; edges: Edge[] } {
  const rawNodes = arch?.nodes || [];
  const rawEdges = arch?.edges || [];

  const downstreamIds = new Set(rawEdges.filter((e: any) => String(e.target) === String(focusId)).map((e: any) => String(e.source)));
  const upstreamIds = new Set(rawEdges.filter((e: any) => String(e.source) === String(focusId)).map((e: any) => String(e.target)));

  const downstream = rawNodes.filter((n: any) => downstreamIds.has(String(n.id)) && String(n.id) !== String(focusId));
  const upstream = rawNodes.filter((n: any) => upstreamIds.has(String(n.id)) && String(n.id) !== String(focusId));
  const focus = rawNodes.find((n: any) => String(n.id) === String(focusId));

  const nodes: Node[] = [];
  const colOf = (n: any) => NODE_TYPE_COLOR[n.node_type] || '#475569';

  downstream.forEach((n: any, idx: number) => {
    nodes.push({
      id: String(n.id),
      data: { label: n.label || n.id },
      position: { x: 0, y: idx * 90 },
      style: { background: colOf(n), color: '#f1f5f9', border: '1px solid #94a3b8', borderRadius: 8, fontSize: 12, padding: 8, width: 190 },
    });
  });
  if (focus) {
    nodes.push({
      id: String(focus.id),
      data: { label: focus.label || focus.id },
      position: { x: 280, y: (Math.max(downstream.length, upstream.length) * 90) / 2 - 20 },
      style: { background: '#1e293b', color: '#fde68a', border: '2px solid #fbbf24', borderRadius: 8, fontSize: 13, fontWeight: 700, padding: 10, width: 200 },
    });
  }
  upstream.forEach((n: any, idx: number) => {
    nodes.push({
      id: String(n.id),
      data: { label: n.label || n.id },
      position: { x: 560, y: idx * 90 },
      style: { background: colOf(n), color: '#f1f5f9', border: '1px solid #94a3b8', borderRadius: 8, fontSize: 12, padding: 8, width: 190 },
    });
  });

  const edges: Edge[] = rawEdges.map((e: any, idx: number) => ({
    id: `e-${idx}-${e.source}-${e.target}`,
    source: String(e.source),
    target: String(e.target),
    label: e.label,
    animated: true,
    style: { stroke: '#64748b' },
    labelStyle: { fill: '#cbd5e1', fontSize: 10 },
  }));
  return { nodes, edges };
}

export default function ArchitectureDiagramModal({ workbookId, recommendationId, recommendationTitle, onClose }: Props) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [codeLoading, setCodeLoading] = useState(false);
  const [codeData, setCodeData] = useState<any>(null);
  const [codeError, setCodeError] = useState<string | null>(null);

  useEffect(() => {
    if (!recommendationId) return;
    setLoading(true);
    setError(null);
    setData(null);
    setCodeData(null);
    setCodeError(null);
    agentAPI.getArchitectureDiagram(workbookId, recommendationId)
      .then((res) => setData(res.findings))
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load diagram'))
      .finally(() => setLoading(false));
  }, [workbookId, recommendationId]);

  const handleSuggestCode = async () => {
    if (!recommendationId) return;
    try {
      setCodeLoading(true);
      setCodeError(null);
      const res = await agentAPI.getModernizedCode(workbookId, recommendationId);
      setCodeData(res.findings);
    } catch (err) {
      setCodeError(err instanceof Error ? err.message : 'Failed to generate modernized code');
    } finally {
      setCodeLoading(false);
    }
  };

  const focusId = data?.recommendation?.module_id || data?.recommendation?.application_id;
  const oldFlow = toFlow(data?.old_architecture, focusId);
  const newFlow = toFlow(data?.new_architecture, focusId);
  const diagramHeight = Math.max(220, (Math.max(oldFlow.nodes.length, 3) - 1) * 90 + 100);

  return (
    <Dialog.Root open={!!recommendationId} onOpenChange={(open) => { if (!open) onClose(); }}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/70 z-40" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[95vw] max-w-6xl max-h-[90vh] overflow-y-auto bg-slate-900 border border-slate-700 rounded-xl p-6 z-50">
          <div className="flex items-center justify-between mb-4">
            <Dialog.Title className="text-xl font-bold text-slate-50">
              Architecture: Before vs After{recommendationTitle ? ` — ${recommendationTitle}` : ''}
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-slate-400 hover:text-slate-100 text-2xl leading-none">×</button>
            </Dialog.Close>
          </div>

          {loading && <p className="text-slate-400">Generating architecture diagram...</p>}
          {error && <p className="text-red-400">{error}</p>}

          {data && (
            <div className="space-y-6">
              <AIInsightPanel narrative={data.ai_narrative} aiGenerated={data.ai_generated} fallbackReason={data.ai_fallback_reason} />

              <div className="flex flex-wrap gap-4 text-xs text-slate-400">
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full inline-block" style={{ background: '#fbbf24' }} /> Focus component</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full inline-block" style={{ background: NODE_TYPE_COLOR.application }} /> Application</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full inline-block" style={{ background: NODE_TYPE_COLOR.module }} /> Module</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full inline-block" style={{ background: NODE_TYPE_COLOR.data_store }} /> Data Store</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full inline-block" style={{ background: NODE_TYPE_COLOR.integration }} /> Integration</span>
                <span>Left = downstream (depends on this) · Right = upstream (this depends on) / data / integrations</span>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-red-300 mb-2">BEFORE (Legacy)</h3>
                <div style={{ height: diagramHeight }} className="bg-slate-950 border border-slate-800 rounded-lg">
                  <ReactFlow nodes={oldFlow.nodes} edges={oldFlow.edges} fitView proOptions={{ hideAttribution: true }}>
                    <Background color="#334155" gap={16} />
                  </ReactFlow>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-green-300 mb-2">AFTER (Modernized)</h3>
                <div style={{ height: diagramHeight }} className="bg-slate-950 border border-slate-800 rounded-lg">
                  <ReactFlow nodes={newFlow.nodes} edges={newFlow.edges} fitView proOptions={{ hideAttribution: true }}>
                    <Background color="#334155" gap={16} />
                  </ReactFlow>
                </div>
              </div>

              {data.key_changes && data.key_changes.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-200 mb-2">Key Changes</h3>
                  <ul className="list-disc list-inside text-slate-300 text-sm space-y-1">
                    {data.key_changes.map((c: string, idx: number) => <li key={idx}>{c}</li>)}
                  </ul>
                </div>
              )}

              <div className="border-t border-slate-800 pt-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-slate-200">💻 Suggested Modernized Code</h3>
                  <button
                    onClick={handleSuggestCode}
                    disabled={codeLoading}
                    className="px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 text-white transition-all"
                  >
                    {codeLoading ? 'Translating Code...' : '✨ Suggest Modernized Code'}
                  </button>
                </div>

                {codeError && <p className="text-red-400 text-sm mb-3">{codeError}</p>}

                {codeData && codeData.available === false && (
                  <p className="text-slate-500 text-sm">{codeData.reason}</p>
                )}

                {codeData && codeData.available !== false && (
                  <div>
                    <AIInsightPanel narrative={codeData.ai_narrative} aiGenerated={codeData.ai_generated} fallbackReason={codeData.ai_fallback_reason} />
                    {codeData.explanation && (
                      <p className="text-slate-300 text-sm mb-3">{codeData.explanation}</p>
                    )}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs font-semibold text-red-300 mb-1">
                          Original COBOL{codeData.paragraph_name ? ` — ${codeData.paragraph_name}` : ''}
                        </p>
                        <pre className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 overflow-x-auto max-h-80 overflow-y-auto whitespace-pre-wrap">
                          {codeData.original_code}
                        </pre>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-green-300 mb-1">
                          Modernized{codeData.language ? ` (${codeData.language})` : ''}
                        </p>
                        <pre className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 overflow-x-auto max-h-80 overflow-y-auto whitespace-pre-wrap">
                          {codeData.modernized_code || 'No modernized code generated.'}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
