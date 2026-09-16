# LegacyX - Legacy Modernization Command Center

> **Enterprise-Grade AI-Powered Legacy Application Modernization Platform**

## 🎯 Mission Statement

> "We don't migrate what we don't understand."
>
> **Evidence → Intelligence → Parity → Risk-Aware Modernization**

LegacyX is a sophisticated enterprise platform for understanding, documenting, testing, and modernizing legacy applications with **complete source traceability** and **human-in-the-loop governance**.

---

## ✨ Core Features

### 1. **Upload & Ingest**
- Upload `Legacy_Modernization_Synthetic_Dataset.xlsx`
- Automatic validation and normalization
- Dynamic sheet detection and relationship inference
- Real-time metadata extraction and traceability tracking

### 2. **Command Center Dashboard**
- **Modernization Pipeline**: UNDERSTAND → DOCUMENT → MAP → TEST → MODERNIZE
- **Key Metrics**: Applications, Modules, Business Rules, Dependencies, Test Coverage
- **Coverage Analysis**: Rule test coverage, module documentation, integration mapping
- **Quick Actions**: Next steps and recommended workflows

### 3. **Estate Understanding**
- **Application Explorer**: View all applications with metadata and complexity
- **Module Analysis**: Identify hotspots, coverage gaps, and critical components
- **Business Logic**: Business rules, criticality, test coverage analysis
- **Source Traceability**: Every finding traces to source XLSX record

### 4. **Documentation Architect** (6 Specialized Agents)
- **Functional Specification**: Auto-generated from application metadata
- **Requirements**: Extracted from business rules and dependencies
- **API Specification**: Derived from integrations and data flows
- **Process Flows**: Visualized from rule conditions and actions
- **Evidence-Backed**: Every section includes "Trace to Source"
- **Human Review**: Flag insufficient evidence for manual analysis

### 5. **Dependency Detective**
- **Interactive Graph**: Zoom, pan, search, filter
- **Orphan Detection**: Identify unused modules and data stores
- **Cycle Detection**: Find circular dependencies and dead ends
- **Blast Radius**: Visualize downstream impact of changes
- **Node Details**: Drill into relationships and dependencies

### 6. **Parity Lab**
- **Parity Tests**: Auto-generated from business rules
- **Test Execution**: Compare legacy vs. modern implementations
- **Mismatch Detection**: Highlight and analyze differences
- **Source Tracing**: Each test links back to source rule
- **Critical Rules**: Focus on untested critical business rules

### 7. **Modernization Strategist**
- **Evidence-Based Recommendations**: Using criticality, complexity, dependencies
- **Risk Assessment**: Security, continuity, and complexity risks
- **Effort Estimation**: Data-driven effort and risk calculations
- **Roadmap**: Protect → Understand → Isolate → Migrate → Retire
- **Approval Workflow**: Draft, needs review, approved, rejected

### 8. **Security & Continuity Guardian**
- **Security Risks**: Hardcoded credentials (masked), PII exposure
- **Continuity Risks**: Dangling integrations, retired systems
- **Downstream Impact**: Identify critical dependencies
- **Remediation**: Specific recommendations for each risk

### 9. **Traceability Center**
- **Complete Audit Trail**: Every finding linked to source
- **Evidence Chain**: Finding → Rule/Module → Dependency → Source Sheet → Source Record
- **Change History**: Track approvals and rejections
- **Compliance Ready**: Full TRAIL documentation

### 10. **Human-in-the-Loop**
- **Draft Status**: All AI-generated items start as drafts
- **Approval Gates**: Explicit human review before execution
- **No Automatic Destructive Actions**: Migration requires manual approval
- **Audit Logging**: All decisions recorded with timestamp and user

---

## 🏗️ Architecture

### Backend (FastAPI)
- **XLSX Ingestion Service**: Robust, schema-agnostic reader
- **SQLite Storage**: Normalized data with full traceability
- **Analysis Engine**: Dependency graph, risk analysis, coverage metrics
- **Agent Orchestrator**: 6 specialized AI agents
- **REST API**: Complete data and analysis endpoints

### Frontend (React + TypeScript)
- **Modern UI**: Dark enterprise design (Navy/Black + Blue/Cyan)
- **Responsive Cards**: Dashboard, charts, tables, animations
- **Interactive Graph**: React Flow for dependency visualization
- **Real-time Updates**: WebSocket-ready architecture
- **Type-Safe**: Full TypeScript coverage

### Data Layer
- **SQLite**: Normalized multi-sheet data
- **Automated Joins**: Entity relationships
- **Trace Metadata**: Source sheet, row, and record ID per entity
- **Change Tracking**: All modifications logged

