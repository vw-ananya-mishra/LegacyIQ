// LegacyX Types
// src/types/index.ts

export interface Workbook {
  workbook_id: string;
  sheets: string[];
  sheet_counts: Record<string, number>;
  ingestion_time: string;
  total_sheets: number;
}

export interface Application {
  id: string;
  name: string;
  description?: string;
  status: string;
  criticality: string;
  complexity: string;
  technology_stack?: string;
  lines_of_code?: number;
  last_modified?: string;
  source_sheet: string;
  source_row: number;
  trace_id: string;
}

export interface CodeModule {
  id: string;
  application_id: string;
  name: string;
  description?: string;
  language: string;
  lines_of_code?: number;
  complexity_score: number;
  test_coverage?: number;
  critical_functions?: number;
  source_sheet: string;
  source_row: number;
  trace_id: string;
}

export interface BusinessRule {
  id: string;
  application_id: string;
  rule_name: string;
  description?: string;
  condition?: string;
  action?: string;
  criticality: string;
  test_coverage?: string;
  source_sheet: string;
  source_row: number;
  trace_id: string;
}

export interface Dependency {
  id: string;
  source_id: string;
  source_type: string;
  target_id: string;
  target_type: string;
  relationship_type: string;
  criticality?: string;
  description?: string;
  source_sheet: string;
  source_row: number;
  trace_id: string;
}

export interface Risk {
  id: string;
  entity_id: string;
  entity_type: string;
  risk_type: string;
  risk_description: string;
  severity: string;
  remediation?: string;
  source_sheet: string;
  source_row: number;
  trace_id: string;
}

export interface ParityTest {
  rule_id: string;
  rule: string;
  input: string;
  expected_output: string;
  legacy_result?: string;
  modern_result?: string;
  status: 'pending_execution' | 'passed' | 'failed' | 'mismatch';
  source_rule: BusinessRule;
}

export interface Recommendation {
  id: string;
  recommendation: string;
  reason: string;
  evidence: Risk[];
  risk: string;
  continuity_impact: string;
  effort: string;
  dependencies: string[];
  status: 'draft' | 'needs_review' | 'approved' | 'rejected';
  priority: number;
}

export interface DependencyNode {
  id: string;
  label: string;
  in_degree: number;
  out_degree: number;
}

export interface DependencyEdge {
  source: string;
  target: string;
  relationship: string;
  criticality: string;
}

export interface DependencyGraphData {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
  orphan_nodes: string[];
  cycles: string[][];
  statistics: {
    node_count: number;
    edge_count: number;
    graph_density: number;
  };
}

export interface AgentAnalysis {
  agent_type: string;
  status: string;
  findings: Record<string, any>;
  evidence: Array<Record<string, any>>;
  confidence: number;
  trace: Array<Record<string, any>>;
}

export interface DashboardSummary {
  applications: number;
  modules: number;
  business_rules: number;
  dependencies: number;
  test_cases: number;
  integrations: number;
  metrics: {
    rule_test_coverage: number;
    module_test_coverage: number;
    module_documentation_coverage: number;
  };
  pipeline: {
    understand: { status: string; completion: number };
    document: { status: string; completion: number };
    map: { status: string; completion: number };
    test: { status: string; completion: number };
    modernize: { status: string; completion: number };
  };
}

export interface TraceChain {
  step: number;
  level: string;
  type: string;
  data?: Record<string, any>;
}
