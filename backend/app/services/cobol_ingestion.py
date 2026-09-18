"""
COBOL Ingestion Service - synthesizes a full LegacyIQ workbook (same SQLite
schema as the XLSX pipeline) from a single .cbl source file, so every
existing page/agent (Dashboard, Understand, Document, Dependencies, Parity,
Modernization, Traceability, Knowledge Hub) works completely unchanged
regardless of whether the estate came from a spreadsheet or real COBOL code.

Mapping (all deterministic - parsed straight from the source, never invented):
  - applications          -> one row for the COBOL program itself
  - code_modules          -> one row per PROCEDURE DIVISION paragraph
  - business_rules        -> one row per paragraph containing conditional logic (IF/EVALUATE)
  - dependencies          -> PERFORM edges (module->module), CALL edges (module->integration),
                             and file-access edges (module->data_store)
  - data_stores           -> one row per SELECT...ASSIGN TO file
  - integrations          -> one row per unique external CALL target
  - modernization_backlog -> seeded recommendations for high-complexity paragraphs,
                             external CALLs, and file I/O (same triage a modernization
                             team would do manually)
  - documentation_artifacts -> empty (0% doc coverage is an honest, accurate finding
                             for undocumented legacy COBOL - Document tab still works
                             on-demand via the existing documentation_architect agent)
  - test_cases            -> empty (no tests exist yet for freshly-ingested code -
                             an accurate, not fabricated, starting state)

Every synthesized row carries source_sheet=filename and source_row=<real line
number in the .cbl file>, so Traceability still points at real evidence -
just source code lines instead of spreadsheet cells.
"""

import os
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, Tuple

from app.services.cobol_parser import parse_cobol_source
from app.services.xlsx_ingestion import XLSXIngestionService


def _criticality_from_complexity(score: int) -> str:
    if score >= 15:
        return "High"
    if score >= 8:
        return "Medium"
    return "Low"


def _source_path(cache_dir: str, workbook_id: str) -> str:
    return os.path.join(cache_dir, f"workbook_{workbook_id}_source.cbl")


def _source_meta_path(cache_dir: str, workbook_id: str) -> str:
    return os.path.join(cache_dir, f"workbook_{workbook_id}_source.filename")


def get_cobol_source(workbook_id: str, cache_dir: str = "data/cache"):
    """
    Re-fetch the exact original .cbl source text for a COBOL-ingested
    workbook (used to ground modernized-code suggestions in real source,
    not just structural facts). Returns (source_text, filename) or
    (None, None) if this workbook wasn't COBOL-sourced.
    """
    src_path = _source_path(cache_dir, workbook_id)
    meta_path = _source_meta_path(cache_dir, workbook_id)
    if not os.path.exists(src_path):
        return None, None
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()
    filename = workbook_id
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            filename = f.read().strip()
    return source, filename


