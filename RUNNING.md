# 🚀 LegacyIQ - LIVE & OPERATIONAL

## Status: ✅ BOTH BACKEND & FRONTEND RUNNING

---

## 🌐 Access Points

### Frontend Application
**URL:** http://localhost:3000  
**Status:** ✅ Running (Vite Dev Server)  
**Port:** 3000  

### Backend API
**URL:** http://localhost:8000  
**Status:** ✅ Running (FastAPI)  
**Port:** 8000  

### API Documentation
**URL:** http://localhost:8000/docs  
**Type:** Swagger UI (auto-generated)  

---

## 🎯 What to Do Next

### 1. Open Frontend in Browser
```
http://localhost:3000
```
You'll see the LegacyIQ Command Center with:
- Upload page for XLSX files
- Dashboard with estate metrics
- 8 pipeline stage pages

### 2. Upload Test Data
The test file is ready at:
```
Legacy_Modernization_Synthetic_Dataset.xlsx
```
- Contains 5 applications, 28 modules, 53 rules
- Pre-generated in project root

### 3. Explore the Application
After upload, you can:
- View applications in estate (OrderManagement, BillingSystem, etc.)
- See dependency graph (27 nodes, 24 edges, 0 orphans, 0 cycles)
- Check coverage metrics (32% test gap identified)
- Trace findings back to XLSX source

### 4. Test API Directly
```powershell
# Get applications
Invoke-WebRequest -Uri "http://localhost:8000/api/workbook/18225f8f/applications"

# Get dashboard summary
Invoke-WebRequest -Uri "http://localhost:8000/api/workbook/18225f8f/dashboard-summary"

# Get dependency graph
$body = @{ workbook_id = "18225f8f" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/dependency-graph/analyze" `
  -Method Post -ContentType "application/json" -Body $body
```

---

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Port:** 8000
- **Framework:** FastAPI
- **Database:** SQLite (normalized 8-table schema)
- **Features:**
  - XLSX ingestion with dynamic sheet detection
  - Dependency graph analysis (NetworkX)
  - Risk identification
  - Complete source traceability
  - 6 specialized analysis agents

### Frontend (React/TypeScript/Vite)
- **Port:** 3000
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **UI Library:** Tailwind CSS
- **Pages:** 8 (Upload, Dashboard, Understand, Document, Dependencies, Parity, Modernize, Traceability)

---

## 📊 Current Data

**Workbook ID:** 18225f8f  
**Dataset:** Legacy_Modernization_Synthetic_Dataset.xlsx  

**Ingested Data:**
- 5 Applications (critical legacy systems)
- 28 Code Modules (VB.NET, C++, Java mix)
- 53 Business Rules (core logic to preserve)
- 25 Dependencies (integration points)
- 27 Dependency Graph Nodes
- 24 Dependency Edges
- 0 Orphaned Components
- 0 Circular Dependencies
- 32% Test Coverage (gap identified for action)

---

## 🔧 Running Services

### Terminal 1: Backend (Already Running)
```bash
cd backend
.\venv\Scripts\activate
python main.py
# Running on http://localhost:8000
```

### Terminal 2: Frontend (Already Running)
```bash
cd frontend
npm run dev
# OR
.\node_modules\.bin\vite.cmd
# Running on http://localhost:3000
```

---

## 📝 Demo Sequence

1. **Open Frontend:** http://localhost:3000
2. **Upload XLSX:** Legacy_Modernization_Synthetic_Dataset.xlsx
3. **View Dashboard:** See 5 apps, 28 modules, 53 rules metrics
4. **Explore Applications:** OrderManagement, BillingSystem, etc.
5. **Map Dependencies:** 27 nodes, 24 edges, no orphans/cycles
6. **Check Coverage:** 32% test gap identified
7. **Trace Finding:** Show source_sheet + source_row traceability
8. **Message:** "We don't migrate what we don't understand"

---

## 🛑 Stopping the Application

### Kill Frontend
```bash
# In frontend terminal: Ctrl+C
```

### Kill Backend
```bash
# In backend terminal: Ctrl+C
# Or:
Get-Process -Name python | Stop-Process -Force
```

---

## ✨ Key Features Demonstrated

✅ Single XLSX source of truth  
✅ Complete source traceability  
✅ Dependency graph with orphan/cycle detection  
✅ Test coverage metrics  
✅ Beautiful enterprise UI  
✅ 6 specialized analysis agents (backend ready)  
✅ Risk-aware assessment  
✅ Human-in-the-loop governance  

---

## 📚 Documentation

See project root for:
- `README.md` - Full feature guide
- `QUICKSTART.md` - Setup & demo flow
- `ARCHITECTURE.md` - System design
- `TEST_RESULTS.md` - Comprehensive test report
- `LIVE_DEMO_READY.md` - Demo guide
- `DELIVERY_SUMMARY.md` - Executive overview

---

**Ready for Demo! 🎉**

*LegacyIQ v1.0.0 — Enterprise Legacy Modernization Command Center*