---

## 📋 Sheet Structure

The XLSX file should contain these sheets:

| Sheet | Purpose | Key Fields |
|-------|---------|-----------|
| **Applications** | System inventory | ID, Name, Status, Criticality, Complexity, Technology_Stack, Lines_of_Code |
| **Code_Modules** | Module analysis | ID, Application_ID, Name, Language, Complexity_Score, Test_Coverage, Critical_Functions |
| **Business_Rules** | Rules inventory | ID, Application_ID, Rule_Name, Condition, Action, Criticality, Test_Coverage |
| **Dependencies** | Relationships | ID, Source_ID, Source_Type, Target_ID, Target_Type, Relationship_Type, Criticality |
| **Data_Stores** | Data assets | ID, Name, Store_Type, Technology, Criticality, PII_Data, Data_Volume |
| **Integrations** | External systems | ID, Application_ID, External_System, Integration_Type, API_Version, Criticality, Status |
| **Test_Cases** | Parity tests | ID, Rule_ID, Module_ID, Test_Name, Input_Data, Expected_Output, Test_Type, Status |
| **Modernization_Backlog** | Recommendations | ID, Application_ID, Module_ID, Recommendation, Priority, Effort_Estimate, Risk_Level |
| **Documentation_Artifacts** | Generated docs | ID, Application_ID, Artifact_Type, Content, Generated_By, Generated_Date |
| **README** | Metadata | Any reference data |

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
python main.py
# Runs on http://localhost:8000
```

**Terminal 2 - Start Frontend**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Using the Application

1. **Navigate to http://localhost:3000**
2. **Upload** `Legacy_Modernization_Synthetic_Dataset.xlsx`
3. **View Dashboard** - See estate overview and pipeline progress
4. **Explore Each Stage**:
   - 🔍 **Understand**: Analyze applications, modules, business rules
   - 📋 **Document**: Generate functional specs, APIs, requirements
   - 🗺️ **Dependencies**: Visualize relationships and risks
   - ✅ **Parity**: Test compatibility and identify mismatches
   - 🚀 **Modernize**: Create risk-aware modernization plan
5. **Trace Findings**: Click any finding to see complete source traceability

---

## 🔌 API Endpoints

### Workbook Management
```
POST   /api/workbook/upload                      # Upload XLSX
GET    /api/workbook/{workbook_id}/metadata      # Get metadata
GET    /api/workbook/{workbook_id}/applications  # List applications
GET    /api/workbook/{workbook_id}/modules       # List modules
GET    /api/workbook/{workbook_id}/dependencies  # List dependencies
GET    /api/workbook/{workbook_id}/business-rules # List rules
```

### Analysis
```
POST   /api/agent/analyze                        # Run specialized agent
POST   /api/dependency-graph/analyze             # Build graph with analysis
GET    /api/workbook/{workbook_id}/dashboard-summary # Dashboard data
GET    /api/workbook/{workbook_id}/risks         # Identify risks
POST   /api/traceability/trace                   # Build trace chain
```

---

## 🎭 6 Specialized Agents

### 1. **Legacy Archaeologist**
Analyzes applications, modules, business logic, complexity, criticality, documentation, and test coverage.

**Output:**
- Architecture overview
- Business logic summary
- Critical modules and hotspots
- Complexity analysis
- Confidence score with evidence

### 2. **Documentation Architect**
Generates evidence-backed functional specs, requirements, APIs, and process flows.

**Output:**
- Functional Specification (with Trace to Source)
- Requirements Document
- API Specification
- Process Flow Diagrams
- Insufficient evidence warnings for manual review

### 3. **Dependency Detective**
Builds interactive dependency graph with orphan and cycle detection.

**Output:**
- Node/edge visualization data
- Orphan dependencies
- Circular dependencies
- Statistics and metrics
- Blast radius analysis

### 4. **Parity Engineer**
Generates parity tests from business rules and validates legacy vs. modern compatibility.

**Output:**
- Test cases per rule
- Input/expected output
- Legacy and modern results
- Pass/fail/mismatch status
- Source rule linkage

### 5. **Modernization Strategist**
Creates evidence-based modernization recommendations with risk and continuity analysis.

**Output:**
- Risk assessment
- Effort estimation
- Continuity impact
- Recommended sequence
- Approval workflow status

### 6. **Security & Continuity Guardian**
Detects security risks (hardcoded credentials, PII exposure) and continuity threats.

**Output:**
- Security risk list (credentials masked)
- Continuity risk assessment
- Downstream impact analysis
- Specific remediation steps

---

## 📊 Modernization Pipeline

```
UNDERSTAND          → DOCUMENT           → MAP                → TEST              → MODERNIZE
├─ Applications    │ ├─ Specs            │ ├─ Graph Viz      │ ├─ Parity Tests   │ ├─ Recs
├─ Modules         │ ├─ Requirements     │ ├─ Orphans        │ ├─ Comparisons    │ ├─ Roadmap
├─ Rules           │ ├─ APIs             │ ├─ Cycles         │ ├─ Mismatches     │ ├─ Risk/Effort
├─ Coverage        │ ├─ Flows            │ ├─ Blast Radius   │ └─ Coverage       │ └─ Approval
└─ Hotspots        │ └─ Traceability     │ └─ Statistics     │                   └─ Gates
```

---

## 🔒 Security & Compliance

✅ **Credential Masking**: Hardcoded credentials detected and masked  
✅ **PII Protection**: Data store PII flags with remediation  
✅ **RBAC Ready**: User-scoped data retrieval (Future: integrate with auth providers)  
✅ **Audit Logging**: All decisions recorded with timestamps  
✅ **Traceability**: Complete chain from finding to source XLSX  
✅ **No Automatic Actions**: Migration requires explicit approval  

---

## 🎨 Design Philosophy

- **Enterprise Dark Theme**: Navy/Black surfaces, Blue/Cyan accents
- **Minimal Cognitive Load**: Clear information hierarchy
- **Data-Driven**: Every finding backed by source data
- **Human-Centric**: AI assists, humans decide
- **Transparent**: Full traceability, no black boxes

---

## 📝 Example Workflow (Judge Demo)

1. Upload `Legacy_Modernization_Synthetic_Dataset.xlsx` (30s)
2. View **Command Center** dashboard with key metrics (15s)
3. Navigate to **Understand** → Identify critical undocumented module (30s)
4. Go to **Documentation** → Generate functional spec for module (45s)
5. Open **Dependencies** → Show orphan and circular dependencies (30s)
6. Switch to **Parity Lab** → Show untested critical business rules (30s)
7. Click finding → Open **Traceability Center** → Show complete audit chain (45s)
8. Go to **Modernize** → Generate risk-aware recommendations (30s)
9. Highlight recommendation approval workflow (30s)

**Total Demo Time**: ~4 minutes  
**Headline**: "We don't migrate what we don't understand."

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
│   │   │   └── analysis_engine.py       # Analysis & agents
│   │   └── models/
│   │       └── schemas.py               # Pydantic schemas
│   └── data/
│       ├── uploads/                     # Uploaded XLSX files
│       └── cache/                       # SQLite databases
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── types/
│       │   └── index.ts                 # TypeScript types
│       ├── pages/
│       │   ├── UploadPage.tsx
│       │   ├── DashboardPage.tsx
│       │   ├── UnderstandPage.tsx
│       │   ├── DocumentPage.tsx
│       │   ├── DependencyMapPage.tsx
│       │   ├── ParityLabPage.tsx
│       │   ├── ModernizationPage.tsx
│       │   └── TraceabilityPage.tsx
│       ├── components/
│       │   └── common/
│       │       └── Navigation.tsx
│       ├── utils/
│       │   └── api.ts                   # API client
│       ├── styles/
│       │   └── index.css
│       └── hooks/                       # Custom React hooks
└── README.md
```