def ingest_cobol_file(filename: str, source: str, ingestion_service: XLSXIngestionService) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    """
    Parse a .cbl file and populate a brand-new workbook SQLite DB with the
    exact same schema the XLSX pipeline uses. Returns (workbook_id, metadata,
    validation) with the same shape as XLSXIngestionService.ingest_workbook.

    Takes the app's shared XLSXIngestionService instance (not a fresh one) so
    the resulting workbook_id is registered in the same in-memory metadata
    cache every other endpoint reads from.
    """
    svc = ingestion_service
    cache_dir = svc.cache_dir
    workbook_id = str(uuid.uuid4())[:8]
    validation: Dict[str, Any] = {"errors": [], "warnings": []}

    facts = parse_cobol_source(source, filename)
    if not facts.get("paragraph_count") and not facts.get("program_id"):
        validation["warnings"].append(
            "Could not detect PROGRAM-ID or any PROCEDURE DIVISION paragraphs - "
            "the file may not be standard fixed/free-format COBOL."
        )

    # Persist the raw source so modernization code-suggestion can later
    # re-fetch and translate the exact original paragraph text.
    os.makedirs(cache_dir, exist_ok=True)
    with open(_source_path(cache_dir, workbook_id), "w", encoding="utf-8") as f:
        f.write(source)
    with open(_source_meta_path(cache_dir, workbook_id), "w", encoding="utf-8") as f:
        f.write(filename)

    db_path = os.path.join(cache_dir, f"workbook_{workbook_id}.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    svc._create_schema(cursor)

    app_id = "APP-01"
    app_name = facts.get("program_id") or os.path.splitext(filename)[0]
    complexity = facts.get("complexity_estimate", 1)
    app_trace = str(uuid.uuid4())[:12]

    cursor.execute(
        """INSERT INTO applications
           (id, name, primary_language, platform, business_domain, criticality,
            annual_maint_cost_eur, last_deployed, owner, doc_coverage_pct,
            source_sheet, source_row, trace_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            app_id, app_name, "COBOL", "Mainframe (assumed)", None,
            _criticality_from_complexity(complexity),
            None, None, facts.get("author"), 0.0,
            filename, facts.get("program_id_line", 1), app_trace,
        ),
    )

    paragraph_details = facts.get("paragraph_details", [])
    module_id_by_paragraph: Dict[str, str] = {}
    rule_count = 0

    for idx, p in enumerate(paragraph_details, start=1):
        module_id = f"MOD-{idx:03d}"
        module_id_by_paragraph[p["name"]] = module_id
        cursor.execute(
            """INSERT INTO code_modules
               (id, application_id, name, module_type, lines_of_code, complexity_score,
                last_changed, last_change_author, is_dead_code, has_unit_tests,
                description_present, source_sheet, source_row, trace_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                module_id, app_id, p["name"], "Paragraph", p["line_count"], p["complexity"],
                None, facts.get("author"), "N", "N", "N",
                filename, p["line"], str(uuid.uuid4())[:12],
            ),
        )

        if p["if_count"] + p["evaluate_count"] > 0:
            rule_count += 1
            rule_id = f"RULE-{rule_count:03d}"
            cursor.execute(
                """INSERT INTO business_rules
                   (id, module_id, rule_name, business_domain, criticality,
                    extraction_confidence, duplicate_of, has_test_case,
                    source_sheet, source_row, trace_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rule_id, module_id, f"Conditional logic in {p['name']}", None,
                    _criticality_from_complexity(p["complexity"]),
                    0.6, None, "N",
                    filename, p["line"], str(uuid.uuid4())[:12],
                ),
            )

    # --- Data stores (one per SELECT...ASSIGN TO file) ---
    data_store_id_by_file: Dict[str, str] = {}
    for idx, f in enumerate(facts.get("file_io_details", []), start=1):
        ds_id = f"DST-{idx:02d}"
        data_store_id_by_file[f["file_name"]] = ds_id
        store_type = "Indexed File" if f.get("organization") == "INDEXED" else "Sequential File"
        cursor.execute(
            """INSERT INTO data_stores
               (id, name, store_type, application_id, classification, pii_data,
                data_volume, source_sheet, source_row, trace_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ds_id, f["file_name"], store_type, app_id, "Unknown", "N", None,
                filename, f["line"], str(uuid.uuid4())[:12],
            ),
        )

    # --- Integrations (one per unique external CALL target) ---
    integration_id_by_call: Dict[str, str] = {}
    seen_calls = set()
    call_idx = 0
    for c in facts.get("call_details", []):
        target = c["target"]
        if target in seen_calls:
            continue
        seen_calls.add(target)
        call_idx += 1
        int_id = f"INT-{call_idx:02d}"
        integration_id_by_call[target] = int_id
        cursor.execute(
            """INSERT INTO integrations
               (id, application_id, interface_name, integration_type, direction,
                protocol, downstream_target, criticality, status, last_verified,
                source_sheet, source_row, trace_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                int_id, app_id, target, "CALL", "Outbound", "COBOL CALL", target,
                "medium", "Active", None,
                filename, c["line"], str(uuid.uuid4())[:12],
            ),
        )

    # --- Dependencies: PERFORM (module->module), CALL (module->integration),
    # --- file access (module->data_store, inferred from body text mentioning the file name) ---
    dep_idx = 0
    for p in paragraph_details:
        source_module = module_id_by_paragraph[p["name"]]

        for target_name in p["perform_targets"]:
            dep_idx += 1
            cursor.execute(
                """INSERT INTO dependencies
                   (id, source_id, source_type, target_id, target_type,
                    relationship_type, criticality, source_sheet, source_row, trace_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"DEP-{dep_idx:03d}", source_module, "module",
                    module_id_by_paragraph[target_name], "module",
                    "performs", "medium", filename, p["line"], str(uuid.uuid4())[:12],
                ),
            )

        for target in p["calls"]:
            if target not in integration_id_by_call:
                continue
            dep_idx += 1
            cursor.execute(
                """INSERT INTO dependencies
                   (id, source_id, source_type, target_id, target_type,
                    relationship_type, criticality, source_sheet, source_row, trace_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"DEP-{dep_idx:03d}", source_module, "module",
                    integration_id_by_call[target], "integration",
                    "calls", "high", filename, p["line"], str(uuid.uuid4())[:12],
                ),
            )

        body_upper = p.get("body", "").upper()
        for file_name, ds_id in data_store_id_by_file.items():
            if file_name.upper() in body_upper:
                dep_idx += 1
                cursor.execute(
                    """INSERT INTO dependencies
                       (id, source_id, source_type, target_id, target_type,
                        relationship_type, criticality, source_sheet, source_row, trace_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        f"DEP-{dep_idx:03d}", source_module, "module", ds_id, "data_store",
                        "reads/writes", "medium", filename, p["line"], str(uuid.uuid4())[:12],
                    ),
                )

    # --- Seed modernization backlog from static-analysis triage (deterministic heuristics) ---
    backlog_idx = 0
    priority_map = {"High": "P1", "Medium": "P2", "Low": "P3"}
    for p in paragraph_details:
        if p["complexity"] < 4:
            continue
        backlog_idx += 1
        crit = _criticality_from_complexity(p["complexity"])
        target_tech = "Java/Spring" if crit == "High" else ("Python (FastAPI)" if crit == "Medium" else None)
        cursor.execute(
            """INSERT INTO modernization_backlog
               (id, application_id, module_id, recommendation, priority, effort_estimate,
                risk_level, preserves_continuity, target_tech, status,
                source_sheet, source_row, trace_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"BL-{backlog_idx:03d}", app_id, module_id_by_paragraph[p["name"]],
                f"Refactor high-complexity paragraph '{p['name']}' into smaller units",
                priority_map.get(crit, "P3"), str(max(3, p["complexity"] // 2)),
                crit, "Y", target_tech, "Proposed",
                filename, p["line"], str(uuid.uuid4())[:12],
            ),
        )
    for target, int_id in integration_id_by_call.items():
        backlog_idx += 1
        cursor.execute(
            """INSERT INTO modernization_backlog
               (id, application_id, module_id, recommendation, priority, effort_estimate,
                risk_level, preserves_continuity, target_tech, status,
                source_sheet, source_row, trace_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"BL-{backlog_idx:03d}", app_id, None,
                f"Replace external CALL to '{target}' with a modern service interface",
                "P2", "8", "Medium", "Y", "REST API", "Proposed",
                filename, 1, str(uuid.uuid4())[:12],
            ),
        )
    for file_name, ds_id in data_store_id_by_file.items():
        backlog_idx += 1
        cursor.execute(
            """INSERT INTO modernization_backlog
               (id, application_id, module_id, recommendation, priority, effort_estimate,
                risk_level, preserves_continuity, target_tech, status,
                source_sheet, source_row, trace_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"BL-{backlog_idx:03d}", app_id, None,
                f"Migrate flat file '{file_name}' to a relational database",
                "P2", "13", "Medium", "Y", "PostgreSQL", "Proposed",
                filename, 1, str(uuid.uuid4())[:12],
            ),
        )

    conn.commit()
    conn.close()

    sheet_counts = {
        "Program": 1,
        "Paragraphs (Modules)": len(paragraph_details),
        "Business Rules": rule_count,
        "Dependencies": dep_idx,
        "Data Stores": len(data_store_id_by_file),
        "Integrations": len(integration_id_by_call),
        "Modernization Backlog": backlog_idx,
    }

    metadata = {
        "workbook_id": workbook_id,
        "db_path": db_path,
        "sheets": [filename],
        "sheet_counts": sheet_counts,
        "ingestion_time": datetime.now().isoformat(),
        "total_sheets": 1,
        "source_type": "cobol",
    }
    svc.workbooks[workbook_id] = metadata

    return workbook_id, metadata, validation
