# LegacyIQ - Architecture & System Design

> **Enterprise-Grade Modernization Intelligence Platform**

---

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                           │
├──────────────────────────────────────────────────────────────────────┤
│  React 18 + TypeScript + Tailwind CSS (Dark/Light Theme Support)    │
│  ├─ Dashboard Page       (Metrics, KPIs, quick actions)             │
│  ├─ Upload Page          (XLSX / COBOL file ingestion)              │
│  ├─ Understand Page      (Application inventory deep-dive)          │
│  ├─ Document Page        (AI-generated specs)                       │
│  ├─ Dependencies Page    (3D graph visualization)                   │
│  ├─ Parity Lab Page      (Test coverage tracking)                   │
│  ├─ Modernization Page   (Recommendations + code translation)       │
│  ├─ Traceability Page    (Audit chain visualization)                │
│  └─ Knowledge Hub        (LLM Q&A interface)                        │
│  
│  Components:
│  ├─ Navigation Bar       (Theme toggle, workbook selector)          │
│  ├─ Application Filter   (Multi-page application selector)          │
│  ├─ 3D Graph Component   (Three.js, react-force-graph-3d)          │
│  ├─ Modal Dialogs        (Architecture diagrams, code suggestions)  │
│  ├─ Data Tables          (Sortable, filterable entity lists)        │
│  └─ Charts/Analytics     (Risk levels, coverage %, effort burndown) │
└──────────────────────────────────────────────────────────────────────┘
                                  ↓ (REST API)
┌──────────────────────────────────────────────────────────────────────┐
│                         API LAYER (FastAPI)                          │
├──────────────────────────────────────────────────────────────────────┤
│  Core Endpoints:                                                     │
│  ├─ POST /api/workbook/upload          (XLSX or COBOL ingestion)   │
│  ├─ GET  /api/workbook/{id}/metadata   (Workbook info)             │
│  ├─ GET  /api/workbook/{id}/dashboard  (Dashboard metrics)         │
│  ├─ GET  /api/workbook/{id}/applications                           │
│  ├─ GET  /api/workbook/{id}/modules    (With filtering)            │
│  ├─ GET  /api/workbook/{id}/rules                                  │
│  ├─ GET  /api/workbook/{id}/dependencies                           │
│  ├─ GET  /api/workbook/{id}/risks                                  │
│  ├─ GET  /api/workbook/{id}/trace/{entity_id}                      │
│  ├─ POST /api/agent/analyze            (Recommendations engine)    │
│  ├─ POST /api/agent/modernize-code     (COBOL→Python/Java trans.)  │
│  └─ POST /api/graph/render             (3D graph data generation)  │
│                                                                      │
│  Middleware:                                                         │
│  ├─ CORS (frontend cross-origin access)                             │
│  ├─ Request validation (Pydantic)                                   │
│  ├─ Error handling (consistent error responses)                     │
│  └─ Logging (request/response traces)                               │
└──────────────────────────────────────────────────────────────────────┘
                                  ↓ (In-Memory Compute)
