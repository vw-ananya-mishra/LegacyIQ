"""
Pydantic models and schemas for LegacyX
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class WorkbookMetadata(BaseModel):
    workbook_id: str
    sheets: List[str]
    sheet_counts: Dict[str, int]
    ingestion_time: str
    total_sheets: int

class ApplicationSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    criticality: str
    complexity: str
    technology_stack: Optional[str]
    lines_of_code: Optional[int]
    last_modified: Optional[str]

class ModuleSchema(BaseModel):
    id: str
    application_id: str
    name: str
    description: Optional[str]
    language: str
    lines_of_code: Optional[int]
    complexity_score: float
    test_coverage: Optional[float]
    critical_functions: Optional[int]

class BusinessRuleSchema(BaseModel):
    id: str
    application_id: str
    rule_name: str
    description: Optional[str]
    condition: Optional[str]
    action: Optional[str]
    criticality: str
    test_coverage: Optional[str]

class DependencySchema(BaseModel):
    id: str
    source_id: str
    source_type: str
    target_id: str
    target_type: str
    relationship_type: str
    criticality: Optional[str]
    description: Optional[str]

class RiskSchema(BaseModel):
    id: str
    entity_id: str
    entity_type: str
    risk_type: str
    risk_description: str
    severity: str
    remediation: Optional[str]
