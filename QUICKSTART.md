# LegacyIQ Quick Start Guide

## 🎯 5-Minute Setup

### Step 1: Verify Prerequisites
```bash
python --version      # Should be 3.9+
node --version        # Should be 18+
npm --version         # Should be 8+
```

### Step 2: Generate Sample Data
```bash
cd LegacyX
python generate_sample_data.py
# Output: Legacy_Modernization_Synthetic_Dataset.xlsx
```

### Step 2.5: (Optional) Configure AI Narratives
The 6 agents work fully without this step (evidence-only view). To see live
LLM-generated narratives in the "AI Insight" panels, add LLM credentials to
`backend/.env` before starting the backend — see "LLM Configuration" in
[README.md](README.md) for the exact variables (VW LLMaaS primary, Ollama
local fallback).

### Step 3: Start the Application

**On Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**On Windows:**
```cmd
start.bat
```

**Manual (Any OS):**
```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
# Runs on http://localhost:8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Step 4: Access the Application
1. Open browser to **http://localhost:3000**
2. You should see the LegacyIQ upload page
3. Upload the generated `Legacy_Modernization_Synthetic_Dataset.xlsx`

---

## 🎭 4-Minute Demo Flow

### Demo Scenario: Understanding an Enterprise Application Estate

1. **Upload Dataset** (30 seconds)
   - Click upload area
   - Select `Legacy_Modernization_Synthetic_Dataset.xlsx`
   - Watch validation complete
   - Redirects to dashboard

2. **View Command Center** (30 seconds)
   - See estate overview: 5 applications, 25+ modules
   - Notice pipeline: UNDERSTAND → DOCUMENT → MAP → TEST → MODERNIZE
   - Point out coverage metrics: Rule test coverage, module documentation
   - Highlight next steps

3. **Understand the Estate** (30 seconds)
   - Navigate to "Understand" page
   - Show application explorer
   - Highlight complexity hotspots
   - Point out undocumented modules

4. **Generate Documentation** (45 seconds)
   - Go to "Documentation Architect"
   - Click "Generate" for Functional Specification
   - Observe AI-generated sections
   - Highlight "Evidence insufficient" warning sections
   - Show source trace links

5. **View Dependencies** (30 seconds)
   - Navigate to "Dependencies"
   - Observe dependency graph visualization
   - Click on "Orphans" filter
   - Show orphan nodes that don't connect
   - Click on "Cycles" to highlight circular dependencies

6. **Security & Risk Analysis** (30 seconds)
   - Still on dependencies page
   - Point out critical dependencies
   - Navigate to "Modernize" page
   - Show critical risks highlighted
   - Explain PII data store risks

7. **Parity Testing** (30 seconds)
   - Go to "Parity Lab"
   - Show generated test cases from business rules
   - Point out mismatches between legacy/modern
   - Highlight untested critical rules

8. **Modernization Strategy** (30 seconds)
   - Navigate to "Modernize" page
   - Show evidence-based recommendations
   - Display roadmap: Protect → Understand → Isolate → Migrate → Retire
   - Highlight approval workflow status

9. **Traceability** (45 seconds)
   - Go to "Traceability Center"
   - Click on any finding
   - Show complete trace chain
   - Trace back to source XLSX sheet and row
   - Demonstrate: "Finding → Rule → Dependency → Source Sheet"

10. **Closing Statement** (15 seconds)
    - Headline: "We don't migrate what we don't understand"
    - Tagline: "Evidence → Intelligence → Parity → Risk-Aware Modernization"
    - Show that all findings are evidence-backed and traceable

**Total Duration: ~4 minutes**

---

## 📊 What to Show in Each Section

### Command Center Dashboard
- **Key Metrics**: 5 Applications, 25 Modules, 40+ Business Rules
- **Pipeline Progress**: Test coverage at 45%, Documentation at 60%
- **Next Steps**: 5 actionable items from Understand → Modernize

### Understand the Estate
- **Applications**: Legacy systems in Java 6, Python 2.7, VB.NET
- **Modules**: Complexity scores ranging 3-9.5
- **Hotspots**: Identify 2-3 high-complexity, low-test-coverage modules
- **Rules**: Show critical rules with no test coverage

### Documentation Generated
```
Functional Specification - OrderManagement
├─ 1. Overview (from Applications sheet)
├─ 2. Business Context (from Description field)
├─ 3. Architecture (from Technology_Stack field)
├─ [Evidence insufficient - Needs human review]
├─ Approve | Export | Regenerate
```

### Dependencies & Risks
- **Orphan Nodes**: 2-3 modules with no dependencies
- **Circular Dependencies**: Show 1-2 cycles
- **Blast Radius**: Highlight critical path that would break if module changed

### Security & Continuity Risks
```
Critical Risks (4):
- Database contains PII (Data_Volume: 10TB) → Implement encryption
- Deprecated integration still in use → Plan migration
- High-complexity module untested → Refactor first
- No documentation for critical workflow → Generate and review
```

### Parity Tests
```
Business Rules: 40 Total
Test Coverage: 18 Tested (45%)
Mismatches: 2
└─ Rule_003: Legacy returns X, Modern returns Y → Investigate
└─ Rule_012: Legacy accepts null, Modern rejects → Harmonize
```

### Modernization Strategy
```
Recommendation Priorities:
1. [CRITICAL] Refactor OrderManagement modules (Complexity 9.2, Test 0%)
   - Effort: 2-3 months | Risk: High | Evidence: 15 references
   - Approval: Draft [Needs Review]