┌──────────────────────────────────────────────────────────────────────┐
│                       ANALYSIS ENGINE (Python)                       │
├──────────────────────────────────────────────────────────────────────┤
│  Analysis Services:                                                  │
│  ├─ XLSX Ingestion                                                  │
│  │  ├─ Sheet detection (fuzzy column matching)                      │
│  │  ├─ Data validation (type checking, null handling)               │
│  │  ├─ Relationship inference (FK detection by convention)          │
│  │  └─ Traceability tracking (source_sheet, source_row, trace_id)  │
│  │                                                                   │
│  ├─ COBOL Ingestion                                                 │
│  │  ├─ Lexical parsing (PROCEDURE DIVISION, paragraphs)            │
│  │  ├─ Line tracking (exact source position for each entity)        │
│  │  ├─ Complexity scoring (per-paragraph, local IF/EVALUATE count) │
│  │  ├─ Dependency resolution (PERFORM, CALL, SELECT...ASSIGN TO)  │
│  │  └─ Raw source persistence (for later code translation)         │
│  │                                                                   │
│  ├─ Dependency Analysis (NetworkX)                                  │
│  │  ├─ Graph construction (edges from PERFORM/CALL/file I/O)       │
│  │  ├─ Cycle detection (DFS-based circular dependency finder)      │
│  │  ├─ Orphan detection (isolated nodes, never referenced)         │
│  │  ├─ Transitive closure (reachability analysis)                  │
│  │  └─ Complexity metrics (out-degree, in-degree, betweenness)     │
│  │                                                                   │
│  ├─ Risk Assessment                                                 │
│  │  ├─ Complexity scoring (LOC + cyclomatic + nesting depth)       │
│  │  ├─ Criticality mapping (business domain + owner)               │
│  │  ├─ Risk level assignment (high/medium/low/unknown)             │
│  │  ├─ Continuity break detection (file I/O patterns)              │
│  │  └─ Coverage metrics (test %, doc %)                            │
│  │                                                                   │
│  └─ Trace Chain Builder                                             │
│     ├─ Entity resolution (app → module → rule → test)              │
│     ├─ Dependency traversal (upstream/downstream)                  │
│     ├─ Source mapping (entity → XLSX sheet/row)                    │
│     └─ UUID trace ID generation (audit trail)                      │
│                                                                      │
│  LLM Integration Services:                                          │
│  ├─ Narrative generation (why behind recommendations)              │
│  ├─ Risk prioritization (ML-powered ordering)                      │
│  ├─ Code modernization (COBOL paragraph → Python/Java/SQL)        │
│  ├─ Functional spec synthesis (overview + architecture)            │
│  └─ Fallback handling (Ollama local if LLMaaS unavailable)        │
└──────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────┐
│                       DATA PERSISTENCE LAYER                         │
├──────────────────────────────────────────────────────────────────────┤
│  SQLite (Per-Workbook Database):                                    │
│  ├─ applications (app inventory with criticality, owner, costs)    │
│  ├─ code_modules (COBOL/app modules with complexity metrics)       │
│  ├─ business_rules (extracted logic with domain & criticality)     │
│  ├─ dependencies (PERFORM/CALL/file I/O edges with types)         │
│  ├─ data_stores (file/database endpoints)                         │
│  ├─ integrations (external CALL targets)                          │
│  ├─ test_cases (parity validation coverage)                       │
│  ├─ modernization_backlog (recommendations + target tech)         │
│  └─ documentation_artifacts (generated specs, APIs, runbooks)     │
│                                                                      │
│  Key Feature: 100% Traceability                                    │
│  ├─ Every row has source_sheet + source_row + trace_id (UUID)     │
│  ├─ Audit-ready (complete chain from UI finding to source data)   │
│  └─ GDPR-compliant (one file = one complete deletion)             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Diagram

```
User Action (Upload)
    ↓
[Frontend: Upload Component]
    ├─ File selection (XLSX or COBOL)
    ├─ Client-side validation (extension check)
    └─ POST to /api/workbook/upload
        ↓
[Backend: File Router]
    ├─ Detect file type (suffix-based)
    ├─ Route to appropriate ingestion service
    └─ Store workbook_id in response
        ↓
[XLSX Ingestion Path]           [COBOL Ingestion Path]
├─ Read sheets                  ├─ Parse COBOL source
├─ Match columns (fuzzy)        ├─ Extract PROCEDURE DIV
├─ Normalize data               ├─ Track paragraph lines
├─ Validate relationships       ├─ Score complexity
└─ Synthesize SQLite            └─ Synthesize SQLite
        ↓                               ↓
     Same Schema ← ─ ─ ─ ─ ─ ─ ─ ─ ← Same Schema
        ↓
[SQLite Database]
(8 tables, full traceability)
        ↓
User navigates to "Understand" page
    ↓
[Frontend: Make GET request]
GET /api/workbook/{id}/applications
    ↓
[Backend: Query SQLite]
SELECT * FROM applications
WHERE workbook_id = {id}
    ↓
[Response: JSON entity list]
    ↓
[Frontend: Render component]
Display app cards, enable filtering
    ↓
User clicks an application
    ↓
[Frontend: Filter & display]
GET /api/workbook/{id}/modules
?application_id={app_id}
    ↓
[Backend: Query + Compute]
├─ Fetch modules from DB
├─ Build dependency graph (NetworkX)
├─ Compute complexity metrics
└─ Return enriched data
    ↓
[Frontend: Render deep-dive]
Show module details, complexity scores, test coverage
```

---

## Data Flow Sequence

### **Scenario 1: Generate Modernization Recommendations**

```
User clicks "Generate Recommendations"
    ↓
[Frontend]
POST /api/agent/analyze
{
  "workbook_id": "...",
  "agent": "modernization_strategist",
  "context": {}
}
    ↓
[Backend: Agent Orchestrator]
    ├─ 1. Fetch all entities (apps, modules, rules)
    ├─ 2. Build dependency graph (NetworkX)
    ├─ 3. Compute risks (complexity + criticality)
    ├─ 4. Rank recommendations (P1→P4)
    ├─ 5. Prepare LLM prompt with facts
    └─ 6. Call LLMaaS (GPT-4o) for narrative
        ↓
[LLMaaS Gateway (VW LLMaaS)]
    ├─ OAuth2 auth (client-credentials)
    ├─ Forward prompt to Azure OpenAI
    └─ Return narrative + reasoning
        ↓
[Backend: Format response]
{
  "findings": {
    "recommendations": [
      {
        "id": "BL-001",
        "module_id": "...",
        "title": "Modernize COBOL paragraph",
        "target_tech": "Python (FastAPI)",
        "priority": "P1"
      }
    ],
    "ai_narrative": "Based on complexity analysis...",
    "ai_generated": true
  }
}
    ↓
[Frontend]
Display recommendations with badges showing target_tech
```

