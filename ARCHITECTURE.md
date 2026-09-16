# LegacyX Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                                 │
│                    (http://localhost:3000)                          │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                    React Frontend
                    ┌─────────────────┐
                    │   React + TS    │
                    │   8 Pages       │
                    │   Tailwind UI   │
                    └────────┬────────┘
                             │
                        ┌────▼────────┐
                        │  Axios API  │
                        │   Client    │
                        └────┬────────┘
                             │
                   HTTP REST API (Port 8000)
                             │
     ┌───────────────────────┴──────────────────────┐
     │                                              │
     ▼                                              ▼
FastAPI Backend ◄────────────────────────────► SQLite Database
(Port 8000)      HTTP (REST + JSON)            (Normalized Data)
│                                                │
├─ /api/workbook/*                             ├─ Applications
├─ /api/agent/*                                ├─ Code_Modules
├─ /api/dependency-graph/*                     ├─ Business_Rules
├─ /api/traceability/*                         ├─ Dependencies
└─ /health                                     ├─ Data_Stores
                                               ├─ Integrations
                                               ├─ Test_Cases
                                               ├─ Modernization_Backlog
                                               └─ Risks (Calculated)
```

## System Components

### 1. Frontend Layer (React/TypeScript)
```
Frontend (Vite + React + TypeScript)
├── Pages (8 main)
│   ├── UploadPage - XLSX ingestion interface
│   ├── DashboardPage - Command center with pipeline
│   ├── UnderstandPage - Estate analysis
│   ├── DocumentPage - Documentation generation
│   ├── DependencyMapPage - Interactive graph
│   ├── ParityLabPage - Test validation
│   ├── ModernizationPage - Strategy & recommendations
│   └── TraceabilityPage - Audit trail viewer
├── Components
│   └── Navigation - Main navigation bar
├── Types
│   └── 15+ TypeScript interfaces
└── Utils
    └── API client with Axios
```

### 2. API Layer (FastAPI)
```
FastAPI Backend (Python)
├── Workbook Management (6 endpoints)
│   ├── POST /api/workbook/upload
│   ├── GET /api/workbook/{id}/metadata
│   ├── GET /api/workbook/{id}/applications
│   ├── GET /api/workbook/{id}/modules
│   ├── GET /api/workbook/{id}/dependencies
│   └── GET /api/workbook/{id}/business-rules
├── Analysis Endpoints (9 endpoints)
│   ├── POST /api/agent/analyze
│   ├── POST /api/dependency-graph/analyze
│   ├── GET /api/workbook/{id}/dashboard-summary
│   ├── GET /api/workbook/{id}/risks
│   ├── POST /api/traceability/trace
│   └── [Utility endpoints]
└── Infrastructure
    ├── GET /health
    ├── CORS middleware
    └── Error handling
```

### 3. Service Layer (Business Logic)
```
Analysis & Processing Services

XLSXIngestionService
├── ingest_workbook()
├── _extract_sheet_data()
├── _store_sheet_data()
├── _create_schema()
├── _build_relationships()
└── Data retrieval methods (get_applications, etc.)

AnalysisEngine
├── build_dependency_graph()
├── generate_dashboard_summary()
├── identify_risks()
└── build_trace_chain()

AgentOrchestrator (6 Agents)
├── legacy_archaeologist_analyze()
├── documentation_architect_generate()
├── dependency_detective_analyze()
├── parity_engineer_generate()
├── modernization_strategist_recommend()
└── security_continuity_guardian_detect()
```

### 4. Data Layer (SQLite)
```
Database Schema (Normalized)

Tables (8):
├── applications
│   └── Core system information
├── code_modules
│   └── Software components with metrics
├── business_rules
│   └── Business logic definitions
├── dependencies
│   └── Relationships between entities
├── data_stores
│   └── Data assets and databases
├── integrations
│   └── External system connections
├── test_cases
│   └── Test definitions for parity
└── modernization_backlog
    └── Recommendations and tasks

All tables include:
├── source_sheet - Which XLSX sheet
├── source_row - Which row in sheet
├── trace_id - Unique trace identifier
└── Related metadata

Plus calculated tables:
├── risks (Generated from analysis)
└── coverage_metrics (Aggregated stats)
```

## Data Flow Architecture

```
1. UPLOAD & INGEST
   XLSX File → FastAPI /upload
              ↓
   Validation & Normalization
              ↓
   SQLite Storage (with trace metadata)

2. ANALYSIS & PROCESSING
   SQLite Data → Analysis Engine
                ├→ Coverage Analysis
                ├→ Risk Identification
                ├→ Graph Construction
                └→ Trace Building
                ↓
   Agent Orchestrator
   ├→ Legacy Archaeologist
   ├→ Documentation Architect
   ├→ Dependency Detective
   ├→ Parity Engineer
   ├→ Modernization Strategist
   └→ Security & Continuity Guardian
                ↓
   Findings + Evidence + Trace

3. DELIVERY TO FRONTEND
   REST API Responses
        ↓
   React Components
        ↓
   User Dashboard & Analysis
```

## Processing Pipeline

```
UNDERSTAND           DOCUMENT           MAP                TEST              MODERNIZE
   │                   │                 │                  │                   │
   ├─ Applications     ├─ Specs          ├─ Graph Viz       ├─ Test Gen        ├─ Risk Assess
   ├─ Modules          ├─ Requirements   ├─ Orphans         ├─ Comparison      ├─ Effort Est
   ├─ Rules            ├─ APIs           ├─ Cycles          ├─ Mismatches      ├─ Roadmap
   └─ Coverage         └─ Traceability   └─ Statistics      └─ Source Trace    └─ Approval Gate

    Coverage %        Evidence Quality    Graph Metrics      Test Pass %       Recommendation
    Documentation %   Review Status       Cycle Count        Mismatch Count     Status
    Hotspots          Completeness        Orphan Count       Critical Rules     Priority
```

## Traceability Architecture

```
Finding (Recommendation/Risk/Test Result)
    │
    ├─ Finding ID
    ├─ Finding Type
    ├─ Finding Data
    │
    ▼
Trace Chain
    │
    ├─ Step 1: Entity Reference (Rule/Module/Integration)
    │   └─ entity_id, entity_type
    │
    ├─ Step 2: Source Sheet
    │   └─ source_sheet name
    │
    ├─ Step 3: Source Row
    │   └─ source_row number
    │
    ├─ Step 4: Trace ID
    │   └─ UUID for audit
    │
    └─ Step 5: Dependencies
        └─ Related entities and their traces

Result: "Finding → Rule/Module → Dependency → Source Sheet → Source Record"
```

## Agent Architecture

```
6 Specialized Agents

┌─────────────────────────────────────────────────────────────────┐
│                     Agent Orchestrator                          │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─────────────────┬─────────────────┬─────────────────┐
    │                 │                 │                 │
    ▼                 ▼                 ▼                 ▼
┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Legacy    │  │ Documentation│  │ Dependency   │  │ Parity       │
│Archaeologist│  │ Architect    │  │ Detective    │  │ Engineer     │
│            │  │              │  │              │  │              │
│• Apps      │  │• Specs       │  │• Graph       │  │• Tests       │
│• Modules   │  │• Requirements│  │• Orphans     │  │• Comparison  │
│• Rules     │  │• APIs        │  │• Cycles      │  │• Mismatches  │
│• Complexity│  │• Flows       │  │• Path trace  │  │• Coverage    │
└────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
    │                 │                 │                 │
    │                 │                 │                 │
    ├─────────────────┬─────────────────┬─────────────────┤
    │                 │                 │
    ▼                 ▼                 ▼
┌──────────────────┐  ┌──────────────────────────────────────┐
│ Modernization    │  │ Security & Continuity Guardian       │
│ Strategist       │  │                                      │
│                  │  │ • Security risks (credentials, PII)  │
│ • Recommendations│  │ • Continuity risks (integrations)    │
│ • Risk/Effort    │  │ • Downstream impact                  │
│ • Roadmap        │  │ • Remediation steps                  │
│ • Approval Gate  │  │                                      │
└──────────────────┘  └──────────────────────────────────────┘

Each Agent:
├─ Takes: workbook_id + context
├─ Returns: findings + evidence + trace
└─ Confidence: 0-1 score with reasoning
```

## Dependency Graph Analysis

```
Graph Construction (NetworkX DiGraph)
    │
    ├─ Nodes: All entities (modules, apps, data stores, etc.)
    ├─ Edges: Relationships between entities
    │   └─ Attributes: type, criticality, bidirectional
    │
    ▼
Analysis Algorithms
    │
    ├─ Orphan Detection
    │   └─ in_degree = 0 AND out_degree = 0
    │   └─ Output: List of orphan node IDs
    │
    ├─ Cycle Detection
    │   └─ Simple cycle finding algorithm
    │   └─ Output: List of cycles (paths)
    │
    ├─ Path Analysis
    │   └─ Shortest path between any two nodes
    │   └─ Output: Critical paths, blast radius
    │
    ├─ Density Calculation
    │   └─ Graph density metric
    │   └─ Output: Complexity score
    │
    └─ Centrality Analysis
        └─ Node importance by in/out degree
        └─ Output: Most critical components

Visualization Data
├─ nodes: [{id, label, in_degree, out_degree}]
├─ edges: [{source, target, relationship, criticality}]
└─ stats: {node_count, edge_count, density, cycles[], orphans[]}
```

## Risk Analysis Architecture

```
Risk Identification Engine

Input: SQLite Data
    │
    ├─ Rule 1: Undocumented High-Complexity Modules
    │   └─ Query: complexity > 7 AND description IS NULL
    │   └─ Severity: HIGH
    │
    ├─ Rule 2: Untested Critical Rules
    │   └─ Query: criticality='critical' AND rule_id NOT IN test_cases
    │   └─ Severity: CRITICAL
    │
    ├─ Rule 3: Dangling Integrations
    │   └─ Query: status IN ('deprecated', 'retired')
    │   └─ Severity: HIGH
    │
    ├─ Rule 4: PII Data Exposure
    │   └─ Query: pii_data = TRUE
    │   └─ Severity: CRITICAL
    │
    └─ Rule 5: High Complexity Modules
        └─ Query: complexity_score > 8
        └─ Severity: MEDIUM

Output: [Risk Objects]
├─ risk_id
├─ entity_id, entity_type
├─ risk_type
├─ severity (CRITICAL/HIGH/MEDIUM/LOW)
├─ description
├─ remediation
└─ source_sheet, source_row (traceability)
```

## Deployment Topology

```
Option 1: Local Development
┌────────────────┐
│ Docker Desktop │
└────────────────┘
    │
    ├─ Backend Container (Python/FastAPI)
    ├─ Frontend Container (Node/React)
    └─ Nginx Container (Reverse Proxy)

Option 2: Cloud Deployment
┌─────────────────┐
│ Kubernetes/ECS  │
└─────────────────┘
    │
    ├─ Backend Pod (Replicated)
    ├─ Frontend Pod (Replicated)
    ├─ PostgreSQL (Persistent)
    ├─ Redis (Cache)
    └─ Nginx Ingress

Option 3: Development
┌─────────────────┐
│ Local Terminals │
└─────────────────┘
    │
    ├─ Terminal 1: python main.py (Backend)
    └─ Terminal 2: npm run dev (Frontend)
```

## Security Architecture

```
Security Layers

1. Input Validation
   ├─ XLSX schema validation
   ├─ File type checking
   └─ Size limits

2. Data Sanitization
   ├─ Credential detection & masking
   ├─ PII flagging (not extraction)
   └─ SQL injection prevention (SQLite parameterized queries)

3. API Security
   ├─ CORS configuration
   ├─ Rate limiting (for production)
   └─ Error message sanitization

4. Storage Security
   ├─ Local SQLite encryption (at rest)
   ├─ No credentials in code
   └─ Environment variable isolation

5. Audit Trail
   ├─ Trace ID per finding
   ├─ Source sheet reference
   ├─ User action logging
   └─ Approval workflow tracking
```

## Performance Characteristics

```
Benchmark Results (Sample Data):
├─ XLSX Ingestion
│   └─ 50 entities/sheet → ~2 seconds
│   └─ Index creation → ~0.5 seconds
│
├─ Analysis Generation
│   └─ Dependency graph → ~0.1 seconds
│   └─ Risk identification → ~0.05 seconds
│   └─ Coverage metrics → ~0.02 seconds
│
├─ API Response Times
│   └─ Metadata retrieval → <50ms
│   └─ Agent analysis → 100-500ms
│   └─ Dashboard summary → ~100ms
│
└─ Frontend Performance
    └─ Initial load → <2 seconds
    └─ Page transitions → <200ms
    └─ Graph rendering → <1 second
```

## Scalability Considerations

```
Current (Prototype):
├─ SQLite: Single file-based DB
├─ Single backend instance
├─ Memory-based caching
└─ Suitable for: Individual analysis

For Production Scale:
├─ PostgreSQL: Multi-user, ACID compliance
├─ Backend replicas: Load balanced
├─ Redis cache: Distributed caching
├─ Async jobs: Background processing
├─ CDN: Frontend static asset delivery
└─ Suitable for: Enterprise teams
```

---

## Key Design Decisions

✅ **SQLite for Prototype**: Fast, file-based, no setup overhead
✅ **REST API**: Standard, well-understood, easy testing
✅ **React SPA**: Responsive, modern, component-based
✅ **Type-Safe Frontend**: TypeScript catches errors early
✅ **Deterministic Analysis**: No hallucinations, reproducible results
✅ **Complete Traceability**: Every finding linked to source
✅ **Human Approval Gates**: No automatic destructive actions
✅ **Evidence-Backed**: Every recommendation has supporting data

---

## Architecture Evolution Path

```
v1.0 (Current)
├─ Core agents implemented
├─ SQLite storage
├─ REST API
├─ React frontend
└─ Prototype-ready

v2.0 (Planned)
├─ PostgreSQL backend
├─ Multi-user support
├─ Real-time collaboration
├─ Advanced visualization
└─ CI/CD integration

v3.0 (Envisioned)
├─ LLM-powered agents
├─ Predictive analysis
├─ Automated testing
├─ Custom rule engines
└─ Enterprise SaaS platform
```

---

**LegacyX Architecture v1.0**
*Enterprise Legacy Modernization Command Center*
