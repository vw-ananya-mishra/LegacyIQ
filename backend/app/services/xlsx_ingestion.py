"""
XLSX Ingestion Service
Reads and normalizes Legacy_Modernization_Synthetic_Dataset.xlsx
Creates dynamic relationships between entities
"""

import openpyxl
from openpyxl.utils import get_column_letter
import pandas as pd
import uuid
import json
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import sqlite3
import os

class XLSXIngestionService:
    """
    Robust XLSX reader with:
    - Dynamic sheet detection
    - Schema validation
    - Relationship inference
    - Normalized data storage
    - Traceability metadata
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self.workbooks = {}  # Store loaded workbook metadata
        os.makedirs(cache_dir, exist_ok=True)
    
    def ingest_workbook(self, file_path: str) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Main ingestion pipeline:
        1. Load XLSX
        2. Validate structure
        3. Extract sheets
        4. Normalize data
        5. Create relationships
        6. Store in SQLite
        7. Build indices
        
        Returns: (workbook_id, metadata, validation_report)
        """
        workbook_id = str(uuid.uuid4())[:8]
        validation = {"errors": [], "warnings": []}
        metadata = {}
        
        try:
            # Load workbook
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheets = wb.sheetnames
            
            if not sheets:
                validation['errors'].append("No sheets found in workbook")
                return workbook_id, {}, validation
            
            # Store sheet counts
            metadata['sheet_counts'] = {}
            for sheet_name in sheets:
                ws = wb[sheet_name]
                row_count = ws.max_row - 1  # Exclude header
                metadata['sheet_counts'][sheet_name] = row_count
            
            # Initialize SQLite database for this workbook
            db_path = os.path.join(self.cache_dir, f"workbook_{workbook_id}.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create schema
            self._create_schema(cursor)
            
            # Extract and normalize data from each sheet
            sheet_data = {}
            
            # Expected sheets
            expected_sheets = [
                'Applications', 'Code_Modules', 'Business_Rules', 'Dependencies',
                'Data_Stores', 'Integrations', 'Test_Cases', 'Modernization_Backlog',
                'Documentation_Artifacts', 'README'
            ]
            
            for expected_sheet in expected_sheets:
                # Try variations of sheet name
                sheet_name = None
                for s in sheets:
                    if s.lower() == expected_sheet.lower() or s.lower() == expected_sheet.lower().replace('_', ' '):
                        sheet_name = s
                        break
                
                if sheet_name:
                    try:
                        data = self._extract_sheet_data(wb[sheet_name], sheet_name)
                        sheet_data[sheet_name] = data
                        self._store_sheet_data(cursor, sheet_name, data)
                    except Exception as e:
                        validation['warnings'].append(f"Error processing sheet {sheet_name}: {str(e)}")
                else:
                    validation['warnings'].append(f"Sheet '{expected_sheet}' not found")
            
            # Build relationships
            self._build_relationships(cursor, sheet_data)
            
            conn.commit()
            
            # Store metadata
            metadata['workbook_id'] = workbook_id
            metadata['db_path'] = db_path
            metadata['sheets'] = sheets
            metadata['ingestion_time'] = datetime.now().isoformat()
            metadata['total_sheets'] = len(sheets)
            
            self.workbooks[workbook_id] = metadata
            
            return workbook_id, metadata, validation
        
        except Exception as e:
            validation['errors'].append(f"Ingestion failed: {str(e)}")
            return workbook_id, metadata, validation
    
    def _create_schema(self, cursor):
        """Create SQLite schema for normalized data"""
        
        # Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                name TEXT,
                primary_language TEXT,
                platform TEXT,
                business_domain TEXT,
                criticality TEXT,
                annual_maint_cost_eur REAL,
                last_deployed TEXT,
                owner TEXT,
                doc_coverage_pct REAL,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT
            )
        """)
        
        # Code Modules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_modules (
                id TEXT PRIMARY KEY,
                application_id TEXT,
                name TEXT,
                module_type TEXT,
                lines_of_code INTEGER,
                complexity_score REAL,
                last_changed TEXT,
                last_change_author TEXT,
                is_dead_code TEXT,
                has_unit_tests TEXT,
                description_present TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        
        # Business Rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_rules (
                id TEXT PRIMARY KEY,
                module_id TEXT,
                rule_name TEXT,
                business_domain TEXT,
                criticality TEXT,
                extraction_confidence REAL,
                duplicate_of TEXT,
                has_test_case TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT,
                FOREIGN KEY(module_id) REFERENCES code_modules(id)
            )
        """)
        
        # Dependencies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                source_type TEXT,
                target_id TEXT,
                target_type TEXT,
                relationship_type TEXT,
                criticality TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT
            )
        """)
        
        # Data Stores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_stores (
                id TEXT PRIMARY KEY,
                name TEXT,
                store_type TEXT,
                application_id TEXT,
                classification TEXT,
                pii_data TEXT,
                data_volume TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT
            )
        """)
        
        # Integrations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrations (
                id TEXT PRIMARY KEY,
                application_id TEXT,
                interface_name TEXT,
                integration_type TEXT,
                direction TEXT,
                protocol TEXT,
                downstream_target TEXT,
                criticality TEXT,
                status TEXT,
                last_verified TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        
        # Test Cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_cases (
                id TEXT PRIMARY KEY,
                rule_id TEXT,
                module_id TEXT,
                test_name TEXT,
                test_type TEXT,
                expected_output TEXT,
                legacy_result TEXT,
                status TEXT,
                last_run TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT
            )
        """)
        
        # Risks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risks (
                id TEXT PRIMARY KEY,
                entity_id TEXT,
                entity_type TEXT,
                risk_type TEXT,
                risk_description TEXT,
                severity TEXT,
                remediation TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT
            )
        """)
        
        # Modernization Backlog table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS modernization_backlog (
                id TEXT PRIMARY KEY,
                application_id TEXT,
                module_id TEXT,
                recommendation TEXT,
                priority TEXT,
                effort_estimate TEXT,
                risk_level TEXT,
                preserves_continuity TEXT,
                target_tech TEXT,
                status TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
        
        # Documentation Artifacts table (tribal knowledge, runbooks, design docs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentation_artifacts (
                id TEXT PRIMARY KEY,
                application_id TEXT,
                doc_type TEXT,
                doc_title TEXT,
                last_updated TEXT,
                author TEXT,
                excerpt TEXT,
                source_sheet TEXT,
                source_row INTEGER,
                trace_id TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id)
            )
        """)
    
    def _normalize_column_name(self, name: str) -> str:
        """Normalize column name to match expected format (snake_case)"""
        if not name:
            return ""
        # Convert to title case and remove spaces/special chars, but keep format flexible
        return str(name).strip()
    
    def _find_column_value(self, row_dict: Dict, *possible_names: str):
        """Find value in row using multiple possible column names (case-insensitive)"""
        for possible_name in possible_names:
            # Try exact match first
            if possible_name in row_dict:
                return row_dict[possible_name]
            
            # Try case-insensitive match
            for key, value in row_dict.items():
                if key and str(key).lower() == str(possible_name).lower():
                    return value
            
            # Try without spaces
            normalized_possible = str(possible_name).lower().replace('_', '').replace(' ', '')
            for key, value in row_dict.items():
                if key and str(key).lower().replace('_', '').replace(' ', '') == normalized_possible:
                    return value
        
        return None
    
    def _extract_sheet_data(self, worksheet, sheet_name: str) -> List[Dict[str, Any]]:
        """Extract data from worksheet with headers"""
        data = []
        
        # Get headers from first row
        headers = []
        for cell in worksheet[1]:
            headers.append(cell.value)
        
        # Extract data rows
        for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=False), start=2):
            row_data = {}
            for col_idx, cell in enumerate(row):
                header = headers[col_idx] if col_idx < len(headers) else f"col_{col_idx}"
                row_data[header] = cell.value if cell else None
            
            if any(v is not None for v in row_data.values()):  # Skip empty rows
                row_data['_source_row'] = row_idx
                data.append(row_data)
        
        return data
    
    def _store_sheet_data(self, cursor, sheet_name: str, data: List[Dict[str, Any]]):
        """Store normalized sheet data in appropriate tables"""
        
        # Determine target table based on sheet name
        sheet_lower = sheet_name.lower()
        
        if 'application' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                app_id = self._find_column_value(row, 'app_id', 'Application_ID', 'ID') or f"app_{idx}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO applications 
                    (id, name, primary_language, platform, business_domain, criticality,
                     annual_maint_cost_eur, last_deployed, owner, doc_coverage_pct,
                     source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    app_id,
                    self._find_column_value(row, 'app_name', 'Name', 'Application_Name'),
                    self._find_column_value(row, 'primary_language', 'Language'),
                    self._find_column_value(row, 'platform', 'Platform'),
                    self._find_column_value(row, 'business_domain', 'Business_Domain'),
                    self._find_column_value(row, 'criticality', 'Criticality'),
                    self._find_column_value(row, 'annual_maint_cost_eur', 'Annual_Maint_Cost_EUR'),
                    self._find_column_value(row, 'last_deployed', 'Last_Deployed', 'Last_Modified'),
                    self._find_column_value(row, 'owner', 'Owner'),
                    self._find_column_value(row, 'doc_coverage_pct', 'Doc_Coverage_Pct'),
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
        
        elif 'module' in sheet_lower or 'code' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                module_id = self._find_column_value(row, 'module_id', 'Module_ID', 'ID') or f"mod_{idx}"
                app_id = self._find_column_value(row, 'app_id', 'Application_ID', 'application_id')
                
                cursor.execute("""
                    INSERT OR REPLACE INTO code_modules
                    (id, application_id, name, module_type, lines_of_code,
                     complexity_score, last_changed, last_change_author,
                     is_dead_code, has_unit_tests, description_present,
                     source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    module_id,
                    app_id,
                    self._find_column_value(row, 'module_name', 'Name', 'Module_Name'),
                    self._find_column_value(row, 'module_type', 'Module_Type'),
                    self._find_column_value(row, 'lines_of_code', 'Lines_of_Code', 'LOC'),
                    self._find_column_value(row, 'cyclomatic_complexity', 'Complexity_Score', 'Complexity'),
                    self._find_column_value(row, 'last_changed', 'Last_Modified', 'Modified'),
                    self._find_column_value(row, 'last_change_author', 'Last_Change_Author'),
                    self._find_column_value(row, 'is_dead_code', 'Is_Dead_Code'),
                    self._find_column_value(row, 'has_unit_tests', 'Has_Unit_Tests'),
                    self._find_column_value(row, 'description_present', 'Description_Present'),
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
        
        elif 'business' in sheet_lower or 'rule' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                rule_id = self._find_column_value(row, 'rule_id', 'Rule_ID', 'ID') or f"rule_{idx}"
                module_id = self._find_column_value(row, 'module_id', 'Module_ID')
                
                cursor.execute("""
                    INSERT OR REPLACE INTO business_rules
                    (id, module_id, rule_name, business_domain, criticality,
                     extraction_confidence, duplicate_of, has_test_case,
                     source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule_id,
                    module_id,
                    self._find_column_value(row, 'rule_summary', 'Rule_Name', 'Name'),
                    self._find_column_value(row, 'business_domain', 'Business_Domain'),
                    self._find_column_value(row, 'criticality', 'Criticality'),
                    self._find_column_value(row, 'extraction_confidence', 'Extraction_Confidence'),
                    self._find_column_value(row, 'duplicate_of', 'Duplicate_Of'),
                    self._find_column_value(row, 'has_test_case', 'Has_Test_Case'),
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
        
        elif 'dependenc' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                dep_id = self._find_column_value(row, 'dependency_id', 'Dependency_ID', 'ID') or f"dep_{idx}"
                source_id = self._find_column_value(row, 'source_module_id', 'Source_ID', 'source_id')
                target_id = self._find_column_value(row, 'target_id', 'Target_ID')
                
                # Skip if source or target is None
                if source_id is None or target_id is None:
                    continue
                
                is_runtime_critical = self._find_column_value(row, 'is_runtime_critical', 'Is_Runtime_Critical')
                criticality = 'critical' if str(is_runtime_critical).strip().upper() == 'Y' else 'medium'
                
                cursor.execute("""
                    INSERT OR REPLACE INTO dependencies
                    (id, source_id, source_type, target_id, target_type,
                     relationship_type, criticality, source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    dep_id,
                    source_id,
                    'module',
                    target_id,
                    str(self._find_column_value(row, 'target_type', 'Target_Type') or 'unknown').strip().lower().replace(' ', '_'),
                    self._find_column_value(row, 'dependency_kind', 'Relationship_Type'),
                    criticality,
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
        
        elif 'data_store' in sheet_lower or 'store' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                store_id = self._find_column_value(row, 'store_id', 'DataStore_ID', 'ID') or f"store_{idx}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO data_stores
                    (id, name, store_type, application_id, classification, pii_data,
                     data_volume, source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    store_id,
                    self._find_column_value(row, 'store_name', 'Name'),
                    self._find_column_value(row, 'store_type', 'Store_Type'),
                    self._find_column_value(row, 'owning_app_id', 'Application_ID'),
                    self._find_column_value(row, 'classification', 'Classification'),
                    self._find_column_value(row, 'pii_present', 'PII_Data'),
                    self._find_column_value(row, 'record_count_est', 'Data_Volume'),
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
        
        elif 'integration' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                int_id = self._find_column_value(row, 'integration_id', 'Integration_ID', 'ID') or f"int_{idx}"
                app_id = self._find_column_value(row, 'app_id', 'Application_ID')
                
                cursor.execute("""
                    INSERT OR REPLACE INTO integrations
                    (id, application_id, interface_name, integration_type, direction,
                     protocol, downstream_target, criticality, status, last_verified,
                     source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int_id,
                    app_id,
                    self._find_column_value(row, 'interface_name', 'External_System'),
                    self._find_column_value(row, 'integration_type', 'Integration_Type'),
                    self._find_column_value(row, 'direction', 'Direction'),
                    self._find_column_value(row, 'protocol', 'Protocol'),
                    self._find_column_value(row, 'downstream_target', 'Downstream_Target'),
                    self._find_column_value(row, 'criticality', 'Criticality'),
                    self._find_column_value(row, 'status', 'Status'),
                    self._find_column_value(row, 'last_verified', 'Last_Verified'),
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
        
        elif 'test' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                test_id = self._find_column_value(row, 'test_id', 'Test_ID', 'ID') or f"test_{idx}"
                rule_id = self._find_column_value(row, 'rule_id', 'Rule_ID')
                module_id = self._find_column_value(row, 'module_id', 'Module_ID')
                
                parity_status = self._find_column_value(row, 'parity_status', 'Parity_Status')
                status = 'pass' if str(parity_status).strip().lower() == 'match' else \
                         'mismatch' if str(parity_status).strip().lower() == 'mismatch' else 'pending'
                
                cursor.execute("""
                    INSERT OR REPLACE INTO test_cases
                    (id, rule_id, module_id, test_name, test_type,
                     expected_output, legacy_result, status, last_run,
                     source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_id,
                    rule_id,
                    module_id,
                    self._find_column_value(row, 'test_name', 'Test_Name'),
                    self._find_column_value(row, 'test_type', 'Test_Type'),
                    self._find_column_value(row, 'expected_result', 'Expected_Output'),
                    self._find_column_value(row, 'legacy_result', 'Legacy_Result'),
                    status,
                    self._find_column_value(row, 'last_run', 'Last_Run'),
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
        
        elif 'modernization' in sheet_lower or 'backlog' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                recommendation_id = self._find_column_value(row, 'backlog_id', 'ID', 'Recommendation_ID') or f"rec_{idx}"
                app_id = self._find_column_value(row, 'app_id', 'Application_ID')
                module_id = self._find_column_value(row, 'module_id', 'Module_ID')
                
                cursor.execute("""
                    INSERT OR REPLACE INTO modernization_backlog
                    (id, application_id, module_id, recommendation, priority,
                     effort_estimate, risk_level, preserves_continuity, target_tech, status,
                     source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    recommendation_id,
                    app_id,
                    module_id,
                    self._find_column_value(row, 'recommendation', 'Recommendation'),
                    self._find_column_value(row, 'priority', 'Priority'),
                    self._find_column_value(row, 'effort_points', 'Effort_Estimate'),
                    self._find_column_value(row, 'risk_level', 'Risk_Level'),
                    self._find_column_value(row, 'preserves_continuity', 'Preserves_Continuity'),
                    self._find_column_value(row, 'target_tech', 'Target_Tech'),
                    self._find_column_value(row, 'status', 'Status'),
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
        
        elif 'documentation' in sheet_lower or 'artifact' in sheet_lower:
            for idx, row in enumerate(data):
                trace_id = str(uuid.uuid4())[:12]
                doc_id = self._find_column_value(row, 'doc_id', 'Doc_ID', 'ID') or f"doc_{idx}"
                app_id = self._find_column_value(row, 'app_id', 'Application_ID')
                
                cursor.execute("""
                    INSERT OR REPLACE INTO documentation_artifacts
                    (id, application_id, doc_type, doc_title, last_updated, author, excerpt,
                     source_sheet, source_row, trace_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    app_id,
                    self._find_column_value(row, 'doc_type', 'Doc_Type'),
                    self._find_column_value(row, 'doc_title', 'Doc_Title'),
                    self._find_column_value(row, 'last_updated', 'Last_Updated'),
                    self._find_column_value(row, 'author', 'Author'),
                    self._find_column_value(row, 'excerpt', 'Excerpt'),
                    sheet_name,
                    row.get('_source_row'),
                    trace_id
                ))
    
    def _build_relationships(self, cursor, sheet_data: Dict[str, List[Dict]]):
        """Infer and build relationships between entities"""
        # This is called after all data is stored to create linkages
        pass
    
    def get_metadata(self, workbook_id: str) -> Dict[str, Any]:
        """Get workbook metadata"""
        return self.workbooks.get(workbook_id, {})
    
    def get_applications(self, workbook_id: str) -> List[Dict]:
        """Retrieve all applications"""
        db_path = self._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM applications")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_modules(self, workbook_id: str, app_id: Optional[str] = None) -> List[Dict]:
        """Retrieve modules, optionally filtered by application"""
        db_path = self._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if app_id:
            cursor.execute("SELECT * FROM code_modules WHERE application_id = ?", (app_id,))
        else:
            cursor.execute("SELECT * FROM code_modules")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_dependencies(self, workbook_id: str) -> List[Dict]:
        """Retrieve all dependencies"""
        db_path = self._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM dependencies")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_business_rules(self, workbook_id: str) -> List[Dict]:
        """Retrieve all business rules"""
        db_path = self._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM business_rules")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_documentation_artifacts(self, workbook_id: str) -> List[Dict]:
        """Retrieve all documentation artifacts (tribal knowledge, runbooks, design docs)"""
        db_path = self._get_db_path(workbook_id)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documentation_artifacts")
        return [dict(row) for row in cursor.fetchall()]
    
    def _get_db_path(self, workbook_id: str) -> str:
        """Get database path for workbook"""
        return os.path.join(self.cache_dir, f"workbook_{workbook_id}.db")
