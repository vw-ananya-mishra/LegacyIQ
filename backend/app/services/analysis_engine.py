"""
Analysis Engine & Agent Orchestrator
Core intelligence for LegacyX
"""

import sqlite3
import uuid
from typing import Dict, List, Any, Tuple, Optional
import networkx as nx
from collections import defaultdict, deque
import re

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
        
        # Fetch all dependencies
        cursor.execute("SELECT * FROM dependencies")
        deps = [dict(row) for row in cursor.fetchall()]
        
        # Build NetworkX graph (filter out None values)
        G = nx.DiGraph()
        
        for dep in deps:
            source = dep['source_id']
            target = dep['target_id']
            # Skip if source or target is None
            if source is None or target is None:
                continue
            G.add_edge(source, target, 
                      relationship=dep['relationship_type'],
                      criticality=dep['criticality'])
        
        # Convert to node/edge lists for visualization
        nodes = []
        edges = []
        
        for node in G.nodes():
            in_degree = G.in_degree(node)
            out_degree = G.out_degree(node)
            nodes.append({
                "id": node,
                "label": node,
                "in_degree": in_degree,
                "out_degree": out_degree
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
            }
        }
        
        # Detect orphans
        if detect_orphans:
            orphans = []
            for node in G.nodes():
                if G.in_degree(node) == 0 and G.out_degree(node) == 0:
                    orphans.append(node)
                elif G.in_degree(node) == 0 and node not in [G.nodes()]:
                    pass
            result['orphan_nodes'] = orphans
        
        # Detect cycles
        if detect_cycles:
            cycles = list(nx.simple_cycles(G))
            result['cycles'] = cycles
        
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
            SELECT COUNT(*) as count FROM code_modules WHERE test_coverage IS NOT NULL AND test_coverage > 0
        """)
        tested_modules = cursor.fetchone()[0]
        
        module_coverage = (tested_modules / module_count * 100) if module_count > 0 else 0
        
        # Count documented modules
        cursor.execute("""
            SELECT COUNT(*) as count FROM code_modules WHERE description IS NOT NULL
        """)
        documented_modules = cursor.fetchone()[0]
        
        doc_coverage = (documented_modules / module_count * 100) if module_count > 0 else 0
        
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
                "understand": {"status": "pending", "completion": 0},
                "document": {"status": "pending", "completion": 0},
                "map": {"status": "pending", "completion": 0},
                "test": {"status": "pending", "completion": rule_coverage},
                "modernize": {"status": "pending", "completion": 0}
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
        
        # Risk 1: Undocumented critical modules
        cursor.execute("""
            SELECT id, name, complexity_score FROM code_modules 
            WHERE description IS NULL OR description = ''
            AND complexity_score > 7
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "module",
                "risk_type": "documentation",
                "risk_description": f"Critical module '{row['name']}' (complexity {row['complexity_score']}) lacks documentation",
                "severity": "high",
                "remediation": "Generate functional specification and API documentation"
            })
        
        # Risk 2: Untested critical business rules
        cursor.execute("""
            SELECT id, rule_name, criticality FROM business_rules 
            WHERE id NOT IN (SELECT DISTINCT rule_id FROM test_cases)
            AND criticality = 'critical'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "rule",
                "risk_type": "test_coverage",
                "risk_description": f"Critical business rule '{row['rule_name']}' has no test coverage",
                "severity": "critical",
                "remediation": "Create comprehensive test cases for parity validation"
            })
        
        # Risk 3: Dangling integrations
        cursor.execute("""
            SELECT id, external_system FROM integrations 
            WHERE status = 'deprecated' OR status = 'retired'
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "integration",
                "risk_type": "continuity",
                "risk_description": f"Integration with '{row['external_system']}' is retired but may still be in use",
                "severity": "high",
                "remediation": "Trace downstream dependencies and plan migration"
            })
        
        # Risk 4: PII exposure
        cursor.execute("""
            SELECT id, name FROM data_stores WHERE pii_data = 1
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
        
        # Risk 5: High complexity modules
        cursor.execute("""
            SELECT id, name, complexity_score FROM code_modules 
            WHERE complexity_score > 8
        """)
        for row in cursor.fetchall():
            risk_id += 1
            risks.append({
                "id": f"risk_{risk_id}",
                "entity_id": row['id'],
                "entity_type": "module",
                "risk_type": "complexity",
                "risk_description": f"Module '{row['name']}' has high complexity score ({row['complexity_score']}) — migration risk",
                "severity": "medium",
                "remediation": "Refactor into smaller, testable units before modernization"
            })
        
        return risks
    
    def build_trace_chain(self, workbook_id: str, finding_id: str, finding_type: str) -> List[Dict[str, Any]]:
        """
        Build complete trace chain: Output → Rule/Module → Dependency → Source Sheet → Source Record
        """
        from app.services.xlsx_ingestion import XLSXIngestionService
        
        svc = XLSXIngestionService()
        db_path = svc._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        trace = []
        
        if finding_type == "risk":
            # Trace back to entity
            cursor.execute("SELECT * FROM risks WHERE id = ?", (finding_id,))
        elif finding_type == "recommendation":
            cursor.execute("SELECT * FROM modernization_backlog WHERE id = ?", (finding_id,))
        else:
            return []
        
        finding = cursor.fetchone()
        if finding:
            trace.append({
                "step": 1,
                "level": "finding",
                "type": finding_type,
                "data": dict(finding)
            })
        
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
        
        cursor.execute("SELECT * FROM business_rules WHERE application_id = ?", (app['id'],))
        rules = [dict(row) for row in cursor.fetchall()]
        
        findings = {
            "application": dict(app),
            "module_count": len(modules),
            "rule_count": len(rules),
            "architecture": {
                "technology_stack": app.get('technology_stack'),
                "total_lines_of_code": sum(m.get('lines_of_code', 0) for m in modules),
                "average_module_complexity": sum(m.get('complexity_score', 0) for m in modules) / len(modules) if modules else 0
            },
            "critical_modules": [m for m in modules if m.get('complexity_score', 0) > 7],
            "business_logic": {
                "critical_rules": [r for r in rules if r.get('criticality') == 'critical'],
                "total_rules": len(rules)
            },
            "complexity_hotspots": [m for m in modules if m.get('complexity_score', 0) > 8],
            "confidence": 0.85
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
        
        findings = {
            "document_type": doc_type,
            "status": "draft",
            "application": dict(app) if app else None,
            "sections": []
        }
        
        if doc_type == "functional_specification":
            findings['sections'] = [
                {
                    "title": "1. Overview",
                    "content": f"System: {app.get('name')}\nTechnology: {app.get('technology_stack')}\nStatus: {app.get('status')}"
                },
                {
                    "title": "2. Business Context",
                    "content": app.get('description', 'No description provided'),
                    "requires_review": app.get('description') is None
                },
                {
                    "title": "3. Architecture",
                    "content": f"Complexity: {app.get('complexity')}\nCriticality: {app.get('criticality')}",
                    "requires_review": True
                }
            ]
        
        evidence = {
            "evidence_list": [
                {"source_sheet": "Applications", "source_row": app.get('source_row'), "field": "Name"},
                {"source_sheet": "Applications", "source_row": app.get('source_row'), "field": "Description"},
                {"source_sheet": "Applications", "source_row": app.get('source_row'), "field": "Technology_Stack"}
            ],
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
        
        findings = {
            "graph": graph,
            "orphans": graph.get('orphan_nodes', []),
            "cycles": graph.get('cycles', []),
            "statistics": graph.get('statistics', {})
        }
        
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
        
        tests = []
        for idx, test in enumerate(test_cases):
            # Find the rule for this test
            rule = next((r for r in rules if r['id'] == test.get('rule_id')), None)
            
            tests.append({
                "test_id": test.get('id', f"test_{idx}"),
                "test_name": test.get('test_name', f"Test_{idx}"),
                "rule_id": test.get('rule_id', 'N/A'),
                "module_id": test.get('module_id', 'N/A'),
                "description": test.get('description', 'No description'),
                "input_data": test.get('input_data', 'N/A'),
                "expected_output": test.get('expected_output', 'N/A'),
                "test_type": test.get('test_type', 'unit'),
                "status": test.get('status', 'pending'),
                "legacy_result": "pending",
                "modern_result": "pending",
                "parity_status": "pending_execution"
            })
        
        findings = {
            "total_tests": len(tests),
            "passed": 0,
            "failed": 0,
            "tests": tests
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
        priority_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        
        for idx, item in enumerate(backlog_items):
            priority = item.get('priority', 'medium')
            priority_num = priority_map.get(str(priority).lower(), 2)
            
            recommendations.append({
                "id": item.get('id', f"rec_{idx+1}"),
                "recommendation": item.get('recommendation', 'Modernization recommendation'),
                "priority": priority,
                "priority_level": priority_num,
                "application_id": item.get('application_id'),
                "module_id": item.get('module_id'),
                "effort_estimate": item.get('effort_estimate', 'unknown'),
                "risk_level": item.get('risk_level', 'medium'),
                "dependencies": item.get('dependencies', '').split(',') if item.get('dependencies') else [],
                "status": item.get('status', 'draft'),
                "strategy": f"Execute {item.get('recommendation', 'recommendation').lower()}",
                "effort": item.get('effort_estimate', 'medium')
            })
        
        findings = {
            "recommendations": recommendations,
            "roadmap": ["Protect", "Understand", "Isolate", "Migrate", "Retire"],
            "total_recommendations": len(recommendations),
            "statistics": {
                "total_risks": len(risks),
                "critical_risks": len([r for r in risks if r['severity'] == 'critical']),
                "high_risks": len([r for r in risks if r['severity'] == 'high']),
                "modernization_items": len(backlog_items)
            }
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
        
        findings = {
            "security_risks": security_risks,
            "continuity_risks": continuity_risks,
            "total_risks": len(risks),
            "summary": f"Found {len(security_risks)} security issues and {len(continuity_risks)} continuity issues"
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
