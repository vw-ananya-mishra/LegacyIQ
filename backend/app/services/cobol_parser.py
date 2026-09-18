"""
COBOL Source Analyzer - lightweight structural parser for a single .cbl file.

This is NOT a full COBOL compiler/parser (that's out of scope) - it uses
line-oriented regex heuristics to extract the structural facts a modernization
engineer cares about first: PROGRAM-ID, divisions present, data items,
PROCEDURE DIVISION paragraphs (each with its own line range, local
complexity, and PERFORM targets), external CALLs, COPY (copybook) includes,
file I/O (SELECT...ASSIGN TO), embedded SQL blocks, and a whole-program
complexity estimate.

Every fact here carries a `line` (1-based) so downstream ingestion can build
real traceability (source_sheet=filename, source_row=line) exactly like the
XLSX pipeline does with sheet/row - except the "row" points at actual source
code, not a spreadsheet cell.
"""

import re
from typing import Any, Dict, List


_SCOPE_TERMINATORS = {
    'END', 'STOP', 'EXIT', 'CONTINUE', 'ELSE', 'END-IF', 'END-READ', 'END-WRITE',
    'END-REWRITE', 'END-DELETE', 'END-EVALUATE', 'END-PERFORM', 'END-CALL',
    'END-COMPUTE', 'END-STRING', 'END-UNSTRING', 'END-SEARCH', 'END-ADD',
    'END-SUBTRACT', 'END-MULTIPLY', 'END-DIVIDE', 'END-ACCEPT', 'END-DISPLAY',
    'END-EXEC', 'END-START', 'END-RETURN', 'WHEN-OTHER',
}


def _line_of(source: str, char_index: int) -> int:
    """1-based line number for a character offset into `source`."""
    return source.count('\n', 0, char_index) + 1


