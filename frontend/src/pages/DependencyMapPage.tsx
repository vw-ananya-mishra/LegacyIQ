// src/pages/DependencyMapPage.tsx
import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import ForceGraph3D, { ForceGraphMethods } from 'react-force-graph-3d';
import { Workbook } from '../types';
import { agentAPI, workbookAPI } from '../utils/api';
import AIInsightPanel from '../components/common/AIInsightPanel';

type FilterType = 'all' | 'modules' | 'orphans' | 'cycles';

const TYPE_COLORS: Record<string, string> = {
  application: '#22d3ee',
  module: '#a78bfa',
  data_store: '#34d399',
  integration: '#fb923c',
  unknown: '#94a3b8'
};

const LEGEND = [
  { label: 'Application', color: TYPE_COLORS.application },
  { label: 'Module', color: TYPE_COLORS.module },
  { label: 'Data Store', color: TYPE_COLORS.data_store },
  { label: 'Integration', color: TYPE_COLORS.integration },
  { label: 'Orphan', color: '#facc15' },
  { label: 'In Cycle', color: '#f87171' }
];

export default function DependencyMapPage({ workbook }: { workbook: Workbook }) {
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [graphData, setGraphData] = useState<any>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const [moduleAppMap, setModuleAppMap] = useState<Record<string, string>>({});
  const [selectedAppId, setSelectedAppId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [aiInsight, setAiInsight] = useState<{ narrative: string | null; generated?: boolean; reason?: string | null } | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<ForceGraphMethods>();
  const [dimensions, setDimensions] = useState({ width: 800, height: 560 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const measure = () => setDimensions({ width: el.clientWidth, height: 560 });
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const loadDependencyGraph = async () => {
      try {
        setLoading(true);
        setError(null);
        const [data, apps, mods] = await Promise.all([
          agentAPI.buildDependencyGraph(workbook.workbook_id),
          workbookAPI.getApplications(workbook.workbook_id),
          workbookAPI.getModules(workbook.workbook_id)
        ]);
        setGraphData(data);
        setApplications(apps);
        const map: Record<string, string> = {};
        mods.forEach((m: any) => { map[m.id] = m.application_id; });
        setModuleAppMap(map);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dependency graph');
      } finally {
        setLoading(false);
      }
    };
    loadDependencyGraph();
  }, [workbook.workbook_id]);

  const getFilteredNodes = useCallback(() => {
    if (!graphData?.nodes) return [];
    let nodes = graphData.nodes;
    switch (activeFilter) {
      case 'modules':
        nodes = nodes.filter((n: any) => n.node_type === 'module');
        break;
      case 'orphans':
        nodes = nodes.filter((n: any) => n.is_orphan);
        break;
      case 'cycles':
        nodes = nodes.filter((n: any) => n.in_cycle);
        break;
      default:
        break;
    }

    if (!selectedAppId) return nodes;

    // Keep the application itself, its own modules, and anything directly
    // connected to those modules so cross-system context isn't lost
    const ownedIds = new Set(
      nodes
        .filter((n: any) => n.id === selectedAppId || moduleAppMap[n.id] === selectedAppId)
        .map((n: any) => n.id)
    );
    const neighborIds = new Set<string>();
    (graphData.edges || []).forEach((e: any) => {
      if (ownedIds.has(e.source)) neighborIds.add(e.target);
      if (ownedIds.has(e.target)) neighborIds.add(e.source);
    });
    return nodes.filter((n: any) => ownedIds.has(n.id) || neighborIds.has(n.id));
  }, [graphData, activeFilter, selectedAppId, moduleAppMap]);

  const filteredNodes = getFilteredNodes();

  const handleGenerateAiInsight = async () => {
    try {
      setAiLoading(true);
      const result = await agentAPI.analyzeWithAgent(workbook.workbook_id, 'dependency_detective', {});
      const f = result?.findings || {};
      const narrative = [f.ai_narrative, f.orphan_analysis, f.cycle_analysis].filter(Boolean).join(' ');
      setAiInsight({ narrative: narrative || null, generated: f.ai_generated, reason: f.ai_fallback_reason });
    } catch (err) {
      setAiInsight({ narrative: null, generated: false, reason: err instanceof Error ? err.message : 'Failed to generate AI insight' });
    } finally {
      setAiLoading(false);
    }
  };

  // Data shaped for the 3D force graph: bigger nodes for more-connected entities
  const graph3d = useMemo(() => {
    const ids = new Set(filteredNodes.map((n: any) => n.id));
    const links = (graphData?.edges || [])
      .filter((e: any) => ids.has(e.source) && ids.has(e.target))
      .map((e: any) => ({ ...e }));
    const nodes = filteredNodes.map((n: any) => ({
      ...n,
      val: Math.max(1.5, ((n.in_degree || 0) + (n.out_degree || 0)) * 1.5)
    }));
    return { nodes, links };
  }, [filteredNodes, graphData]);

  const nodeColor = useCallback((node: any) => {
    if (node.in_cycle) return '#f87171';
    if (node.is_orphan) return '#facc15';
    return TYPE_COLORS[node.node_type] || TYPE_COLORS.unknown;
  }, []);

  // Full id -> name lookup (independent of active filters) so upstream/downstream
  // lists can always show a readable name even for neighbors outside the current view
  const nodeNameById = useMemo(() => {
    const map: Record<string, string> = {};
    (graphData?.nodes || []).forEach((n: any) => { map[n.id] = n.name || n.id; });
    return map;
  }, [graphData]);


  const selectedNodeLinks = useMemo(() => {
    if (!selectedNode) return { upstream: [] as { id: string; name: string }[], downstream: [] as { id: string; name: string }[] };
    const upstream: { id: string; name: string }[] = [];
    const downstream: { id: string; name: string }[] = [];
    (graphData?.edges || []).forEach((e: any) => {
      if (e.source === selectedNode.id) upstream.push({ id: e.target, name: nodeNameById[e.target] || e.target });
      if (e.target === selectedNode.id) downstream.push({ id: e.source, name: nodeNameById[e.source] || e.source });
    });
    return { upstream, downstream };
  }, [selectedNode, graphData, nodeNameById]);

  // Slow cinematic orbit until the user takes control of the camera
  useEffect(() => {
    if (loading || graph3d.nodes.length === 0) return;
    const fg = fgRef.current;
    if (!fg) return;

    fg.d3Force('charge')?.strength(-140);
    setTimeout(() => fg.zoomToFit(600, 60), 250);

    let angle = 0;
    let stopped = false;
    const distance = 320;
    const timer = window.setInterval(() => {
      if (stopped) return;
      angle += 0.0018;
      fg.cameraPosition({ x: distance * Math.sin(angle), z: distance * Math.cos(angle) });
    }, 30);

    const stop = () => { stopped = true; };
    const el = containerRef.current;
    el?.addEventListener('pointerdown', stop, { once: true });
    el?.addEventListener('wheel', stop, { once: true });

    return () => {
      window.clearInterval(timer);
      el?.removeEventListener('pointerdown', stop);
      el?.removeEventListener('wheel', stop);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, graph3d.nodes.length, activeFilter, selectedAppId]);

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Dependency Graph</h1>
        <p className="text-slate-400 mb-8">
          Interactive 3D visualization of dependencies across applications, modules, data stores, integrations, and APIs.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
            {error}
          </div>
        )}

        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8">
          {/* Statistics */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-800 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">{selectedAppId ? 'Visible Nodes' : 'Total Nodes'}</p>
              <p className="text-2xl font-bold text-slate-50">{graph3d.nodes.length}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">{selectedAppId ? 'Visible Edges' : 'Total Edges'}</p>
              <p className="text-2xl font-bold text-slate-50">{graph3d.links.length}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Orphaned Nodes</p>
              <p className="text-2xl font-bold text-yellow-400">
                {graph3d.nodes.filter((n: any) => n.is_orphan).length}
              </p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Cycles Detected</p>
              <p className="text-2xl font-bold text-red-400">
                {graphData?.cycles?.length || 0}
              </p>
            </div>
          </div>

          {/* AI Insight */}
          <div className="mb-6">
            <button
              onClick={handleGenerateAiInsight}
              disabled={aiLoading || loading}
              className="px-4 py-2 rounded-lg text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 text-white transition-all mb-3"
            >
              {aiLoading ? 'Analyzing Graph...' : '✨ Generate AI Insight'}
            </button>
            {aiInsight && (
              <AIInsightPanel narrative={aiInsight.narrative} aiGenerated={aiInsight.generated} fallbackReason={aiInsight.reason} />
            )}
          </div>

          {/* Filters */}
          <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
            <div className="flex gap-2">
              {(['all', 'modules', 'orphans', 'cycles'] as const).map((filter) => (
                <button
                  key={filter}
                  onClick={() => { setActiveFilter(filter); setSelectedNode(null); }}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                    activeFilter === filter
                      ? 'bg-cyan-600 text-white'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {filter.charAt(0).toUpperCase() + filter.slice(1)}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-3">
              <select
                value={selectedAppId}
                onChange={(e) => { setSelectedAppId(e.target.value); setSelectedNode(null); }}
                className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-50 text-sm focus:outline-none focus:border-cyan-600"
              >
                <option value="">All Applications</option>
                {applications.map((app: any) => (
                  <option key={app.id} value={app.id}>{app.name}</option>
                ))}
              </select>
              {!loading && graph3d.nodes.length > 0 && (
                <button
                  onClick={() => fgRef.current?.zoomToFit(600, 60)}
                  className="px-3 py-2 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
                >
                  Reset View
                </button>
              )}
            </div>
          </div>

          {/* 3D Graph Visualization */}
          <div
            ref={containerRef}
            className="relative rounded-lg mb-6 border border-slate-700 overflow-hidden"
            style={{ height: 560, background: 'radial-gradient(circle at 50% 30%, #0f1c33 0%, #020617 75%)' }}
          >
            {loading ? (
              <div className="h-full flex items-center justify-center">
                <p className="text-slate-500">Loading dependency graph...</p>
              </div>
            ) : graph3d.nodes.length === 0 ? (
              <div className="h-full flex items-center justify-center">
                <p className="text-slate-500">No nodes to visualize for this filter</p>
              </div>
            ) : (
              <>
                <ForceGraph3D
                  ref={fgRef}
                  graphData={graph3d}
                  width={dimensions.width}
                  height={dimensions.height}
                  backgroundColor="rgba(0,0,0,0)"
                  showNavInfo={false}
                  nodeLabel={(n: any) => `${n.name} · ${n.node_type} · ${n.out_degree || 0} upstream · ${n.in_degree || 0} downstream${n.is_orphan ? ' · orphan' : ''}${n.in_cycle ? ' · in cycle' : ''}`}
                  nodeColor={nodeColor}
                  nodeVal="val"
                  nodeOpacity={0.94}
                  nodeResolution={20}
                  linkColor={(l: any) => (l.criticality === 'critical' ? '#f87171' : 'rgba(148,163,184,0.55)')}
                  linkWidth={(l: any) => (l.criticality === 'critical' ? 2.2 : 0.6)}
                  linkOpacity={0.55}
                  linkDirectionalParticles={(l: any) => (l.criticality === 'critical' ? 3 : 1)}
                  linkDirectionalParticleWidth={1.6}
                  linkDirectionalParticleSpeed={0.006}
                  onNodeClick={(node: any) => {
                    setSelectedNode(node);
                    fgRef.current?.cameraPosition(
                      { x: node.x, y: node.y, z: (node.z || 0) + 120 },
                      { x: node.x, y: node.y, z: node.z },
                      800
                    );
                  }}
                  onBackgroundClick={() => setSelectedNode(null)}
                />
                <div className="absolute top-3 left-3 text-xs text-slate-400 bg-slate-900/70 px-3 py-1.5 rounded-lg border border-slate-700">
                  Drag to rotate · Scroll to zoom · Click a node for details
                </div>
                {selectedNode && (
                  <div className="absolute bottom-3 right-3 max-w-sm max-h-[70%] overflow-y-auto bg-slate-900/90 backdrop-blur border border-slate-700 rounded-lg p-4 text-sm">
                    <p className="font-semibold text-slate-50">{selectedNode.name}</p>
                    <p className="text-slate-400 text-xs mb-2">{selectedNode.node_type}</p>
                    <div className="flex gap-2 mb-3">
                      {selectedNode.is_orphan && <span className="text-xs bg-yellow-900/30 text-yellow-300 px-2 py-1 rounded">Orphan</span>}
                      {selectedNode.in_cycle && <span className="text-xs bg-red-900/30 text-red-300 px-2 py-1 rounded">In Cycle</span>}
                    </div>
                    <div className="mb-2">
                      <p className="text-slate-300 text-xs font-semibold">
                        Upstream ({selectedNodeLinks.upstream.length}) <span className="font-normal text-slate-500">· what this depends on</span>
                      </p>
                      <p className="text-slate-400 text-xs">
                        {selectedNodeLinks.upstream.length > 0
                          ? selectedNodeLinks.upstream.map((u) => u.name).join(', ')
                          : 'None'}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-300 text-xs font-semibold">
                        Downstream ({selectedNodeLinks.downstream.length}) <span className="font-normal text-slate-500">· what depends on this</span>
                      </p>
                      <p className="text-slate-400 text-xs">
                        {selectedNodeLinks.downstream.length > 0
                          ? selectedNodeLinks.downstream.map((d) => d.name).join(', ')
                          : 'None'}
                      </p>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Legend */}
          <div className="flex flex-wrap gap-4 mb-6 text-xs text-slate-400">
            {LEGEND.map((item) => (
              <span key={item.label} className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full inline-block" style={{ background: item.color }} />
                {item.label}
              </span>
            ))}
          </div>

          {/* Dependency Details */}
          {!loading && graphData && (
            <div>
              <h3 className="text-lg font-bold text-slate-50 mb-4">
                {activeFilter === 'all' && 'All Dependencies'}
                {activeFilter === 'modules' && 'Module Dependencies'}
                {activeFilter === 'orphans' && 'Orphaned Nodes'}
                {activeFilter === 'cycles' && 'Nodes in Cycles'}
              </h3>
              {filteredNodes.length === 0 ? (
                <p className="text-slate-500">No nodes found for this filter</p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {filteredNodes.slice(0, 50).map((node: any, idx: number) => (
                    <button
                      key={node.id || `node-${idx}`}
                      onClick={() => setSelectedNode(node)}
                      className="w-full text-left bg-slate-800 p-3 rounded-lg border border-slate-700 text-sm hover:border-cyan-600 transition-colors"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-semibold text-slate-50">{node.name}</p>
                          <p className="text-slate-400 text-xs">{node.node_type}</p>
                        </div>
                        <div className="flex gap-2">
                          {node.is_orphan && <span className="text-xs bg-yellow-900/30 text-yellow-300 px-2 py-1 rounded">Orphan</span>}
                          {node.in_cycle && <span className="text-xs bg-red-900/30 text-red-300 px-2 py-1 rounded">Cycle</span>}
                        </div>
                      </div>
                    </button>
                  ))}
                  {filteredNodes.length > 50 && (
                    <p className="text-slate-500 text-sm">Showing 50 of {filteredNodes.length} nodes</p>
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
