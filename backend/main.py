"""
LegacyX Backend - Enterprise Legacy Modernization Platform
Core XLSX Ingestion and Analysis Engine
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import tempfile
import os
import json
from datetime import datetime

# Import core components
from app.services.xlsx_ingestion import XLSXIngestionService
from app.services.analysis_engine import AnalysisEngine, AgentOrchestrator
from app.models.schemas import (
    WorkbookMetadata, ApplicationSchema, ModuleSchema, 
    DependencySchema, RiskSchema
)

# Initialize FastAPI app
app = FastAPI(
    title="LegacyX Backend",
    description="AI-Powered Legacy Application Modernization Platform",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
ingestion_service = XLSXIngestionService()
analysis_engine = AnalysisEngine()
agent_orchestrator = AgentOrchestrator()

# ============================================================================
# MODELS
# ============================================================================

class UploadResponse(BaseModel):
    status: str
    workbook_id: str
    sheets: Dict[str, int]
    validation_errors: List[str]
    validation_warnings: List[str]
    timestamp: str

class AnalysisRequest(BaseModel):
    workbook_id: str
    agent_type: str
    context: Dict[str, Any] = {}

class AnalysisResponse(BaseModel):
    agent_type: str
    status: str
    findings: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    confidence: float
    trace: List[Dict[str, Any]]

class DependencyGraphRequest(BaseModel):
    workbook_id: str
    filters: Optional[List[str]] = None
    orphan_detection: bool = True
    cycle_detection: bool = True

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)
    print("[OK] LegacyX Backend initialized")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/workbook/upload", response_model=UploadResponse)
async def upload_workbook(file: UploadFile = File(...)):
    """
    Upload and ingest Legacy_Modernization_Synthetic_Dataset.xlsx
    
    - Validates Excel structure
    - Reads all sheets dynamically
    - Creates relationships
    - Stores normalized data
    - Returns metadata and validation report
    """
    try:
        # Save uploaded file
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Ingest workbook
        workbook_id, metadata, validation = ingestion_service.ingest_workbook(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return UploadResponse(
            status="success" if not validation['errors'] else "completed_with_errors",
            workbook_id=workbook_id,
            sheets=metadata['sheet_counts'],
            validation_errors=validation['errors'],
            validation_warnings=validation['warnings'],
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/workbook/{workbook_id}/metadata")
async def get_workbook_metadata(workbook_id: str):
    """Get workbook metadata and structure"""
    try:
        metadata = ingestion_service.get_metadata(workbook_id)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/workbook/{workbook_id}/applications")
async def get_applications(workbook_id: str):
    """Get all applications from workbook"""
    try:
        apps = ingestion_service.get_applications(workbook_id)
        return {"applications": apps}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/workbook/{workbook_id}/modules")
async def get_modules(workbook_id: str, app_id: Optional[str] = None):
    """Get modules, optionally filtered by application"""
    try:
        modules = ingestion_service.get_modules(workbook_id, app_id)
        return {"code_modules": modules, "modules": modules}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/workbook/{workbook_id}/dependencies")
async def get_dependencies(workbook_id: str):
    """Get all dependency relationships"""
    try:
        deps = ingestion_service.get_dependencies(workbook_id)
        return {"dependencies": deps}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/workbook/{workbook_id}/business-rules")
async def get_business_rules(workbook_id: str):
    """Get all business rules"""
    try:
        rules = ingestion_service.get_business_rules(workbook_id)
        return {"business_rules": rules}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/agent/analyze", response_model=AnalysisResponse)
async def run_agent_analysis(request: AnalysisRequest):
    """
    Execute specialized agent analysis
    
    Agent types:
    - legacy_archaeologist: Deep analysis of applications, modules, business logic
    - documentation_architect: Generate functional specs, requirements, APIs
    - dependency_detective: Map dependencies, find orphans, detect cycles
    - parity_engineer: Generate and validate parity tests
    - modernization_strategist: Create modernization recommendations
    - security_continuity_guardian: Identify security and continuity risks
    """
    try:
        # Get workbook data
        metadata = ingestion_service.get_metadata(request.workbook_id)
        
        # Execute appropriate agent
        if request.agent_type == "legacy_archaeologist":
            findings, evidence = agent_orchestrator.legacy_archaeologist_analyze(
                request.workbook_id, request.context
            )
        elif request.agent_type == "documentation_architect":
            findings, evidence = agent_orchestrator.documentation_architect_generate(
                request.workbook_id, request.context
            )
        elif request.agent_type == "dependency_detective":
            findings, evidence = agent_orchestrator.dependency_detective_analyze(
                request.workbook_id, request.context
            )
        elif request.agent_type == "parity_engineer":
            findings, evidence = agent_orchestrator.parity_engineer_generate(
                request.workbook_id, request.context
            )
        elif request.agent_type == "modernization_strategist":
            findings, evidence = agent_orchestrator.modernization_strategist_recommend(
                request.workbook_id, request.context
            )
        elif request.agent_type == "security_continuity_guardian":
            findings, evidence = agent_orchestrator.security_continuity_guardian_detect(
                request.workbook_id, request.context
            )
        else:
            raise ValueError(f"Unknown agent type: {request.agent_type}")
        
        return AnalysisResponse(
            agent_type=request.agent_type,
            status="success",
            findings=findings,
            evidence=evidence['evidence_list'],
            confidence=evidence['confidence'],
            trace=evidence['trace']
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/dependency-graph/analyze")
async def analyze_dependency_graph(request: DependencyGraphRequest):
    """
    Analyze dependency graph with cycle and orphan detection
    """
    try:
        graph_data = analysis_engine.build_dependency_graph(
            request.workbook_id,
            filters=request.filters,
            detect_orphans=request.orphan_detection,
            detect_cycles=request.cycle_detection
        )
        
        return {
            "status": "success",
            "nodes": graph_data['nodes'],
            "edges": graph_data['edges'],
            "orphan_nodes": graph_data.get('orphan_nodes', []),
            "cycles": graph_data.get('cycles', []),
            "statistics": graph_data['statistics']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/workbook/{workbook_id}/dashboard-summary")
async def get_dashboard_summary(workbook_id: str):
    """Get command center dashboard summary"""
    try:
        summary = analysis_engine.generate_dashboard_summary(workbook_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/workbook/{workbook_id}/risks")
async def get_risks(workbook_id: str):
    """Get all identified risks: security, continuity, complexity"""
    try:
        risks = analysis_engine.identify_risks(workbook_id)
        return {"risks": risks}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/traceability/trace")
async def trace_finding(workbook_id: str, finding_id: str, finding_type: str):
    """
    Trace any finding back to source XLSX
    Returns: Output → Rule/Module → Dependency → Source Sheet → Source Record
    """
    try:
        trace_chain = analysis_engine.build_trace_chain(
            workbook_id, finding_id, finding_type
        )
        return {"trace": trace_chain}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