def parse_cobol_source(source: str, filename: str) -> Dict[str, Any]:
    lines = source.splitlines()
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('*')]

    def find_first(pattern: str):
        m = re.search(pattern, source, re.IGNORECASE)
        if not m:
            return None, None
        return m.group(1).strip().rstrip('.'), _line_of(source, m.start(1))

    program_id, program_id_line = find_first(r'PROGRAM-ID\.\s*([A-Za-z0-9_-]+)')
    author, _ = find_first(r'AUTHOR\.\s*([^\n]+)')

    divisions = [
        div for div in ('IDENTIFICATION', 'ENVIRONMENT', 'DATA', 'PROCEDURE')
        if re.search(rf'{div}\s+DIVISION', source, re.IGNORECASE)
    ]

    data_items: List[Dict[str, Any]] = []
    for m in re.finditer(
        r'^\s*(0[1-9]|[1-4][0-9])\s+([A-Za-z0-9_-]+)\s*(?:PIC(?:TURE)?\s+([A-Za-z0-9\(\)V9XS.,+-]+))?',
        source, re.IGNORECASE | re.MULTILINE,
    ):
        data_items.append({
            "level": m.group(1), "name": m.group(2), "pic": m.group(3),
            "line": _line_of(source, m.start(2)),
        })

    # --- File I/O ---
    file_selects = []
    for m in re.finditer(
        r'SELECT\s+([A-Za-z0-9_-]+)\s+ASSIGN\s+TO\s+([A-Za-z0-9_."\'-]+)(?:[^.]*ORGANIZATION\s+IS\s+([A-Za-z]+))?',
        source, re.IGNORECASE | re.DOTALL,
    ):
        file_selects.append({
            "file_name": m.group(1), "assigned_to": m.group(2).strip('"\''),
            "organization": (m.group(3) or 'SEQUENTIAL').upper(),
            "line": _line_of(source, m.start(1)),
        })

    copybooks = []
    for m in re.finditer(r'COPY\s+([A-Za-z0-9_-]+)', source, re.IGNORECASE):
        copybooks.append({"name": m.group(1), "line": _line_of(source, m.start(1))})

    sql_blocks = len(re.findall(r'EXEC\s+SQL', source, re.IGNORECASE))

    # --- Paragraph segmentation: split PROCEDURE DIVISION body at each header ---
    proc_match = re.search(r'PROCEDURE\s+DIVISION[^.]*\.\s*', source, re.IGNORECASE)
    paragraphs: List[Dict[str, Any]] = []
    all_calls: List[Dict[str, Any]] = []

    if proc_match:
        proc_start = proc_match.end()
        proc_body = source[proc_start:]
        headers = list(re.finditer(r'^\s*([A-Za-z0-9][A-Za-z0-9_-]*)\s*\.\s*$', proc_body, re.MULTILINE))
        headers = [h for h in headers if h.group(1).upper() not in _SCOPE_TERMINATORS]

        for idx, h in enumerate(headers):
            name = h.group(1)
            body_start = h.end()
            body_end = headers[idx + 1].start() if idx + 1 < len(headers) else len(proc_body)
            body = proc_body[body_start:body_end]
            start_line = _line_of(source, proc_start + h.start())
            end_line = _line_of(source, proc_start + body_end)

            if_count = len(re.findall(r'\bIF\b', body, re.IGNORECASE))
            evaluate_count = len(re.findall(r'\bEVALUATE\b', body, re.IGNORECASE))
            goto_count = len(re.findall(r'\bGO\s+TO\b', body, re.IGNORECASE))
            perform_targets = sorted(set(re.findall(r'PERFORM\s+([A-Za-z0-9][A-Za-z0-9_-]*)', body, re.IGNORECASE)))
            local_calls = re.findall(r'CALL\s+["\']?([A-Za-z0-9_-]+)["\']?', body, re.IGNORECASE)
            for c in local_calls:
                all_calls.append({"target": c, "from_paragraph": name, "line": start_line})

            paragraphs.append({
                "name": name,
                "line": start_line,
                "end_line": end_line,
                "line_count": max(1, end_line - start_line),
                "complexity": 1 + if_count + evaluate_count + goto_count,
                "if_count": if_count, "evaluate_count": evaluate_count, "goto_count": goto_count,
                "perform_targets": perform_targets,
                "calls": sorted(set(local_calls)),
                "body": body,
            })

    valid_paragraph_names = {p["name"] for p in paragraphs}
    for p in paragraphs:
        # Only keep PERFORM targets that resolve to a real paragraph in this file
        p["perform_targets"] = [t for t in p["perform_targets"] if t in valid_paragraph_names and t != p["name"]]

    calls = sorted({c["target"] for c in all_calls})

    if_count_total = sum(p["if_count"] for p in paragraphs)
    evaluate_count_total = sum(p["evaluate_count"] for p in paragraphs)
    perform_count_total = sum(len(p["perform_targets"]) for p in paragraphs)
    goto_count_total = sum(p["goto_count"] for p in paragraphs)
    complexity_estimate = 1 + if_count_total + evaluate_count_total + goto_count_total

    return {
        "filename": filename,
        "program_id": program_id,
        "program_id_line": program_id_line or 1,
        "author": author,
        "divisions_found": divisions,
        "total_lines": len(lines),
        "code_lines": len(code_lines),
        "data_item_count": len(data_items),
        "data_items": data_items[:30],
        "paragraph_count": len(paragraphs),
        "paragraphs": [p["name"] for p in paragraphs][:30],
        "paragraph_details": paragraphs,
        "external_calls": calls,
        "call_details": all_calls,
        "copybooks": [c["name"] for c in copybooks],
        "copybook_details": copybooks,
        "file_io": [{"file_name": f["file_name"], "assigned_to": f["assigned_to"]} for f in file_selects],
        "file_io_details": file_selects,
        "embedded_sql_blocks": sql_blocks,
        "complexity_estimate": complexity_estimate,
        "control_flow": {
            "if_count": if_count_total, "evaluate_count": evaluate_count_total,
            "perform_count": perform_count_total, "goto_count": goto_count_total,
        },
    }
