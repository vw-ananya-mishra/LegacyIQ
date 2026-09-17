# LegacyIQ - Legacy Modernization Command Center

> **Enterprise-Grade AI-Powered Legacy Application Modernization Platform**

## 🎯 Mission Statement

> "We don't migrate what we don't understand."
>
> **Evidence → Intelligence → Parity → Risk-Aware Modernization**

LegacyIQ is a sophisticated enterprise platform for understanding, documenting, testing, and modernizing legacy applications with **complete source traceability** and **human-in-the-loop governance**.

---

## ✨ Core Features

### 1. **Upload & Ingest**
- Upload `Legacy_Modernization_Synthetic_Dataset.xlsx`
- Automatic validation and normalization
- Dynamic sheet detection and relationship inference
- Real-time metadata extraction and traceability tracking

### 2. **Command Center Dashboard**
- **Modernization Pipeline**: UNDERSTAND → DOCUMENT → MAP → TEST → MODERNIZE, each stage showing a real, data-driven completion percentage (see [Modernization Pipeline Metrics](#-modernization-pipeline-metrics))
- **Key Metrics**: Applications, Modules, Business Rules, Dependencies — all cards are clickable and deep-link to the relevant page
- **Coverage Analysis**: Rule test coverage, module test coverage, documentation coverage — cards are clickable and deep-link to the relevant page
- **Quick Actions**: Next steps and recommended workflows

### 3. **Estate Understanding**
- **Application Explorer**: Language, platform, business domain, criticality, owner, doc coverage %, annual maintenance cost
- **Module Analysis**: Type, lines of code, cyclomatic complexity, unit test presence, dead-code flag
- **Business Logic**: Rule summary, domain, criticality, test-case presence, extraction confidence, duplicate detection
- **Application Selector**: Modules and Business Rules tabs can be filtered down to a single application
- **Source Traceability**: Every finding traces to its source XLSX sheet/row

### 4. **Documentation Architect** (1 of 6 Specialized Agents)
- **Application Selector**: Pick which application to generate documentation for (previously always defaulted to the first application)
- **Functional Specification**: Overview, business context, architecture, business rules, critical rules requiring sign-off, code modules
- **API Specification**: Integration endpoints, data flows/dependencies, inactive/deprecated endpoints
- **Evidence-Backed**: Every section is derived directly from ingested data with a source-sheet/row trace

### 5. **Dependency Detective**
- **Interactive 3D Graph** (WebGL, via `react-force-graph-3d`): drag to rotate, scroll to zoom, click a node to focus the camera on it
- **Application Selector**: Narrow the graph to one application's modules plus their immediate neighbors (data stores, integrations, cross-app links)
- **Filters**: All / Modules / Orphans / Cycles
- **Upstream / Downstream**: Selecting a node shows named upstream dependencies ("what this depends on") and downstream dependents ("what depends on this"), not just raw in/out-degree counts
- **Orphan & Cycle Detection**: Computed over the full graph (including isolated nodes that never appear in any dependency edge)

### 6. **Parity Lab**
- **Parity Tests**: Read directly from the `Test_Cases` sheet (`expected_result`, `legacy_result`, `parity_status`)
- **Status Buckets**: Pass / Fail / Mismatch / Pending, derived from the sheet's own `parity_status` column
- **Source Tracing**: Each test links back to its business rule and module

### 7. **Modernization Strategist**
- **Application Selector**: Filter generated recommendations down to one application
- **Evidence-Based Recommendations**: Target technology, effort points, risk level, priority (P1–P4), continuity preservation flag
- **Risk List**: Full portfolio of identified risks (see [Risk Identification](#-risk-identification))
- **Roadmap**: Protect → Understand → Isolate → Migrate → Retire

### 8. **Traceability Center**
- **Complete Audit Trail**: Applications, Modules, Business Rules, and Dependencies are all traceable
- **Evidence Chain**: Entity → Related Entities (owning app / implementing module / test cases / dependency edges) → Source Sheet → Source Row → Trace ID
- **Compliance Ready**: Full trail from any UI finding back to a specific XLSX cell

### 9. **Human-in-the-Loop**
- **Draft Status**: Backlog items track their own status from the sheet (`Proposed`, `In Progress`, `Done`, …)
- **No Automatic Destructive Actions**: Migration requires manual approval
- **Traceable Decisions**: All findings are reproducible from source data, not model hallucination

---

## 🏗️ Architecture

### Backend (FastAPI)
- **XLSX Ingestion Service**: Schema-aware reader mapped directly to the dataset's real column names, with case/spacing-tolerant fallback lookups
- **SQLite Storage**: Normalized data with full traceability (`source_sheet`, `source_row`, `trace_id` on every row)
- **Analysis Engine**: Dependency graph (NetworkX), risk analysis, dashboard/coverage metrics, trace-chain builder
- **Agent Orchestrator**: 6 specialized AI agents — deterministic SQL/graph analysis for facts, plus a live LLM (VW LLMaaS GPT-4o, Ollama fallback) that generates the narrative/reasoning layer on top of those facts
- **REST API**: Complete data and analysis endpoints

### Frontend (React + TypeScript)
- **Modern UI**: Dark enterprise design (Navy/Black + Blue/Cyan), built with Tailwind CSS
- **3D Dependency Graph**: `react-force-graph-3d` (three.js under the hood) with cinematic auto-orbit, click-to-focus camera, and directional particles on critical edges
- **Application Selectors**: Understand, Document, Dependency Map, and Modernization pages all support filtering by application where it meaningfully reduces clutter
- **Type-Safe**: Full TypeScript coverage

### Data Layer
- **SQLite**: Normalized multi-sheet data, one `.db` file per uploaded workbook (`backend/data/cache/workbook_{id}.db`)
- **Trace Metadata**: Source sheet, row, and trace ID per entity
- **Risks**: Computed on-the-fly from current data (not persisted) each time they're requested

---

## 📋 Sheet Structure

The XLSX file should contain these sheets (column names match the ingestion code exactly):

| Sheet | Purpose | Key Columns |
|-------|---------|-----------|
| **Applications** | System inventory | `app_id`, `app_name`, `primary_language`, `platform`, `business_domain`, `criticality`, `annual_maint_cost_eur`, `last_deployed`, `owner`, `doc_coverage_pct` |
| **Code_Modules** | Module analysis | `module_id`, `app_id`, `module_name`, `module_type`, `lines_of_code`, `cyclomatic_complexity`, `last_changed`, `last_change_author`, `is_dead_code`, `has_unit_tests`, `description_present` |
| **Business_Rules** | Rules inventory | `rule_id`, `module_id`, `rule_summary`, `business_domain`, `criticality`, `extraction_confidence`, `duplicate_of`, `has_test_case` |
| **Dependencies** | Relationships | `dependency_id`, `source_module_id`, `target_type`, `target_id`, `dependency_kind`, `is_runtime_critical` |
| **Data_Stores** | Data assets | `store_id`, `store_name`, `store_type`, `owning_app_id`, `classification`, `pii_present`, `record_count_est` |
| **Integrations** | External systems | `integration_id`, `app_id`, `interface_name`, `integration_type`, `direction`, `protocol`, `downstream_target`, `status`, `last_verified` |
| **Test_Cases** | Parity tests | `test_id`, `rule_id`, `module_id`, `test_name`, `test_type`, `expected_result`, `legacy_result`, `parity_status`, `last_run` |
| **Modernization_Backlog** | Recommendations | `backlog_id`, `app_id`, `module_id`, `recommendation`, `target_tech`, `effort_points`, `risk_level`, `preserves_continuity`, `priority`, `status` |
| **Documentation_Artifacts** | Tribal knowledge / docs | `doc_id`, `app_id`, `doc_type`, `doc_title`, `last_updated`, `author`, `excerpt` |
| **README** | Metadata | Free-text reference sheet, not ingested |
| **Answer_Key** *(optional)* | Ground-truth seeded scenarios for validation | Not ingested; used only for manual QA of the analysis engine |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- pip / npm

### Installation

1. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

**Terminal 1 - Start Backend**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
# Runs on http://localhost:8000
```

**Terminal 2 - Start Frontend**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Using the Application

## 🤖 LLM Configuration (AI Agent Narratives)

The 6 agents generate their narrative/reasoning text via a real LLM. Configure one or both providers in `backend/.env` (git-ignored, never commit real values — see `.env.example` for placeholder names):

```bash
# Primary provider: VW Group LLMaaS (OAuth2 client-credentials + OpenAI-compatible API)
LLMAAS_IDP_URL=https://idp.cloud.vwgroup.com/auth/realms/kums-mfa/protocol/openid-connect/token
LLMAAS_CLIENT_ID=<your-client-id>
LLMAAS_CLIENT_SECRET=<your-client-secret>
LLMAAS_API_KEY=<your-api-key>
LLMAAS_BASE_URL=https://llmapi.ai.vwgroup.com
LLMAAS_MODEL=gpt-4o

# Secondary/local fallback: Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

**Provider selection order**: `llm_service.generate_narrative()` tries VW LLMaaS first, falls back to Ollama if LLMaaS isn't configured/reachable, and returns `None` if neither is available — in which case the UI simply omits the AI Insight panel and shows the deterministic facts only. No code changes are needed to switch providers; the app auto-detects which env vars are present.

Without any LLM configured, the app is still fully functional — the LLM layer only adds narrative summaries on top of the deterministic findings that already power every page.

---
3. **View Dashboard** - See estate overview and pipeline progress
4. **Explore Each Stage**:
   - 🔍 **Understand**: Analyze applications, modules, business rules (filterable by application)
   - 📋 **Document**: Generate functional specs and API specs for a chosen application
   - 🗺️ **Dependencies**: Explore the 3D dependency graph, filter by application, inspect upstream/downstream links
   - ✅ **Parity**: Review parity test results (pass/fail/mismatch) sourced directly from `Test_Cases`
   - 🚀 **Modernize**: Review risks and generate/filter modernization recommendations
5. **Trace Findings**: Use the Traceability Center to trace any application, module, rule, or dependency back to its source row

---

## 🔌 API Endpoints

### Workbook Management
```
POST   /api/workbook/upload                             # Upload XLSX
GET    /api/workbook/{workbook_id}/metadata              # Get metadata
GET    /api/workbook/{workbook_id}/applications          # List applications
GET    /api/workbook/{workbook_id}/modules?app_id=...     # List modules (optional app filter)
GET    /api/workbook/{workbook_id}/dependencies           # List dependencies
GET    /api/workbook/{workbook_id}/business-rules         # List rules
GET    /api/workbook/{workbook_id}/documentation-artifacts # List tribal-knowledge docs
```

### Analysis
```
POST   /api/agent/analyze                            # Run a specialized agent
POST   /api/dependency-graph/analyze                  # Build graph with orphan/cycle analysis
GET    /api/workbook/{workbook_id}/dashboard-summary  # Dashboard + pipeline metrics
GET    /api/workbook/{workbook_id}/risks              # Identify risks (computed on demand)
POST   /api/traceability/trace                        # Build trace chain for any entity
```

---

## 🎭 6 Specialized Agents

All agents live in `AgentOrchestrator` (`backend/app/services/analysis_engine.py`). Each agent first computes deterministic facts by querying the ingested SQLite data directly (reproducible, auditable), then calls `llm_service.generate_narrative()` to have a real LLM (VW LLMaaS / GPT-4o, with local Ollama as fallback) write a grounded natural-language narrative on top of those facts. The narrative is attached as `findings.ai_narrative` and rendered in the UI via `AIInsightPanel`; if no LLM provider is available the app degrades gracefully and just shows the deterministic facts.

### 1. **Legacy Archaeologist**
Analyzes a single application: its modules, business rules (joined via module → application), architecture, and complexity hotspots.

### 2. **Documentation Architect**
Generates a **Functional Specification** or **API Specification** for a selected application, built from real applications/modules/rules/integrations/dependencies data.

### 3. **Dependency Detective**
Builds the full dependency graph (via `AnalysisEngine.build_dependency_graph`) with orphan and cycle detection.

### 4. **Parity Engineer**
Reads `Test_Cases` directly and normalizes `parity_status` into `pass` / `mismatch` / `pending` buckets for the UI.

### 5. **Modernization Strategist**
Reads `Modernization_Backlog` and maps priority (`P1`–`P4`), effort points, target tech, and continuity flag into UI-ready recommendations; also surfaces the current risk list for context.

### 6. **Security & Continuity Guardian**
Filters the shared risk list down to `security` and `continuity` risk types (PII exposure, dangling/inactive integrations).

---

## 📊 Modernization Pipeline Metrics

Each pipeline stage on the dashboard reflects a real, data-driven signal instead of a placeholder:

| Stage | Metric | Meaning |
|---|---|---|
| **Understand** | 100% once applications exist | The estate is ingested and fully explorable |
| **Document** | Average `doc_coverage_pct` across applications | Existing legacy documentation coverage from the source data |
| **Map** | `1 − (orphans + cycle nodes) / total nodes` | How "clean"/resolved the dependency graph is |
| **Test** | % business rules with a test case | Parity-validation readiness |
| **Modernize** | % backlog items with status Done/Completed | Real modernization progress |

---

## 🛡️ Risk Identification

`AnalysisEngine.identify_risks()` computes risks directly from the ingested data (not persisted — recomputed on every request):

- **Undocumented critical modules** — `description_present = 'N'` inside a High-criticality application
- **High-complexity hotspots** — `cyclomatic_complexity >= 38` with no unit tests and no docs
- **Dead code** — `is_dead_code = 'Y'`
- **Orphan / dangling dependencies** — an edge pointing to a non-existent module/data-store/integration/application
- **Untested critical business rules** — `criticality = 'High'` and `has_test_case = 'N'`
- **Duplicated business logic** — `duplicate_of` set on a rule
- **PII exposure** — `pii_data = 'Y'` on a data store
- **Unmapped data store** — owned by a non-existent application
- **Parity mismatches** — test cases with `status = 'mismatch'`
- **Modernization breaks continuity** — backlog items with `preserves_continuity = 'N'`

---

## 🔒 Security & Compliance

✅ **PII Flagging**: Data-store PII flags surfaced as risks with remediation guidance
✅ **Traceability**: Complete chain from finding to source XLSX row
✅ **No Automatic Actions**: Migration requires explicit approval via backlog status
✅ **Parameterized Queries**: All SQLite access uses parameterized queries (no string-built SQL)
✅ **LLM Secrets Isolation**: LLMaaS credentials live only in git-ignored `backend/.env`, never in source control or logs
✅ **OAuth2 Token Flow**: Short-lived, cached access tokens for LLMaaS — no static API key sent per-request
✅ **TLS Everywhere**: IDP token endpoint and LLMaaS gateway are called exclusively over HTTPS
✅ **PII Minimization in Prompts**: Only PII *flags* (booleans) are sent to the LLM, never raw personal data values
✅ **Graceful LLM Failure**: If the LLM is unreachable, the app falls back to evidence-only display — never a broken or partial state

---

## 🎨 Design Philosophy

- **Enterprise Dark Theme**: Navy/Black surfaces, Blue/Cyan accents
- **Minimal Cognitive Load**: Clear information hierarchy, filterable views once data volume grows
- **Data-Driven**: Every finding backed by source data, verified against the seeded ground-truth scenarios
- **Transparent**: Full traceability, no black boxes

---

## 📦 Project Structure

```
LegacyX/
├── backend/
│   ├── main.py                          # FastAPI entry point
│   ├── requirements.txt                 # Python dependencies
│   ├── app/
│   │   ├── services/
│   │   │   ├── xlsx_ingestion.py        # XLSX reader & normalizer
│   │   │   └── analysis_engine.py       # AnalysisEngine + AgentOrchestrator (6 agents)
│   │   └── models/
│   │       └── schemas.py               # Pydantic schemas
│   └── data/
│       ├── uploads/                     # Uploaded XLSX files (temp)
│       └── cache/                       # One SQLite DB per workbook
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── context/
│       │   └── WorkbookContext.tsx      # Active workbook, persisted to localStorage
│       ├── types/
│       │   └── index.ts                 # TypeScript types
│       ├── pages/
│       │   ├── UploadPage.tsx
│       │   ├── DashboardPage.tsx
│       │   ├── UnderstandPage.tsx
│       │   ├── DocumentPage.tsx
│       │   ├── DependencyMapPage.tsx    # 3D graph (react-force-graph-3d)
│       │   ├── ParityLabPage.tsx
│       │   ├── ModernizationPage.tsx
│       │   └── TraceabilityPage.tsx
│       ├── components/
│       │   └── common/
│       │       └── Navigation.tsx
│       ├── utils/
│       │   └── api.ts                   # API client
│       └── styles/
│           └── index.css
└── README.md
```

---

## 🔄 Data Flow

```
XLSX Upload
    ↓
Validation & Column-aware Normalization
    ↓
SQLite Storage (Normalized, with trace metadata)
    ↓
Analysis Engine
    ├── Coverage Metrics
    ├── Risk Identification
    ├── Dependency Graph (with orphan/cycle detection)
    └── Trace-Chain Building
    ↓
Agent Orchestrator (per agent)
    ├── Legacy Archaeologist
    ├── Documentation Architect
    ├── Dependency Detective
    ├── Parity Engineer
    ├── Modernization Strategist
    └── Security & Continuity Guardian
        │
        ├── 1. Deterministic facts (SQL / NetworkX queries)
        └── 2. llm_service.generate_narrative() → VW LLMaaS (GPT-4o) → ai_narrative
    ↓
REST API → Frontend
    ↓
User Dashboard & Analysis (facts + AI narrative via AIInsightPanel)
```

---

## 🛠️ Development

### Adding a New Agent

1. Implement agent logic as a method on `AgentOrchestrator` in `app/services/analysis_engine.py`
2. Add an `elif` branch in `run_agent_analysis` (`main.py`) dispatching to it
3. Call it from the frontend via `agentAPI.analyzeWithAgent(workbookId, agentType, context)`

### Extending XLSX Support

1. Update `XLSXIngestionService._create_schema()` for new/changed tables
2. Implement sheet-specific parsing in `_store_sheet_data()`, using `_find_column_value()` for resilient column matching
3. Update `AnalysisEngine`/`AgentOrchestrator` methods and the corresponding frontend pages to match any new fields

---

## 📄 License

This project is part of the i.Mobilothon 6.0 Enterprise Modernization Challenge.

---

## 💡 Contact & Support

For questions or issues, please refer to the comprehensive inline documentation and API specifications.

---

**LegacyIQ: Where Understanding Meets Modernization.**
