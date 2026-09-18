"""
Analysis Engine & Agent Orchestrator
Core intelligence for LegacyIQ
"""

import sqlite3
import uuid
from typing import Dict, List, Any, Tuple, Optional
import networkx as nx
from collections import defaultdict, deque
import re
from app.services import llm_service


def _merge_ai_notes(items: List[Dict], notes: Any, get_item_id, target_field: str, keep_original_if_missing: bool = False) -> List[Dict]:
    """
    Merge compact {"id": ..., "text": ...} notes from the LLM onto a list of
    deterministic items (matched by id), without requiring the LLM to echo
    back full records. This keeps AI output small (fast) and tolerates the
    model only covering a subset of ids (no all-or-nothing validation).
    """
    notes_map: Dict[str, str] = {}
    if isinstance(notes, list):
        for n in notes:
            if isinstance(n, dict) and n.get("id") not in (None, ""):
                notes_map[str(n["id"])] = str(n.get("text", ""))
    merged_items = []
    for item in items:
        merged = dict(item)
        item_id = str(get_item_id(item))
        if item_id in notes_map:
            merged[target_field] = notes_map[item_id]
        elif not keep_original_if_missing:
            merged[target_field] = ""
        merged_items.append(merged)
    return merged_items


class AnalysisEngine:
    """
    Core analysis capabilities:
    - Dependency graph analysis
    - Risk identification
    - Coverage analysis
    - Orphan detection
    - Cycle detection
    """
    
    def __init__(self):
        pass
    
    def build_dependency_graph(self, workbook_id: str, filters: Optional[List[str]] = None,
                              detect_orphans: bool = True, detect_cycles: bool = True) -> Dict[str, Any]:
        """Build interactive dependency graph with analysis"""
        from app.services.xlsx_ingestion import XLSXIngestionService
        
        svc = XLSXIngestionService()
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build a lookup of every known entity so isolated (orphan) entities
        # are represented as nodes even if they never appear in a dependency
        entity_lookup: Dict[str, Dict[str, str]] = {}
        entity_queries = [
            ("applications", "id, name", "application"),
            ("code_modules", "id, name", "module"),
            ("data_stores", "id, name", "data_store"),
            ("integrations", "id, interface_name as name", "integration"),
        ]
        for table, columns, node_type in entity_queries:
            cursor.execute(f"SELECT {columns} FROM {table}")
            for row in cursor.fetchall():
                entity_lookup[row['id']] = {"name": row['name'] or row['id'], "node_type": node_type}
        
        # Fetch all dependencies
        cursor.execute("SELECT * FROM dependencies")
        deps = [dict(row) for row in cursor.fetchall()]
        
        # Build NetworkX graph (filter out None values)
        G = nx.DiGraph()
        
        # Seed the graph with every known entity so orphans are detectable
        for entity_id, info in entity_lookup.items():
            G.add_node(entity_id, **info)
        
        for dep in deps:
            source = dep['source_id']
            target = dep['target_id']
            # Skip if source or target is None
            if source is None or target is None:
                continue
            if source not in entity_lookup:
                entity_lookup[source] = {"name": source, "node_type": dep.get('source_type') or 'unknown'}
            if target not in entity_lookup:
                entity_lookup[target] = {"name": target, "node_type": dep.get('target_type') or 'unknown'}
            G.add_node(source, **entity_lookup[source])
            G.add_node(target, **entity_lookup[target])
            G.add_edge(source, target,
                      relationship=dep['relationship_type'],
                      criticality=dep['criticality'])
        
        # Detect orphans (nodes with no incoming or outgoing edges)
        orphan_ids = set()
        if detect_orphans:
            for node in G.nodes():
                if G.in_degree(node) == 0 and G.out_degree(node) == 0:
                    orphan_ids.add(node)
        
        # Detect cycles
        cycles = []
        if detect_cycles:
            cycles = list(nx.simple_cycles(G))
        cycle_ids = {node for cycle in cycles for node in cycle}
        
        # Convert to node/edge lists for visualization
        nodes = []
        edges = []
        
        for node, attrs in G.nodes(data=True):
            in_degree = G.in_degree(node)
            out_degree = G.out_degree(node)
            nodes.append({
                "id": node,
                "label": attrs.get('name', node),
                "name": attrs.get('name', node),
                "node_type": attrs.get('node_type', 'unknown'),
                "in_degree": in_degree,
                "out_degree": out_degree,
                "is_orphan": node in orphan_ids,
                "in_cycle": node in cycle_ids
            })
        
        for source, target, attrs in G.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "relationship": attrs.get('relationship', 'depends_on'),
                "criticality": attrs.get('criticality', 'medium')
            })
        
        result = {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "graph_density": nx.density(G) if len(nodes) > 1 else 0
            },
            "orphan_nodes": list(orphan_ids),
            "cycles": cycles
        }
        
        return result
    
    def generate_dashboard_summary(self, workbook_id: str) -> Dict[str, Any]:
        """Generate command center dashboard summary"""
        from app.services.xlsx_ingestion import XLSXIngestionService
        
        svc = XLSXIngestionService()
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query counts for each entity type
        cursor.execute("SELECT COUNT(*) as count FROM applications")
        app_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM code_modules")
        module_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM business_rules")
        rule_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM dependencies")
        dep_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM test_cases")
        test_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM integrations")
        integration_count = cursor.fetchone()[0]
        
        # Calculate coverage metrics
        cursor.execute("""
            SELECT COUNT(DISTINCT rule_id) as count FROM test_cases
        """)
        tested_rules = cursor.fetchone()[0]
        
        rule_coverage = (tested_rules / rule_count * 100) if rule_count > 0 else 0
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM code_modules WHERE has_unit_tests = 'Y'
        """)
        tested_modules = cursor.fetchone()[0]
        
        module_coverage = (tested_modules / module_count * 100) if module_count > 0 else 0
        
        # Count documented modules
        cursor.execute("""
            SELECT COUNT(*) as count FROM code_modules WHERE description_present = 'Y'
        """)
        documented_modules = cursor.fetchone()[0]
        
        doc_coverage = (documented_modules / module_count * 100) if module_count > 0 else 0
        
        # Understand: complete as soon as the estate has been ingested & is explorable
        understand_completion = 100.0 if app_count > 0 else 0.0
        
        # Document: proxy from each application's existing legacy doc coverage
        cursor.execute("SELECT doc_coverage_pct FROM applications")
        doc_pcts = [row[0] for row in cursor.fetchall() if row[0] is not None]
        document_completion = (sum(doc_pcts) / len(doc_pcts)) if doc_pcts else 0.0
        
        # Map: cleanliness of the dependency graph (fewer orphans/cycles = more resolved)
        graph = self.build_dependency_graph(workbook_id)
        total_nodes = len(graph.get('nodes', []))
        orphan_count = len(graph.get('orphan_nodes', []))
        cycle_node_ids = {n for cycle in graph.get('cycles', []) for n in cycle}
        unresolved = orphan_count + len(cycle_node_ids)
        map_completion = max(0.0, (1 - (unresolved / total_nodes)) * 100) if total_nodes > 0 else 0.0
        
        # Modernize: share of backlog items already completed
        cursor.execute("SELECT COUNT(*) as count FROM modernization_backlog")
        backlog_total = cursor.fetchone()[0]
        cursor.execute("""
            SELECT COUNT(*) as count FROM modernization_backlog
            WHERE LOWER(status) IN ('done', 'completed', 'closed')
        """)
        backlog_done = cursor.fetchone()[0]
        modernize_completion = (backlog_done / backlog_total * 100) if backlog_total > 0 else 0.0
        
        def stage_status(completion: float) -> str:
            if completion >= 100:
                return "completed"
            if completion > 0:
                return "in_progress"
            return "pending"
        
        return {
            "applications": app_count,
            "modules": module_count,
            "business_rules": rule_count,
            "dependencies": dep_count,
            "test_cases": test_count,
            "integrations": integration_count,
            "metrics": {
                "rule_test_coverage": round(rule_coverage, 2),
                "module_test_coverage": round(module_coverage, 2),
                "module_documentation_coverage": round(doc_coverage, 2)
            },
            "pipeline": {
                "understand": {"status": stage_status(understand_completion), "completion": round(understand_completion, 2)},
                "document": {"status": stage_status(document_completion), "completion": round(document_completion, 2)},
                "map": {"status": stage_status(map_completion), "completion": round(map_completion, 2)},
                "test": {"status": stage_status(rule_coverage), "completion": round(rule_coverage, 2)},
                "modernize": {"status": stage_status(modernize_completion), "completion": round(modernize_completion, 2)}
            }
        }
    
    def identify_risks(self, workbook_id: str) -> List[Dict[str, Any]]:
        """Identify security, continuity, and complexity risks"""
        from app.services.xlsx_ingestion import XLSXIngestionService
        
        svc = XLSXIngestionService()
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        risks = []
        risk_id = 0
        
        # Risk: Undocumented business-critical modules (high-criticality app, no description)
        cursor.execute("""
            SELECT cm.id, cm.name, cm.complexity_score FROM code_modules cm
            JOIN applications a ON a.id = cm.application_id
            WHERE cm.description_present = 'N' AND a.criticality = 'High'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "module",
                "risk_type": "documentation",
                "risk_description": f"Undocumented module '{row['name']}' inside a High-criticality application — hidden knowledge risk",
                "severity": "high",
                "remediation": "Generate functional specification and API documentation"
            })
        
        # Risk: High-complexity hotspots (very complex, no tests, no docs)
        cursor.execute("""
            SELECT id, name, complexity_score FROM code_modules
            WHERE complexity_score >= 38 AND has_unit_tests = 'N' AND description_present = 'N'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "module",
                "risk_type": "complexity",
                "risk_description": f"Module '{row['name']}' has very high complexity ({row['complexity_score']}) with no tests and no docs — risky to modernize",
                "severity": "critical",
                "remediation": "Refactor into smaller, testable units before modernization"
            })
        
        # Risk: Dead code (candidates to retire, not migrate)
        cursor.execute("""
            SELECT id, name FROM code_modules WHERE is_dead_code = 'Y'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "module",
                "risk_type": "dead_code",
                "risk_description": f"Module '{row['name']}' is flagged as dead code — candidate to retire, not migrate",
                "severity": "medium",
                "remediation": "Confirm with owners and remove from migration scope"
            })
        
        # Risk: Orphan/dangling dependencies (edge points to a non-existent entity)
        cursor.execute("SELECT id FROM code_modules")
        module_ids = {r['id'] for r in cursor.fetchall()}
        cursor.execute("SELECT id FROM data_stores")
        store_ids = {r['id'] for r in cursor.fetchall()}
        cursor.execute("SELECT id FROM integrations")
        integration_ids = {r['id'] for r in cursor.fetchall()}
        cursor.execute("SELECT id FROM applications")
        app_ids = {r['id'] for r in cursor.fetchall()}
        valid_by_type = {
            "module": module_ids, "data_store": store_ids,
            "integration": integration_ids, "application": app_ids
        }
        cursor.execute("SELECT * FROM dependencies")
        for row in cursor.fetchall():
            valid_ids = valid_by_type.get(row['target_type'], set())
            if row['target_id'] not in valid_ids or row['source_id'] not in module_ids:
                risk_id += 1
                risks.append({
                    "id": f"risk_{risk_id}",
                    "entity_id": row['id'],
                    "entity_type": "dependency",
                    "risk_type": "orphan_dependency",
                    "risk_description": f"Dependency '{row['id']}' points from '{row['source_id']}' to non-existent {row['target_type']} '{row['target_id']}'",
                    "severity": "high",
                    "remediation": "Clean up dangling references before migration"
                })
        
        # Risk: Untested critical business rules
        cursor.execute("""
            SELECT id, rule_name, criticality FROM business_rules
            WHERE LOWER(criticality) = 'high' AND has_test_case = 'N'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "rule",
                "risk_type": "test_coverage",
                "risk_description": f"High-criticality business rule '{row['rule_name']}' has no test coverage — parity risk",
                "severity": "critical",
                "remediation": "Create comprehensive test cases for parity validation"
            })
        
        # Risk: Duplicated business logic
        cursor.execute("""
            SELECT id, rule_name, duplicate_of FROM business_rules WHERE duplicate_of IS NOT NULL AND duplicate_of != ''
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "rule",
                "risk_type": "duplication",
                "risk_description": f"Rule '{row['id']}' duplicates logic already implemented in '{row['duplicate_of']}'",
                "severity": "medium",
                "remediation": "Consolidate duplicated business logic into a single source of truth"
            })
        
        # Risk: PII exposure in data stores
        cursor.execute("""
            SELECT id, name FROM data_stores WHERE pii_data = 'Y'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "data_store",
                "risk_type": "security",
                "risk_description": f"Data store '{row['name']}' contains PII — ensure encryption and access controls",
                "severity": "critical",
                "remediation": "Implement data masking, encryption at rest, and RBAC"
            })
        
        # Risk: Unmapped data store (owned by a non-existent application)
        cursor.execute("SELECT * FROM data_stores")
        for row in cursor.fetchall():
            if row['application_id'] and row['application_id'] not in app_ids:
                risk_id += 1
                risks.append({
                    "id": f"risk_{risk_id}",
                    "entity_id": row['id'],
                    "entity_type": "data_store",
                    "risk_type": "orphan_dependency",
                    "risk_description": f"Data store '{row['name']}' is owned by non-existent application '{row['application_id']}'",
                    "severity": "high",
                    "remediation": "Reassign ownership or retire the data store"
                })
        
        # Risk: Parity mismatches between legacy and expected behavior
        cursor.execute("""
            SELECT id, test_name, module_id FROM test_cases WHERE status = 'mismatch'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "test_case",
                "risk_type": "parity_mismatch",
                "risk_description": f"Test '{row['test_name']}' shows a parity mismatch for module '{row['module_id']}' — behavior gap to preserve",
                "severity": "high",
                "remediation": "Investigate legacy vs. expected behavior before cutover"
            })
        
        # Risk: Modernization breaks continuity
        cursor.execute("""
            SELECT id, recommendation FROM modernization_backlog
            WHERE preserves_continuity = 'N'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "backlog_item",
                "risk_type": "continuity",
                "risk_description": f"Backlog item '{row['id']}' ({row['recommendation']}) does not preserve continuity",
                "severity": "high",
                "remediation": "Add a parity validation step before approving this change"
            })
        
        return risks
    
    def build_trace_chain(self, workbook_id: str, finding_id: str, finding_type: str) -> List[Dict[str, Any]]:
        """
        Build complete trace chain: Finding -> Owning Entity -> Related Records -> Source Sheet/Row
        """
        from app.services.xlsx_ingestion import XLSXIngestionService
        
        svc = XLSXIngestionService()
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        trace: List[Dict[str, Any]] = []
        
        def source_step(step_no: int, row: Dict) -> Dict:
            return {
                "step": step_no,
                "type": "Source Record",
                "name": f"{row.get('source_sheet')} · row {row.get('source_row')}",
                "details": f"trace_id: {row.get('trace_id')}"
            }
        
        if finding_type == "application":
            cursor.execute("SELECT * FROM applications WHERE id = ?", (finding_id,))
            app = cursor.fetchone()
            if not app:
                return []
            app = dict(app)
            cursor.execute("SELECT * FROM code_modules WHERE application_id = ?", (finding_id,))
            modules = [dict(r) for r in cursor.fetchall()]
            module_ids = [m['id'] for m in modules]
            rules = []
            if module_ids:
                placeholders = ','.join('?' * len(module_ids))
                cursor.execute(f"SELECT * FROM business_rules WHERE module_id IN ({placeholders})", module_ids)
                rules = [dict(r) for r in cursor.fetchall()]
            
            trace = [
                {"step": 1, "type": "Application", "name": app.get('name'),
                 "details": f"Criticality: {app.get('criticality')} · Platform: {app.get('platform')} · Owner: {app.get('owner')}"},
                {"step": 2, "type": "Code Modules", "name": f"{len(modules)} modules",
                 "details": ", ".join(m['name'] for m in modules[:8]) or "No modules found"},
                {"step": 3, "type": "Business Rules", "name": f"{len(rules)} rules",
                 "details": ", ".join(r['rule_name'] for r in rules[:5]) or "No rules found"},
                source_step(4, app)
            ]
        
        elif finding_type == "module":
            cursor.execute("SELECT * FROM code_modules WHERE id = ?", (finding_id,))
            module = cursor.fetchone()
            if not module:
                return []
            module = dict(module)
            cursor.execute("SELECT * FROM applications WHERE id = ?", (module.get('application_id'),))
            app = cursor.fetchone()
            app = dict(app) if app else None
            cursor.execute("SELECT * FROM business_rules WHERE module_id = ?", (finding_id,))
            rules = [dict(r) for r in cursor.fetchall()]
            cursor.execute("SELECT * FROM dependencies WHERE source_id = ? OR target_id = ?", (finding_id, finding_id))
            deps = [dict(r) for r in cursor.fetchall()]
            
            trace = [
                {"step": 1, "type": "Code Module", "name": module.get('name'),
                 "details": f"Type: {module.get('module_type')} · Complexity: {module.get('complexity_score')} · "
                            f"Unit Tests: {module.get('has_unit_tests')} · Dead Code: {module.get('is_dead_code')}"},
                {"step": 2, "type": "Owning Application", "name": app.get('name') if app else 'Unknown',
                 "details": f"Criticality: {app.get('criticality')}" if app else ""},
                {"step": 3, "type": "Business Rules", "name": f"{len(rules)} rules",
                 "details": ", ".join(r['rule_name'] for r in rules[:5]) or "No rules found"},
                {"step": 4, "type": "Dependencies", "name": f"{len(deps)} edges",
                 "details": ", ".join(f"{d['source_id']}→{d['target_id']}" for d in deps[:5]) or "No dependencies found"},
                source_step(5, module)
            ]
        
        elif finding_type == "rule":
            cursor.execute("SELECT * FROM business_rules WHERE id = ?", (finding_id,))
            rule = cursor.fetchone()
            if not rule:
                return []
            rule = dict(rule)
            cursor.execute("SELECT * FROM code_modules WHERE id = ?", (rule.get('module_id'),))
            module = cursor.fetchone()
            module = dict(module) if module else None
            app = None
            if module:
                cursor.execute("SELECT * FROM applications WHERE id = ?", (module.get('application_id'),))
                app_row = cursor.fetchone()
                app = dict(app_row) if app_row else None
            cursor.execute("SELECT * FROM test_cases WHERE rule_id = ?", (finding_id,))
            tests = [dict(r) for r in cursor.fetchall()]
            
            trace = [
                {"step": 1, "type": "Business Rule", "name": rule.get('rule_name'),
                 "details": f"Domain: {rule.get('business_domain')} · Criticality: {rule.get('criticality')} · "
                            f"Has Test Case: {rule.get('has_test_case')}"},
                {"step": 2, "type": "Implementing Module", "name": module.get('name') if module else 'Unknown',
                 "details": f"Type: {module.get('module_type')}" if module else ""},
                {"step": 3, "type": "Owning Application", "name": app.get('name') if app else 'Unknown', "details": ""},
                {"step": 4, "type": "Test Cases", "name": f"{len(tests)} tests",
                 "details": ", ".join(t['test_name'] for t in tests[:5]) or "No test cases found"},
                source_step(5, rule)
            ]
        
        elif finding_type == "dependency":
            cursor.execute("SELECT * FROM dependencies WHERE id = ?", (finding_id,))
            dep = cursor.fetchone()
            if not dep:
                return []
            dep = dict(dep)
            
            trace = [
                {"step": 1, "type": "Dependency", "name": f"{dep.get('source_id')} → {dep.get('target_id')}",
                 "details": f"Kind: {dep.get('relationship_type')} · Criticality: {dep.get('criticality')} · "
                            f"Target Type: {dep.get('target_type')}"},
                source_step(2, dep)
            ]
        
        elif finding_type == "risk":
            # Risks are computed on-the-fly (not persisted), so re-derive and locate by id
            risks = self.identify_risks(workbook_id)
            finding = next((r for r in risks if r['id'] == finding_id), None)
            if finding:
                trace = [{"step": 1, "level": "finding", "type": finding_type, "data": finding}]
        
        elif finding_type == "recommendation":
            cursor.execute("SELECT * FROM modernization_backlog WHERE id = ?", (finding_id,))
            finding = cursor.fetchone()
            if finding:
                trace = [{"step": 1, "level": "finding", "type": finding_type, "data": dict(finding)}]
        
        return trace


class AgentOrchestrator:
    """
    Orchestrates 6 specialized AI agents:
    1. Legacy Archaeologist
    2. Documentation Architect
    3. Dependency Detective
    4. Parity Engineer
    5. Modernization Strategist
    6. Security & Continuity Guardian
    """
    
    def __init__(self):
        pass
    
    def legacy_archaeologist_analyze(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """
        Deep analysis of applications, modules, business logic.
        Returns: (findings, evidence)
        """
        from app.services.xlsx_ingestion import XLSXIngestionService
        svc = XLSXIngestionService()
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        app_id = context.get('application_id')
        
        cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,)) if app_id else cursor.execute("SELECT * FROM applications LIMIT 1")
        app_row = cursor.fetchone()
        app = dict(app_row) if app_row else None
        
        if not app:
            return {}, {"evidence_list": [], "confidence": 0, "trace": []}
        
        cursor.execute("SELECT * FROM code_modules WHERE application_id = ?", (app['id'],))
        modules = [dict(row) for row in cursor.fetchall()]
        
        module_ids = [m['id'] for m in modules]
        rules: List[Dict] = []
        if module_ids:
            placeholders = ','.join('?' * len(module_ids))
            cursor.execute(f"SELECT * FROM business_rules WHERE module_id IN ({placeholders})", module_ids)
            rules = [dict(row) for row in cursor.fetchall()]
        
        # Deterministic grounding facts (never shown directly - only fed to the LLM
        # so it cannot invent ids/numbers not present in the real data). Only the
        # critical/hotspot subsets are sent (not every module/rule) to keep the
        # prompt small and the response fast.
        facts = {
            "application": {"name": app.get('name'), "primary_language": app.get('primary_language'), "platform": app.get('platform'), "criticality": app.get('criticality')},
            "module_count": len(modules),
            "rule_count": len(rules),
            "total_lines_of_code": sum(m.get('lines_of_code') or 0 for m in modules),
            "average_module_complexity": sum(m.get('complexity_score') or 0 for m in modules) / len(modules) if modules else 0,
            "critical_modules": [m for m in modules if (m.get('complexity_score') or 0) > 25],
            "critical_rules": [r for r in rules if str(r.get('criticality')).lower() == 'high'],
            "complexity_hotspots": [m for m in modules if (m.get('complexity_score') or 0) >= 38],
        }

        schema_hint = (
            '{"architecture_summary": str, "business_logic_summary": str, '
            '"critical_module_notes": [{"id": str, "text": str}], '
            '"critical_rule_notes": [{"id": str, "text": str}], '
            '"hotspot_notes": [{"id": str, "text": str}], "ai_narrative": str}'
        )
        ai_result = llm_service.generate_structured(
            "Legacy Archaeologist",
            "Analyze this application's architecture and business logic complexity from FACTS. "
            "Write architecture_summary (1 sentence) and business_logic_summary (1 sentence). "
            "For each id in FACTS.critical_modules, FACTS.critical_rules, and "
            "FACTS.complexity_hotspots, add a short (<=15 word) note explaining why it matters "
            "in the matching *_notes list (id = that item's real id). Only use ids present in FACTS.",
            facts,
            schema_hint,
            max_tokens=900,
        )

        if ai_result:
            findings = {
                "application": dict(app),
                "module_count": len(modules),
                "rule_count": len(rules),
                "architecture": {
                    "technology_stack": app.get('primary_language'),
                    "platform": app.get('platform'),
                    "total_lines_of_code": facts["total_lines_of_code"],
                    "average_module_complexity": facts["average_module_complexity"],
                    "summary": ai_result.get("architecture_summary", ""),
                },
                "critical_modules": _merge_ai_notes(facts["critical_modules"], ai_result.get("critical_module_notes"), lambda m: m.get('id'), "ai_reason"),
                "business_logic": {
                    "critical_rules": _merge_ai_notes(facts["critical_rules"], ai_result.get("critical_rule_notes"), lambda r: r.get('id'), "ai_reason"),
                    "total_rules": len(rules),
                    "summary": ai_result.get("business_logic_summary", ""),
                },
                "complexity_hotspots": _merge_ai_notes(facts["complexity_hotspots"], ai_result.get("hotspot_notes"), lambda m: m.get('id'), "ai_reason"),
                "confidence": 0.85,
                "ai_narrative": ai_result.get("ai_narrative"),
                "ai_generated": True,
            }
        else:
            findings = {
                "application": dict(app),
                "module_count": len(modules),
                "rule_count": len(rules),
                "architecture": {
                    "technology_stack": app.get('primary_language'),
                    "platform": app.get('platform'),
                    "total_lines_of_code": facts["total_lines_of_code"],
                    "average_module_complexity": facts["average_module_complexity"]
                },
                "critical_modules": facts["critical_modules"],
                "business_logic": {
                    "critical_rules": facts["critical_rules"],
                    "total_rules": len(rules)
                },
                "complexity_hotspots": facts["complexity_hotspots"],
                "confidence": 0.85,
                "ai_narrative": None,
                "ai_generated": False,
                "ai_fallback_reason": "AI provider unavailable — showing deterministic fallback data, not AI-generated.",
            }
        
        evidence = {
            "evidence_list": [
                {"source_sheet": app.get('source_sheet'), "source_row": app.get('source_row'), "type": "application"},
                {"source_sheet": "Code_Modules", "record_count": len(modules), "type": "modules"},
                {"source_sheet": "Business_Rules", "record_count": len(rules), "type": "rules"}
            ],
            "confidence": 0.85,
            "trace": [
                {"step": 1, "entity": "Application", "id": app['id']},
                {"step": 2, "entity": "Modules", "count": len(modules)},
                {"step": 3, "entity": "Business Rules", "count": len(rules)}
            ]
        }
        
        return findings, evidence
    
    def documentation_architect_generate(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """Generate documentation artifacts with traceability"""
        from app.services.xlsx_ingestion import XLSXIngestionService
        svc = XLSXIngestionService()
        
        app_id = context.get('application_id')
        doc_type = context.get('doc_type', 'functional_specification')
        
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,)) if app_id else cursor.execute("SELECT * FROM applications LIMIT 1")
        app_row = cursor.fetchone()
        app = dict(app_row) if app_row else None
        
        if not app:
            return {}, {"evidence_list": [], "confidence": 0, "trace": []}
        
        cursor.execute("SELECT * FROM code_modules WHERE application_id = ?", (app['id'],))
        modules = [dict(row) for row in cursor.fetchall()]
        
        module_ids = [m['id'] for m in modules]
        rules: List[Dict] = []
        if module_ids:
            placeholders = ','.join('?' * len(module_ids))
            cursor.execute(f"SELECT * FROM business_rules WHERE module_id IN ({placeholders})", module_ids)
            rules = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM integrations WHERE application_id = ?", (app['id'],))
        integrations = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute(
            "SELECT * FROM dependencies WHERE source_id = ? OR target_id = ?",
            (app['id'], app['id'])
        )
        app_deps = [dict(row) for row in cursor.fetchall()]
        if module_ids:
            placeholders = ','.join('?' * len(module_ids))
            cursor.execute(f"SELECT * FROM dependencies WHERE source_id IN ({placeholders})", module_ids)
            app_deps += [dict(row) for row in cursor.fetchall()]
        
        findings = {
            "document_type": doc_type,
            "status": "draft",
            "application": app,
            "sections": []
        }
        
        evidence_list = [
            {"source_sheet": "Applications", "source_row": app.get('source_row'), "field": "app_name"},
            {"source_sheet": "Applications", "source_row": app.get('source_row'), "field": "business_domain"},
            {"source_sheet": "Applications", "source_row": app.get('source_row'), "field": "primary_language"}
        ]
        
        if doc_type == "api_specification":
            endpoints = []
            for integ in integrations:
                endpoints.append({
                    "id": integ.get('id'),
                    "interface_name": integ.get('interface_name'),
                    "protocol": integ.get('protocol'),
                    "direction": integ.get('direction'),
                    "downstream_target": integ.get('downstream_target'),
                    "status": integ.get('status'),
                    "last_verified": integ.get('last_verified')
                })
            
            data_flow_lines = []
            for dep in app_deps:
                data_flow_lines.append(
                    f"{dep.get('source_id')} -> {dep.get('target_id')} ({dep.get('relationship_type')}, {dep.get('criticality')})"
                )
            
            def build_fallback_sections():
                return [
                    {
                        "title": "1. API Overview",
                        "content": f"Application: {app.get('name')}\nTotal Integrations: {len(integrations)}\nPrimary Language: {app.get('primary_language')}"
                    },
                    {
                        "title": "2. Integration Endpoints",
                        "content": "\n".join(
                            f"- [{e['id']}] {e['interface_name']} ({e['direction']}) via {e['protocol']} -> {e['downstream_target']} "
                            f"(status: {e['status']}, last verified: {e['last_verified']})"
                            for e in endpoints
                        ) or "No integrations found for this application",
                        "requires_review": len(endpoints) == 0
                    },
                    {
                        "title": "3. Data Flows & Dependencies",
                        "content": "\n".join(data_flow_lines) or "No cross-system dependencies recorded",
                        "requires_review": len(data_flow_lines) == 0
                    },
                    {
                        "title": "4. Inactive / At-Risk Endpoints",
                        "content": "\n".join(
                            f"- {e['id']} ({e['interface_name']}) is {e['status']}"
                            for e in endpoints if str(e['status']).lower() not in ('active',)
                        ) or "No inactive endpoints detected",
                    }
                ]
            
            facts = {
                "application": app, "endpoints": endpoints[:20], "data_flow_lines": data_flow_lines[:20],
                "integration_count": len(integrations), "dependency_count": len(app_deps),
            }
            schema_hint = (
                '{"sections": [{"title": "1. API Overview", "content": str}, '
                '{"title": "2. Integration Endpoints", "content": str, "requires_review": bool}, '
                '{"title": "3. Data Flows & Dependencies", "content": str, "requires_review": bool}, '
                '{"title": "4. Inactive / At-Risk Endpoints", "content": str}], "ai_narrative": str}'
            )
            ai_result = llm_service.generate_structured(
                "Documentation Architect",
                "Write the API specification document for this application from FACTS. Each "
                "section's 'content' is 2-4 sentences of authored prose (not a line-by-line list) "
                "summarizing the endpoints/data flows/at-risk items — mention a few representative "
                "ids/names from FACTS, not every single one if there are many. Flag "
                "requires_review=true where data is thin or something needs sign-off.",
                facts, schema_hint, max_tokens=1200,
            )
            
            evidence_list += [
                {"source_sheet": "Integrations", "record_count": len(integrations), "type": "endpoints"},
                {"source_sheet": "Dependencies", "record_count": len(app_deps), "type": "data_flows"}
            ]
        
        else:  # functional_specification
            critical_rules = [r for r in rules if str(r.get('criticality')).lower() == 'high']
            
            def build_fallback_sections():
                return [
                    {
                        "title": "1. Overview",
                        "content": f"System: {app.get('name')}\nPrimary Language: {app.get('primary_language')}\nPlatform: {app.get('platform')}"
                    },
                    {
                        "title": "2. Business Context",
                        "content": f"Domain: {app.get('business_domain')}\nOwner: {app.get('owner') or 'Unknown'}\n"
                                   f"Annual Maintenance Cost: €{app.get('annual_maint_cost_eur') or 0:,.0f}",
                    },
                    {
                        "title": "3. Architecture",
                        "content": f"Criticality: {app.get('criticality')}\nDoc Coverage: {app.get('doc_coverage_pct')}%\n"
                                   f"Modules: {len(modules)}\nTotal LOC: {sum(m.get('lines_of_code') or 0 for m in modules)}",
                        "requires_review": (app.get('doc_coverage_pct') or 0) < 30
                    },
                    {
                        "title": "4. Business Rules",
                        "content": "\n".join(
                            f"- [{r['id']}] {r.get('rule_name')} (domain: {r.get('business_domain')}, criticality: {r.get('criticality')})"
                            for r in rules
                        ) or "No business rules found for this application",
                        "requires_review": len(rules) == 0
                    },
                    {
                        "title": "5. Critical Rules Requiring Sign-off",
                        "content": "\n".join(
                            f"- [{r['id']}] {r.get('rule_name')}" for r in critical_rules
                        ) or "No critical rules identified",
                        "requires_review": len(critical_rules) > 0
                    },
                    {
                        "title": "6. Code Modules",
                        "content": "\n".join(
                            f"- [{m['id']}] {m.get('name')} ({m.get('module_type')}, complexity {m.get('complexity_score')}, "
                            f"unit tests: {m.get('has_unit_tests')}, dead code: {m.get('is_dead_code')})"
                            for m in modules
                        ) or "No modules found for this application",
                    }
                ]
            
            facts = {
                "application": app, "modules": modules[:20], "rules": rules[:20], "critical_rules": critical_rules[:20],
                "module_count": len(modules), "rule_count": len(rules), "critical_rule_count": len(critical_rules),
            }
            schema_hint = (
                '{"sections": [{"title": "1. Overview", "content": str}, '
                '{"title": "2. Business Context", "content": str}, '
                '{"title": "3. Architecture", "content": str, "requires_review": bool}, '
                '{"title": "4. Business Rules", "content": str, "requires_review": bool}, '
                '{"title": "5. Critical Rules Requiring Sign-off", "content": str, "requires_review": bool}, '
                '{"title": "6. Code Modules", "content": str}], "ai_narrative": str}'
            )
            ai_result = llm_service.generate_structured(
                "Documentation Architect",
                "Write the functional specification document for this application from FACTS. Each "
                "section's 'content' is 2-4 sentences of authored prose (not a line-by-line list) "
                "covering the overview, business context, architecture, business rules, critical "
                "rules needing sign-off, and code modules — mention a few representative ids/names "
                "from FACTS, not every single one if there are many. Flag requires_review=true where "
                "data is thin or something needs sign-off.",
                facts, schema_hint, max_tokens=1200,
            )
            
            evidence_list += [
                {"source_sheet": "Code_Modules", "record_count": len(modules), "type": "modules"},
                {"source_sheet": "Business_Rules", "record_count": len(rules), "type": "rules"}
            ]
        
        if ai_result and ai_result.get("sections"):
            findings['sections'] = ai_result["sections"]
            findings["ai_narrative"] = ai_result.get("ai_narrative")
            findings["ai_generated"] = True
        else:
            findings['sections'] = build_fallback_sections()
            findings["ai_narrative"] = None
            findings["ai_generated"] = False
            findings["ai_fallback_reason"] = "AI provider unavailable — showing deterministic fallback content, not AI-generated."
        
        evidence = {
            "evidence_list": evidence_list,
            "confidence": 0.75,
            "trace": [
                {"level": "document", "type": doc_type},
                {"level": "entity", "type": "application", "id": app['id']},
                {"level": "source", "sheet": "Applications", "row": app.get('source_row')}
            ]
        }
        
        return findings, evidence
    
    def dependency_detective_analyze(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """Analyze dependencies and detect orphans/cycles"""
        analysis_engine = AnalysisEngine()
        graph = analysis_engine.build_dependency_graph(workbook_id)

        facts = {
            "orphans": graph.get('orphan_nodes', []),
            "cycles": graph.get('cycles', []),
            "statistics": graph.get('statistics', {}),
        }
        schema_hint = (
            '{"orphan_analysis": str, "cycle_analysis": str, '
            '"risk_summary": str, "ai_narrative": str}'
        )
        ai_result = llm_service.generate_structured(
            "Dependency Detective",
            "Analyze this dependency graph's health from FACTS: explain what the orphaned "
            "components and circular dependencies mean for modernization risk. Reference the "
            "real counts/ids given, don't invent new ones.",
            facts, schema_hint, max_tokens=500,
        )

        findings = {
            "graph": graph,
            "orphans": facts["orphans"],
            "cycles": facts["cycles"],
            "statistics": facts["statistics"],
        }
        if ai_result:
            findings["orphan_analysis"] = ai_result.get("orphan_analysis")
            findings["cycle_analysis"] = ai_result.get("cycle_analysis")
            findings["risk_summary"] = ai_result.get("risk_summary")
            findings["ai_narrative"] = ai_result.get("ai_narrative")
            findings["ai_generated"] = True
        else:
            findings["ai_narrative"] = None
            findings["ai_generated"] = False
            findings["ai_fallback_reason"] = "AI provider unavailable — showing deterministic fallback data, not AI-generated."
        
        evidence = {
            "evidence_list": [
                {"source_sheet": "Dependencies", "type": "edges", "count": len(graph['edges'])}
            ],
            "confidence": 0.9,
            "trace": [
                {"step": 1, "analysis": "graph_construction"},
                {"step": 2, "analysis": "orphan_detection"},
                {"step": 3, "analysis": "cycle_detection"}
            ]
        }
        
        return findings, evidence
    
    def _synthesize_test_cases(self, workbook_id: str, cursor, rules: List[Dict], svc) -> List[Dict]:
        """
        Parity Validator agent: auto-generate real test scenarios for business
        rules that don't have one yet (e.g. every rule extracted straight from
        a COBOL ingestion - see cobol_ingestion.py, which seeds has_test_case='N'
        and zero test_cases rows by design). Grounds each scenario in the real
        COBOL paragraph body when available so expected outputs reflect actual
        conditional logic instead of invented behavior. Persists results so
        they survive across page loads, and marks the rule has_test_case='Y'.
        """
        from app.services.cobol_ingestion import get_cobol_source
        from app.services.cobol_parser import parse_cobol_source

        cursor.execute("SELECT id, name FROM code_modules")
        module_names = {row['id']: row['name'] for row in cursor.fetchall()}

        # Ground generation in the real paragraph body for COBOL-sourced
        # workbooks; XLSX-sourced rules fall back to rule name/domain only.
        paragraph_bodies: Dict[str, str] = {}
        source, filename = get_cobol_source(workbook_id, svc.cache_dir)
        if source:
            facts = parse_cobol_source(source, filename)
            for p in facts.get("paragraph_details", []):
                paragraph_bodies[p["name"]] = p.get("body", "")

        needing_tests = [r for r in rules if str(r.get('has_test_case') or '').upper() != 'Y']
        if not needing_tests:
            return []

        ai_facts = {
            "rules": [
                {
                    "rule_id": r['id'],
                    "rule_name": r.get('rule_name'),
                    "criticality": r.get('criticality'),
                    "paragraph_body": paragraph_bodies.get(module_names.get(r.get('module_id')), '')[:800],
                }
                for r in needing_tests
            ]
        }
        schema_hint = (
            '{"tests": [{"rule_id": str, "test_name": str, '
            '"test_type": str ("unit"|"regression"|"boundary"), '
            '"input_data": str, "expected_output": str}]} '
            '(one entry per FACTS.rules item)'
        )
        ai_result = llm_service.generate_structured(
            "Parity Validator",
            "For each rule in FACTS.rules, design one concrete parity test scenario that proves "
            "the modernized code preserves the exact conditional logic in paragraph_body. Give a "
            "realistic input_data and the expected_output implied by that logic - do not invent "
            "fields or conditions not present in paragraph_body. If paragraph_body is empty, base "
            "the scenario on rule_name and criticality instead.",
            ai_facts, schema_hint, max_tokens=900,
        )

        ai_tests_by_rule: Dict[str, Dict] = {}
        if ai_result and isinstance(ai_result.get("tests"), list):
            for t in ai_result["tests"]:
                if isinstance(t, dict) and t.get("rule_id") not in (None, ""):
                    ai_tests_by_rule[str(t["rule_id"])] = t

        generated: List[Dict] = []
        for idx, r in enumerate(needing_tests, start=1):
            test_id = f"TC-{idx:03d}-{r['id']}"
            ai_test = ai_tests_by_rule.get(str(r['id']))
            if ai_test:
                test_name = ai_test.get("test_name") or f"Verify {r.get('rule_name')}"
                test_type = ai_test.get("test_type") or "unit"
                input_data = ai_test.get("input_data") or "N/A"
                expected_output = ai_test.get("expected_output") or "N/A"
            else:
                test_name = f"Verify {r.get('rule_name') or r['id']}"
                test_type = "unit"
                input_data = "AI provider unavailable - define manually"
                expected_output = "AI provider unavailable - define manually"
            cursor.execute(
                """INSERT INTO test_cases
                   (id, rule_id, module_id, test_name, test_type, expected_output,
                    legacy_result, status, last_run, source_sheet, source_row, trace_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    test_id, r['id'], r.get('module_id'), test_name, test_type,
                    f"Input: {input_data} -> Expected: {expected_output}",
                    None, "pending", None,
                    r.get('source_sheet'), r.get('source_row'), str(uuid.uuid4())[:12],
                ),
            )
            cursor.execute("UPDATE business_rules SET has_test_case = 'Y' WHERE id = ?", (r['id'],))
            generated.append({
                "id": test_id, "rule_id": r['id'], "module_id": r.get('module_id'),
                "test_name": test_name, "test_type": test_type,
                "expected_output": f"Input: {input_data} -> Expected: {expected_output}",
                "legacy_result": None, "status": "pending",
            })
        return generated

    def parity_engineer_generate(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """Generate parity tests from business rules and test cases"""
        from app.services.xlsx_ingestion import XLSXIngestionService
        svc = XLSXIngestionService()
        
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fetch test cases
        cursor.execute("SELECT * FROM test_cases")
        test_cases = [dict(row) for row in cursor.fetchall()]
        
        # Fetch business rules for context
        cursor.execute("SELECT * FROM business_rules")
        rules = [dict(row) for row in cursor.fetchall()]
        
        # COBOL-sourced workbooks (and any rule extracted without a matching
        # test) start with zero test_cases by design - see cobol_ingestion.py.
        # The Parity Validator agent synthesizes real, logic-grounded scenarios
        # now instead of the UI falling back to generic placeholder rows.
        if not test_cases and rules:
            test_cases = self._synthesize_test_cases(workbook_id, cursor, rules, svc)
            conn.commit()
        
        # Normalize raw source statuses (e.g. "Passed"/"Failed") to a small set
        # of parity outcomes used by the UI for coloring/aggregation
        status_map = {
            "passed": "pass", "pass": "pass",
            "failed": "fail", "fail": "fail",
            "mismatch": "mismatch",
            "pending": "pending", "not run": "pending", "not_run": "pending"
        }
        
        tests = []
        for idx, test in enumerate(test_cases):
            # Find the rule for this test
            rule = next((r for r in rules if r['id'] == test.get('rule_id')), None)
            
            raw_status = (test.get('status') or 'pending')
            parity_status = status_map.get(str(raw_status).strip().lower(), 'pending')
            
            tests.append({
                "test_id": test.get('id') or f"test_{idx}",
                "test_name": test.get('test_name') or f"Test_{idx}",
                "rule_id": test.get('rule_id') or 'N/A',
                "module_id": test.get('module_id') or 'N/A',
                "description": test.get('description') or (rule.get('rule_name') if rule else 'No description'),
                "input_data": test.get('input_data') or 'N/A',
                "expected_output": test.get('expected_output') or 'N/A',
                "test_type": test.get('test_type') or 'unit',
                "status": parity_status,
                "legacy_result": test.get('legacy_result') or raw_status,
                "modern_result": test.get('expected_output') or raw_status,
                "parity_status": parity_status
            })
        
        passed = sum(1 for t in tests if t['status'] == 'pass')
        failed = sum(1 for t in tests if t['status'] == 'fail')
        # Only tests that aren't clean passes need an AI risk note - sending just
        # those (not all tests) keeps both the prompt and the response small/fast
        non_passing = [t for t in tests if t['status'] in ('mismatch', 'fail')]
        facts = {
            "total_tests": len(tests), "passed": passed, "failed": failed,
            "non_passing_tests": non_passing,
        }
        schema_hint = (
            '{"notes": [{"id": str, "text": str}] (one entry per item in FACTS.non_passing_tests, '
            'id = that test\'s test_id, text = a <=20 word risk note), "ai_narrative": str}'
        )
        ai_result = llm_service.generate_structured(
            "Parity Engineer",
            "For each test in FACTS.non_passing_tests, write a short risk note explaining the "
            "behavioral risk of that mismatch/failure. Then write ai_narrative: overall pass rate "
            "and the biggest behavioral risks to preserve during modernization.",
            facts, schema_hint, max_tokens=700,
        )
        
        if ai_result:
            tests_with_notes = _merge_ai_notes(tests, ai_result.get("notes"), lambda t: t.get('test_id'), "ai_risk_note")
            findings = {
                "total_tests": len(tests), "passed": passed, "failed": failed,
                "tests": tests_with_notes, "ai_narrative": ai_result.get("ai_narrative"), "ai_generated": True,
            }
        else:
            findings = {
                "total_tests": len(tests), "passed": passed, "failed": failed,
                "tests": tests, "ai_narrative": None, "ai_generated": False,
                "ai_fallback_reason": "AI provider unavailable — showing deterministic fallback data, not AI-generated.",
            }
        
        evidence = {
            "evidence_list": [
                {"source_sheet": "Test_Cases", "record_count": len(test_cases), "type": "tests"},
                {"source_sheet": "Business_Rules", "record_count": len(rules), "type": "rules"}
            ],
            "confidence": 0.85,
            "trace": [
                {"level": "generation", "type": "parity_tests"},
                {"level": "source", "sheet": "Test_Cases", "records": len(test_cases)}
            ]
        }
        
        return findings, evidence
    
    def modernization_strategist_recommend(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """Generate modernization recommendations from backlog"""
        from app.services.xlsx_ingestion import XLSXIngestionService
        svc = XLSXIngestionService()
        analysis = AnalysisEngine()
        
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fetch modernization backlog recommendations
        cursor.execute("SELECT * FROM modernization_backlog")
        backlog_items = [dict(row) for row in cursor.fetchall()]
        
        # Fetch risks for context
        risks = analysis.identify_risks(workbook_id)
        
        recommendations = []
        # Backlog priority values are P1 (highest) .. P4 (lowest)
        priority_map = {"p1": 4, "p2": 3, "p3": 2, "p4": 1}
        
        for idx, item in enumerate(backlog_items):
            priority = item.get('priority') or 'P3'
            priority_num = priority_map.get(str(priority).lower(), 2)
            
            recommendations.append({
                "id": item.get('id') or f"rec_{idx+1}",
                "recommendation": item.get('recommendation') or 'Modernization recommendation',
                "priority": priority,
                "priority_level": priority_num,
                "application_id": item.get('application_id'),
                "module_id": item.get('module_id'),
                "effort_estimate": item.get('effort_estimate') or 'unknown',
                "risk_level": item.get('risk_level') or 'medium',
                "target_tech": item.get('target_tech'),
                "preserves_continuity": item.get('preserves_continuity'),
                "status": item.get('status') or 'draft',
                "strategy": f"Migrate to {item.get('target_tech')}" if item.get('target_tech') else 'Modernize',
                "effort": item.get('effort_estimate') or 'medium'
            })
        
        statistics = {
            "total_risks": len(risks),
            "critical_risks": len([r for r in risks if r['severity'] == 'critical']),
            "high_risks": len([r for r in risks if r['severity'] == 'high']),
            "modernization_items": len(backlog_items)
        }
        facts = {"recommendations": [{"id": r["id"], "recommendation": r["recommendation"], "priority": r["priority"], "risk_level": r["risk_level"], "target_tech": r["target_tech"], "preserves_continuity": r["preserves_continuity"]} for r in recommendations], "statistics": statistics}
        schema_hint = (
            '{"notes": [{"id": str, "text": str}] (one entry per item in FACTS.recommendations, '
            'text = a <=15 word AI-authored strategy rationale grounded in its risk_level/target_tech/'
            'preserves_continuity), "ai_narrative": str}'
        )
        ai_result = llm_service.generate_structured(
            "Modernization Strategist",
            "For each recommendation in FACTS.recommendations, write a short one-sentence strategy "
            "rationale (why/how to modernize it) keyed by its id. Then write ai_narrative: an "
            "executive summary of what to prioritize first and why.",
            facts, schema_hint, max_tokens=1200,
        )
        
        if ai_result:
            recs_with_strategy = _merge_ai_notes(recommendations, ai_result.get("notes"), lambda r: r.get('id'), "strategy", keep_original_if_missing=True)
            findings = {
                "recommendations": recs_with_strategy,
                "roadmap": ["Protect", "Understand", "Isolate", "Migrate", "Retire"],
                "total_recommendations": len(recommendations),
                "statistics": statistics,
                "ai_narrative": ai_result.get("ai_narrative"),
                "ai_generated": True,
            }
        else:
            findings = {
                "recommendations": recommendations,
                "roadmap": ["Protect", "Understand", "Isolate", "Migrate", "Retire"],
                "total_recommendations": len(recommendations),
                "statistics": statistics,
                "ai_narrative": None,
                "ai_generated": False,
                "ai_fallback_reason": "AI provider unavailable — showing deterministic fallback data, not AI-generated.",
            }
        
        evidence = {
            "evidence_list": [
                {"source_sheet": "Modernization_Backlog", "record_count": len(backlog_items), "type": "backlog_items"},
                {"type": "risk_analysis", "count": len(risks)}
            ],
            "confidence": 0.75,
            "trace": [
                {"level": "analysis", "type": "risk_identification"},
                {"level": "synthesis", "type": "recommendation_generation"}
            ]
        }
        
        return findings, evidence
    
    def security_continuity_guardian_detect(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """Detect security and continuity risks"""
        analysis = AnalysisEngine()
        risks = analysis.identify_risks(workbook_id)
        
        security_risks = [r for r in risks if r['risk_type'] == 'security']
        continuity_risks = [r for r in risks if r['risk_type'] == 'continuity']

        facts = {
            "security_risks": [{"id": r["id"], "risk_description": r["risk_description"], "severity": r["severity"]} for r in security_risks],
            "continuity_risks": [{"id": r["id"], "risk_description": r["risk_description"], "severity": r["severity"]} for r in continuity_risks],
        }
        schema_hint = (
            '{"security_notes": [{"id": str, "text": str}] (one per item in FACTS.security_risks, '
            '<=15 word priority note), '
            '"continuity_notes": [{"id": str, "text": str}] (one per item in FACTS.continuity_risks, '
            '<=15 word priority note), "summary": str, "ai_narrative": str}'
        )
        ai_result = llm_service.generate_structured(
            "Security & Continuity Guardian",
            "For each risk in FACTS.security_risks and FACTS.continuity_risks, write a short "
            "priority note (why it's urgent), keyed by id. Then write 'summary' (one line) and "
            "'ai_narrative': what's most urgent to fix before modernization.",
            facts, schema_hint, max_tokens=900,
        )
        
        if ai_result:
            security_with_notes = _merge_ai_notes(security_risks, ai_result.get("security_notes"), lambda r: r.get('id'), "ai_priority_note")
            continuity_with_notes = _merge_ai_notes(continuity_risks, ai_result.get("continuity_notes"), lambda r: r.get('id'), "ai_priority_note")
            findings = {
                "security_risks": security_with_notes,
                "continuity_risks": continuity_with_notes,
                "total_risks": len(risks),
                "summary": ai_result.get("summary") or f"Found {len(security_risks)} security issues and {len(continuity_risks)} continuity issues",
                "ai_narrative": ai_result.get("ai_narrative"),
                "ai_generated": True,
            }
        else:
            findings = {
                "security_risks": security_risks,
                "continuity_risks": continuity_risks,
                "total_risks": len(risks),
                "summary": f"Found {len(security_risks)} security issues and {len(continuity_risks)} continuity issues",
                "ai_narrative": None,
                "ai_generated": False,
                "ai_fallback_reason": "AI provider unavailable — showing deterministic fallback data, not AI-generated.",
            }
        
        evidence = {
            "evidence_list": [
                {"type": "data_stores", "pii_check": True},
                {"type": "integrations", "retirement_check": True}
            ],
            "confidence": 0.85,
            "trace": [
                {"step": 1, "check": "PII_exposure"},
                {"step": 2, "check": "dangling_integrations"},
                {"step": 3, "check": "retired_systems"}
            ]
        }
        
        return findings, evidence

    def estate_overview_generate(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """AI narrative summary of overall estate health, for the Dashboard."""
        analysis = AnalysisEngine()
        summary = analysis.generate_dashboard_summary(workbook_id)
        risks = analysis.identify_risks(workbook_id)
        top_risks = [r for r in risks if r['severity'] in ('critical', 'high')][:10]

        facts = {
            "applications": summary["applications"], "modules": summary["modules"],
            "business_rules": summary["business_rules"], "dependencies": summary["dependencies"],
            "metrics": summary["metrics"], "pipeline": summary["pipeline"],
            "critical_and_high_risk_count": len(top_risks),
            "sample_top_risks": [{"risk_type": r["risk_type"], "severity": r["severity"], "risk_description": r["risk_description"]} for r in top_risks[:6]],
        }
        ai_narrative = llm_service.generate_narrative(
            "Estate Overview Analyst",
            "Summarize the overall health of this application estate in 2-3 sentences: pipeline "
            "progress, coverage gaps, and the single biggest risk area to focus on next.",
            facts,
        )

        findings = {
            "summary": summary,
            "top_risk_count": len(top_risks),
            "ai_narrative": ai_narrative,
            "ai_generated": ai_narrative is not None,
        }
        if ai_narrative is None:
            findings["ai_fallback_reason"] = "AI provider unavailable — showing deterministic fallback data, not AI-generated."

        evidence = {
            "evidence_list": [{"type": "dashboard_summary"}, {"type": "risk_analysis", "count": len(risks)}],
            "confidence": 0.8,
            "trace": [{"step": 1, "analysis": "dashboard_summary"}, {"step": 2, "analysis": "risk_identification"}],
        }
        return findings, evidence

    def architecture_diagram_generate(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """
        'Before vs after' architecture diagram for a single modernization
        recommendation - used by the Modernization page's recommendation
        card detail view.

        The topology (nodes/edges: real upstream dependencies, downstream
        dependents, data stores, integrations) is 100% deterministic, pulled
        from the same dependency graph and data_stores/integrations tables
        used everywhere else in the app - never invented. The AI's only job
        is to relabel the modernized node(s) with the target stack and write
        a short narrative of what changes, grounded in those real facts.
        """
        from app.services.xlsx_ingestion import XLSXIngestionService
        svc = XLSXIngestionService()
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        recommendation_id = context.get('recommendation_id')
        cursor.execute("SELECT * FROM modernization_backlog WHERE id = ?", (recommendation_id,))
        rec_row = cursor.fetchone()
        if not rec_row:
            return {}, {"evidence_list": [], "confidence": 0, "trace": []}
        rec = dict(rec_row)

        app = None
        if rec.get('application_id'):
            cursor.execute("SELECT * FROM applications WHERE id = ?", (rec['application_id'],))
            app_row = cursor.fetchone()
            app = dict(app_row) if app_row else None

        module = None
        if rec.get('module_id'):
            cursor.execute("SELECT * FROM code_modules WHERE id = ?", (rec['module_id'],))
            mod_row = cursor.fetchone()
            module = dict(mod_row) if mod_row else None

        focus_id = (module or {}).get('id') or (app or {}).get('id')
        focus_name = (module or {}).get('name') or (app or {}).get('name') or focus_id

        # --- Real topology: reuse the same dependency graph as the Dependencies page ---
        analysis = AnalysisEngine()
        graph = analysis.build_dependency_graph(workbook_id)
        nodes_by_id = {n['id']: n for n in graph['nodes']}
        all_edges = graph['edges']

        upstream_edges = [e for e in all_edges if e['source'] == focus_id][:8]   # what focus_id depends on
        downstream_edges = [e for e in all_edges if e['target'] == focus_id][:8]  # what depends on focus_id

        node_ids = {focus_id}
        node_ids.update(e['target'] for e in upstream_edges)
        node_ids.update(e['source'] for e in downstream_edges)

        real_nodes: Dict[str, Dict[str, Any]] = {}
        if focus_id in nodes_by_id:
            real_nodes[focus_id] = {"id": focus_id, "label": focus_name, "node_type": nodes_by_id[focus_id]['node_type']}
        for nid in node_ids:
            n = nodes_by_id.get(nid)
            if n:
                real_nodes[nid] = {"id": nid, "label": n['name'], "node_type": n['node_type']}

        real_edges = [
            {"source": e['source'], "target": e['target'], "label": e.get('relationship', 'depends_on')}
            for e in upstream_edges + downstream_edges
        ]

        # --- Always surface real DB/integration context for this application,
        # even if it has no modeled dependency edge (this is what was missing) ---
        app_id_for_context = (app or {}).get('id')
        data_store_rows: List[Dict] = []
        integration_rows: List[Dict] = []
        if app_id_for_context:
            cursor.execute("SELECT * FROM data_stores WHERE application_id = ?", (app_id_for_context,))
            data_store_rows = [dict(r) for r in cursor.fetchall()]
            cursor.execute("SELECT * FROM integrations WHERE application_id = ?", (app_id_for_context,))
            integration_rows = [dict(r) for r in cursor.fetchall()]

        for ds in data_store_rows:
            if ds['id'] not in real_nodes:
                pii_tag = " · PII" if str(ds.get('pii_data')).upper() == 'Y' else ""
                real_nodes[ds['id']] = {
                    "id": ds['id'], "node_type": "data_store",
                    "label": f"{ds.get('name') or ds['id']} ({ds.get('store_type') or 'DB'}{pii_tag})",
                }
                real_edges.append({"source": focus_id, "target": ds['id'], "label": "reads/writes"})

        for integ in integration_rows:
            if integ['id'] not in real_nodes:
                real_nodes[integ['id']] = {
                    "id": integ['id'], "node_type": "integration",
                    "label": f"{integ.get('interface_name') or integ['id']} ({integ.get('protocol') or integ.get('integration_type') or 'API'})",
                }
                real_edges.append({"source": focus_id, "target": integ['id'], "label": integ.get('direction') or 'integrates_with'})

        old_nodes = list(real_nodes.values())

        # --- New architecture: identical real topology, only the migrated
        # node(s) get relabeled with the target stack (deterministic, then AI narrates) ---
        target_tech = rec.get('target_tech') or 'Modernized Stack'
        new_nodes = []
        for n in old_nodes:
            n2 = dict(n)
            if n["id"] == focus_id:
                n2["label"] = f"{n['label']} → {target_tech}"
            elif n["node_type"] == "data_store" and target_tech and any(
                kw in target_tech.lower() for kw in ("sql", "postgres", "mongo", "dynamo", "cosmos", "aurora", "db")
            ):
                n2["label"] = f"{n['label']} → {target_tech}"
            new_nodes.append(n2)

        facts = {
            "recommendation": {
                "recommendation": rec.get('recommendation'), "target_tech": target_tech,
                "risk_level": rec.get('risk_level'), "preserves_continuity": rec.get('preserves_continuity'),
                "priority": rec.get('priority'),
            },
            "focus_entity": {"id": focus_id, "name": focus_name, "type": (module or {}).get('module_type') or 'application'},
            "current_stack": {"primary_language": (app or {}).get('primary_language'), "platform": (app or {}).get('platform')},
            "upstream_dependencies": [nodes_by_id[e['target']]['name'] for e in upstream_edges if e['target'] in nodes_by_id],
            "downstream_dependents": [nodes_by_id[e['source']]['name'] for e in downstream_edges if e['source'] in nodes_by_id],
            "data_stores": [ds.get('name') for ds in data_store_rows],
            "integrations": [i.get('interface_name') for i in integration_rows],
        }
        schema_hint = '{"key_changes": [str], "ai_narrative": str}'
        ai_result = llm_service.generate_structured(
            "Modernization Strategist",
            "Given this REAL upstream/downstream/data-store topology in FACTS, write 3-5 short "
            "key_changes bullets (<=12 words each) describing what actually changes when migrating "
            "to target_tech, and a 1-2 sentence ai_narrative covering the impact on the real upstream "
            "dependencies and downstream dependents listed. Do not invent components not in FACTS.",
            facts, schema_hint, max_tokens=500,
        )

        old_architecture = {"nodes": old_nodes, "edges": real_edges}
        new_architecture = {"nodes": new_nodes, "edges": real_edges}

        if ai_result:
            findings = {
                "recommendation": rec,
                "old_architecture": old_architecture,
                "new_architecture": new_architecture,
                "key_changes": ai_result.get("key_changes", []),
                "ai_narrative": ai_result.get("ai_narrative"),
                "ai_generated": True,
            }
        else:
            findings = {
                "recommendation": rec,
                "old_architecture": old_architecture,
                "new_architecture": new_architecture,
                "key_changes": [rec.get('recommendation') or 'Modernize this component'],
                "ai_narrative": None,
                "ai_generated": False,
                "ai_fallback_reason": "AI provider unavailable — topology is real, but key changes/narrative are a minimal fallback, not AI-generated.",
            }

        evidence = {
            "evidence_list": [
                {"source_sheet": "Modernization_Backlog", "source_row": rec.get('source_row'), "type": "recommendation"},
                {"type": "dependency_graph", "upstream_count": len(upstream_edges), "downstream_count": len(downstream_edges)},
                {"type": "data_stores", "count": len(data_store_rows)},
                {"type": "integrations", "count": len(integration_rows)},
            ],
            "confidence": 0.85,
            "trace": [{"step": 1, "entity": "Recommendation", "id": rec['id']}, {"step": 2, "analysis": "dependency_graph_neighborhood"}],
        }
        return findings, evidence

    def knowledge_hub_search(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """
        Vector-embedding RAG search across the workbook's free-text knowledge
        (documentation excerpts, business rules, modernization backlog).
        Retrieval: cosine-similarity search over embedded chunks.
        Augmentation: top-k chunks placed into the LLM prompt as context.
        Generation: the LLM answers strictly from those retrieved chunks.
        """
        from app.services import vector_store

        query = (context.get('query') or '').strip()
        if not query:
            return {}, {"evidence_list": [], "confidence": 0, "trace": []}

        results = vector_store.semantic_search(workbook_id, query, top_k=5)

        if not results:
            findings = {
                "query": query,
                "retrieved": [],
                "answer": None,
                "ai_generated": False,
                "ai_fallback_reason": "Vector embeddings unavailable (LLMaaS not configured/reachable) — no semantic search results.",
            }
            evidence = {"evidence_list": [], "confidence": 0, "trace": []}
            return findings, evidence

        schema_hint = '{"answer": str}'
        ai_result = llm_service.generate_structured(
            "Knowledge Hub Retriever",
            "Answer the user's query using ONLY the retrieved chunks in FACTS.retrieved_chunks. "
            "Cite which source_type(s) you used. If the chunks don't contain enough information, "
            "say so explicitly rather than guessing.",
            {"query": query, "retrieved_chunks": [{"text": r["text"], "source_type": r["source_type"]} for r in results]},
            schema_hint, max_tokens=400,
        )

        findings = {
            "query": query,
            "retrieved": results,
            "answer": ai_result.get("answer") if ai_result else None,
            "ai_generated": ai_result is not None,
        }
        if ai_result is None:
            findings["ai_fallback_reason"] = "AI provider unavailable — showing retrieved chunks only, no generated answer."

        evidence = {
            "evidence_list": [
                {"type": "vector_search", "source_type": r["source_type"], "id": r["id"], "score": r["score"]}
                for r in results
            ],
            "confidence": 0.8,
            "trace": [
                {"step": 1, "analysis": "embedding_retrieval"},
                {"step": 2, "analysis": "grounded_generation"},
            ],
        }
        return findings, evidence

    def cobol_source_analyze(self, source: str, filename: str) -> Tuple[Dict, Dict]:
        """
        Analyze a single .cbl COBOL source file: structural facts (divisions,
        data items, paragraphs, CALLs, copybooks, file I/O, embedded SQL,
        complexity estimate) are parsed deterministically; the LLM only adds
        a business-purpose summary and modernization/risk notes on top.
        """
        from app.services.cobol_parser import parse_cobol_source
        facts = parse_cobol_source(source, filename)

        schema_hint = (
            '{"summary": str, "modernization_notes": [str], "risk_notes": [str], "ai_narrative": str}'
        )
        ai_result = llm_service.generate_structured(
            "Legacy Archaeologist",
            "Analyze this REAL parsed COBOL program from FACTS (not a spreadsheet row - actual "
            "source code structure). Write a 1-2 sentence summary of its likely business purpose "
            "based on the program-id/data item/paragraph names. List 2-4 modernization_notes "
            "(e.g. embedded SQL, external CALLs, COPY dependencies, GOTOs found). List 2-4 "
            "risk_notes (e.g. high complexity, unclear paragraph structure, tight file coupling). "
            "Then write a 1-2 sentence ai_narrative tying it together. Ground everything in FACTS only.",
            facts, schema_hint, max_tokens=700,
        )

        if ai_result:
            findings = {
                **facts,
                "summary": ai_result.get("summary"),
                "modernization_notes": ai_result.get("modernization_notes", []),
                "risk_notes": ai_result.get("risk_notes", []),
                "ai_narrative": ai_result.get("ai_narrative"),
                "ai_generated": True,
            }
        else:
            findings = {
                **facts,
                "summary": None,
                "modernization_notes": [],
                "risk_notes": [],
                "ai_narrative": None,
                "ai_generated": False,
                "ai_fallback_reason": "AI provider unavailable — showing parsed structural facts only, not AI-generated.",
            }

        evidence = {
            "evidence_list": [{"type": "cobol_source", "filename": filename, "total_lines": facts["total_lines"]}],
            "confidence": 0.75,
            "trace": [
                {"step": 1, "analysis": "cobol_structural_parse"},
                {"step": 2, "analysis": "ai_annotation"},
            ],
        }
        return findings, evidence

    def cobol_modernize_code(self, workbook_id: str, context: Dict) -> Tuple[Dict, Dict]:
        """
        For a modernization recommendation that originated from a COBOL
        ingestion, translate the REAL original COBOL source (the exact
        paragraph, re-fetched from the saved .cbl file — not just structural
        facts) into idiomatic code for the recommendation's target_tech.
        The AI is instructed to preserve the original logic exactly, not
        invent new business rules.
        """
        from app.services.cobol_ingestion import get_cobol_source
        from app.services.cobol_parser import parse_cobol_source
        from app.services.xlsx_ingestion import XLSXIngestionService

        recommendation_id = context.get('recommendation_id')
        svc = XLSXIngestionService()
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM modernization_backlog WHERE id = ?", (recommendation_id,))
        rec_row = cursor.fetchone()
        if not rec_row:
            return {}, {"evidence_list": [], "confidence": 0, "trace": []}
        rec = dict(rec_row)

        source, filename = get_cobol_source(workbook_id)
        if source is None:
            return (
                {"available": False, "reason": "This recommendation did not originate from a COBOL file ingestion — no original source code exists to translate."},
                {"evidence_list": [], "confidence": 0, "trace": []},
            )

        module = None
        if rec.get('module_id'):
            cursor.execute("SELECT * FROM code_modules WHERE id = ?", (rec['module_id'],))
            m = cursor.fetchone()
            module = dict(m) if m else None

        facts = parse_cobol_source(source, filename)
        paragraph_name = module.get('name') if module else None
        original_snippet = None
        if paragraph_name:
            for p in facts.get('paragraph_details', []):
                if p['name'] == paragraph_name:
                    original_snippet = f"{paragraph_name}.\n{p['body']}".strip()
                    break
        if original_snippet is None:
            # Program-level recommendation (e.g. file/integration migration) - use the
            # DATA/ENVIRONMENT context most relevant to it instead of a single paragraph.
            original_snippet = source[:4000]

        target_tech = rec.get('target_tech') or 'a modern equivalent stack'
        ai_facts = {
            "recommendation": rec.get('recommendation'),
            "target_tech": target_tech,
            "paragraph_name": paragraph_name,
            "original_cobol_snippet": original_snippet,
        }
        schema_hint = '{"language": str, "modernized_code": str, "explanation": str, "ai_narrative": str}'
        ai_result = llm_service.generate_structured(
            "Modernization Strategist",
            "Translate the REAL COBOL snippet in FACTS.original_cobol_snippet into idiomatic code "
            "for FACTS.target_tech (pick a sensible language: e.g. Java for 'Java/Spring', Python "
            "for generic service targets, SQL/DDL for database targets like PostgreSQL). Preserve "
            "the exact conditions/business logic from the original — do not invent new rules or "
            "fields not present in FACTS. Return: language (the language you chose), modernized_code "
            "(a complete, readable code block), explanation (2-3 sentences mapping old constructs to "
            "new ones), and a 1-sentence ai_narrative.",
            ai_facts, schema_hint, max_tokens=1200,
        )

        if ai_result and ai_result.get("modernized_code"):
            findings = {
                "available": True,
                "recommendation_id": recommendation_id,
                "paragraph_name": paragraph_name,
                "original_code": original_snippet,
                "language": ai_result.get("language", target_tech),
                "modernized_code": ai_result.get("modernized_code"),
                "explanation": ai_result.get("explanation"),
                "ai_narrative": ai_result.get("ai_narrative"),
                "ai_generated": True,
            }
        else:
            findings = {
                "available": True,
                "recommendation_id": recommendation_id,
                "paragraph_name": paragraph_name,
                "original_code": original_snippet,
                "language": None,
                "modernized_code": None,
                "explanation": None,
                "ai_narrative": None,
                "ai_generated": False,
                "ai_fallback_reason": "AI provider unavailable — showing the original COBOL source only, no modernized code generated.",
            }

        evidence = {
            "evidence_list": [{"source_sheet": filename, "source_row": rec.get('source_row'), "type": "recommendation"}],
            "confidence": 0.7,
            "trace": [{"step": 1, "entity": "Recommendation", "id": rec['id']}, {"step": 2, "analysis": "cobol_code_translation"}],
        }
        return findings, evidence