2. [HIGH] Migrate BillingSystem to cloud
   - Effort: 1-2 months | Risk: Medium
   - Approval: Pending Review
```

### Traceability Center
```
Finding: "Undocumented Critical Module"
↓ Trace Back:
├─ Module: MOD0015 (Complexity: 8.7, Test Coverage: 12%)
├─ Source Sheet: Code_Modules
├─ Source Row: 16
├─ Application: APP001 (OrderManagement)
├─ Dependencies: 12 modules depend on this
└─ Risk Assessment: Critical - No documentation, high complexity
```

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill existing process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Frontend won't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS is enabled (should be in main.py)
# Verify API base URL in frontend/src/utils/api.ts
```

### XLSX Upload fails
```bash
# Ensure file has correct sheet names
# Check file is not corrupted
# Verify Python has openpyxl installed

cd backend
pip install openpyxl --upgrade
```

### Module import errors
```bash
# Rebuild frontend
cd frontend
rm -rf node_modules
npm install
npm run build
```

---

## 📋 Sample Data Schema

When you generate sample data, these are created:

| Entity | Count | Purpose |
|--------|-------|---------|
| Applications | 5 | Represents legacy systems |
| Modules | 25-40 | Code components with complexity |
| Business Rules | 40-60 | Core business logic |
| Dependencies | 25-35 | Relationships between entities |
| Data Stores | 5 | Databases and data assets |
| Integrations | 15-20 | External system connections |
| Test Cases | 10-20 | Parity test definitions |
| Recommendations | 10-15 | Modernization items |

---

## 🎨 UI Navigation Map

```
Upload Page (/)
├── Dashboard (/dashboard)
│   ├── Understand (/understand)
│   ├── Document (/document)
│   ├── Dependencies (/dependencies)
│   ├── Parity (/parity)
│   ├── Modernize (/modernize)
│   └── Traceability (/traceability)
└── [Navigation header with links to all pages]
```

---

## 💡 Tips for Best Experience

1. **Start with Dashboard**: Gives complete overview
2. **Follow the Pipeline**: UNDERSTAND → DOCUMENT → MAP → TEST → MODERNIZE
3. **Use Filters**: On dependency graph, use filters to focus on specific relationships
4. **Read Evidence**: Every recommendation includes source data
5. **Click to Trace**: Click any finding to see its complete source trace
6. **Approval Workflow**: Note that all recommendations start as "Draft"

---

## 📞 Common Questions

### Q: Can I use my own data?
**A**: Yes! Create an Excel file with the expected sheet names and column headers. See `generate_sample_data.py` for the schema.

### Q: How do I export findings?
**A**: Each generated document (Functional Spec, API Spec, etc.) has an "Export" button.

### Q: Can I modify recommendations?
**A**: In the UI, recommendations can be set to "Needs Review", "Approved", or "Rejected". Modifications would require manual editing in the backend.

### Q: How do I add more data?
**A**: Edit the XLSX file and re-upload. The backend will re-ingest and update all analysis.

### Q: Is this production-ready?
**A**: This is a demonstration/prototype. For production, add: authentication, database persistence, audit logging, error handling, and API rate limiting.

---

## 🚀 Next Steps

1. **Customize Data**: Replace sample data with your actual application metadata
2. **Add Authentication**: Integrate with corporate identity provider
3. **Extend Agents**: Add more specialized analysis agents
4. **Integrate with CI/CD**: Auto-ingest data from build systems
5. **Custom Dashboards**: Create role-specific views for different teams

---

**Welcome to LegacyIQ! 🎉**

For detailed documentation, see [README.md](README.md)