---

## 🔄 Data Flow

```
XLSX Upload
    ↓
Validation & Normalization
    ↓
SQLite Storage (Normalized)
    ↓
Relationship Inference
    ↓
Analysis Engine
    ├── Coverage Metrics
    ├── Risk Identification
    ├── Graph Analysis
    └── Trace Building
    ↓
Agent Orchestrator
    ├── Legacy Archaeologist
    ├── Documentation Architect
    ├── Dependency Detective
    ├── Parity Engineer
    ├── Modernization Strategist
    └── Security & Continuity Guardian
    ↓
REST API → Frontend
    ↓
User Dashboard & Analysis
```

---

## 🛠️ Development

### Adding a New Agent

1. Implement agent logic in `app/services/analysis_engine.py`
2. Add route in `main.py`
3. Create frontend component in `frontend/src/components/agents/`
4. Add type definitions in `frontend/src/types/index.ts`

### Extending XLSX Support

1. Update `XLSXIngestionService._create_schema()` for new tables
2. Implement sheet-specific parsing in `_store_sheet_data()`
3. Add relationships in `_build_relationships()`

---

## 📄 License

This project is part of the i.Mobilothon 6.0 Enterprise Modernization Challenge.

---

## 💡 Contact & Support

For questions or issues, please refer to the comprehensive inline documentation and API specifications.

---

**LegacyX: Where Understanding Meets Modernization.**