### **Scenario 2: Code Modernization (COBOL → Python)**

```
User clicks "Suggest Modernized Code"
    ↓
[Frontend]
POST /api/agent/modernize-code
{
  "workbook_id": "...",
  "recommendation_id": "BL-001"
}
    ↓
[Backend: Analysis Engine]
    ├─ 1. Fetch recommendation
    ├─ 2. Get raw COBOL source file
    ├─ 3. Re-parse COBOL to extract paragraph
    ├─ 4. Prepare translation prompt
    └─ 5. Call LLMaaS
        ↓
[LLMaaS]
    └─ Return Python code + explanation
        ↓
[Frontend]
Display original COBOL ↔ Modernized Python (side-by-side)
```

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18 + TypeScript | Modern, type-safe, strong ecosystem |
| **Styling** | Tailwind CSS + shadcn/ui | Utility-first, built-in dark/light theme |
| **Icons** | Lucide React | Professional standard library, accessible |
| **3D Visualization** | Three.js + react-force-graph-3d | High-performance WebGL, 10k+ nodes |
| **Backend** | FastAPI (Python 3.9+) | Fast async, auto-docs, Pydantic validation |
| **Database** | SQLite | File-based, ACID, zero setup, easy backup |
| **Graph Analysis** | NetworkX | Mature, proven cycle/orphan detection |
| **LLM Integration** | VW LLMaaS (Azure OpenAI) | Enterprise, internal infrastructure |
| **Fallback LLM** | Ollama | Local inference, privacy-focused, offline |

---

## Performance Characteristics

### Processing Times

| Operation | Time | Scale |
|-----------|------|-------|
| XLSX Ingestion | < 2 sec | 100-sheet workbook |
| COBOL Ingestion | < 1 sec | 500-line source |
| Database Synthesis | < 500ms | 8 tables, full traceability |
| Dependency Graph Build | < 100ms | 1000+ modules |
| Risk Scoring | < 200ms | Full portfolio |
| 3D Graph Render | < 500ms | 1000+ nodes, WebGL |
| LLM Narrative | 2-5 sec | GPT-4o, LLMaaS latency |

### Scalability Profile

| Scale | Performance | Constraint |
|-------|-------------|-----------|
| **Small** (100-500 modules) | <2 sec | Best user experience |
| **Medium** (500-5k modules) | 5-15 sec | Still interactive |
| **Large** (5k+ modules) | 30-60 sec | Requires async queue |
| **Enterprise** (50k+ modules) | Scale horizontally | Shard by domain |

---

## Security & Compliance

### Data Security
- **SQLite Files**: Encrypted-at-rest optional (SQLCipher)
- **HTTPS Only**: All API calls use TLS
- **CORS**: Restricted to known frontend origins
- **Input Validation**: Pydantic models on all endpoints

### LLM Integration Security
- **OAuth2**: Client-credentials flow (no user credentials exposed)
- **Internal Gateway**: VW LLMaaS (no direct OpenAI exposure)
- **Token Management**: Cached, auto-refreshed ~30s before expiry
- **No Logging**: API keys/tokens never in logs

### Compliance Ready
- **Audit Trail**: Every entity has trace_id for regulatory audits
- **Data Residency**: SQLite stays on-premises (no cloud sync)
- **GDPR**: Full deletion (one file = complete deletion)
- **SOX**: Complete traceability for financial audits

---

## Deployment Architecture

```
Local Development:
├─ Backend: FastAPI on :8000 (uvicorn)
├─ Frontend: Vite dev server on :3000
└─ Database: SQLite in data/cache/

Docker Deployment:
├─ docker-compose up -d
├─ Backend service + Frontend service
└─ Volumes for data persistence

Production:
├─ Backend: Gunicorn + Uvicorn
├─ Frontend: Static files + nginx
├─ Database: SQLite (or PostgreSQL if scaling)
└─ Optional: Redis cache, Celery for async tasks
```

---

## Future Enhancements

1. **Multi-Language COBOL**: Copybook resolution, cross-file dependencies
2. **Additional Languages**: Java, C#, Python, Rust source ingestion
3. **Batch Operations**: Process 100+ applications in parallel
4. **Real-Time Collaboration**: WebSocket updates, concurrent editing
5. **Custom Rules Engine**: Organization-specific analysis rules
6. **Advanced Visualizations**: Sankey diagrams, dependency matrices
7. **Refactoring Assistant**: AI-suggested code improvements
8. **Cost Modeling**: Estimate modernization costs per application
9. **Compliance Automation**: Auto-generate audit reports, SOX docs
10. **Integration Hub**: Jira, GitHub, CMDB connectors

---

**For application flow & performance metrics, see [NARRATION.md](NARRATION.md)**  
**For quick-start instructions, see [QUICKSTART.md](QUICKSTART.md)**
