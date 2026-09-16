// src/pages/DependencyMapPage.tsx
import React, { useState, useEffect } from 'react';
import { Workbook } from '../types';
import { agentAPI } from '../utils/api';

type FilterType = 'all' | 'modules' | 'orphans' | 'cycles';

export default function DependencyMapPage({ workbook }: { workbook: Workbook }) {
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDependencyGraph = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await agentAPI.buildDependencyGraph(workbook.workbook_id);
        setGraphData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dependency graph');
      } finally {
        setLoading(false);
      }
    };
    loadDependencyGraph();
  }, [workbook.workbook_id]);

  const getFilteredNodes = () => {
    if (!graphData?.nodes) return [];
    switch (activeFilter) {
      case 'orphans':
        return graphData.nodes.filter((n: any) => n.is_orphan);
      case 'cycles':
        return graphData.nodes.filter((n: any) => n.in_cycle);
      default:
        return graphData.nodes;
    }
  };

  const filteredNodes = getFilteredNodes();

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-slate-50">Dependency Graph</h1>
        <p className="text-slate-400 mb-8">
          Interactive visualization of dependencies across applications, modules, data stores, integrations, and APIs.
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
              <p className="text-slate-400 text-sm">Total Nodes</p>
              <p className="text-2xl font-bold text-slate-50">{graphData?.nodes?.length || 0}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Total Edges</p>
              <p className="text-2xl font-bold text-slate-50">{graphData?.edges?.length || 0}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Orphaned Nodes</p>
              <p className="text-2xl font-bold text-yellow-400">
                {graphData?.nodes?.filter((n: any) => n.is_orphan).length || 0}
              </p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Cycles Detected</p>
              <p className="text-2xl font-bold text-red-400">
                {graphData?.cycles?.length || 0}
              </p>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-2 mb-6">
            {(['all', 'modules', 'orphans', 'cycles'] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
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

          {/* Graph Visualization Placeholder */}
          <div className="bg-slate-800 rounded-lg h-96 flex items-center justify-center mb-6 border border-slate-700">
            {loading ? (
              <p className="text-slate-500">Loading dependency graph...</p>
            ) : (
              <div className="text-center">
                <p className="text-slate-400 mb-2">Graph Visualization</p>
                <p className="text-slate-500 text-sm">
                  {activeFilter === 'all' && `Showing ${filteredNodes.length} nodes and ${graphData?.edges?.length || 0} dependencies`}
                  {activeFilter === 'orphans' && `Found ${filteredNodes.length} orphaned nodes`}
                  {activeFilter === 'cycles' && `Found ${filteredNodes.filter((n: any) => n.in_cycle).length} nodes in cycles`}
                </p>
              </div>
            )}
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
                    <div key={node.id || `node-${idx}`} className="bg-slate-800 p-3 rounded-lg border border-slate-700 text-sm">
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
                    </div>
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
