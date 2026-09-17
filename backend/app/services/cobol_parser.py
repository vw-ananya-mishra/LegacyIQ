"""
COBOL Source Analyzer - lightweight structural parser for a single .cbl file.

This is NOT a full COBOL compiler/parser (that's out of scope) - it uses
line-oriented regex heuristics to extract the structural facts a modernization
engineer cares about first: PROGRAM-ID, divisions present, data items,
PROCEDURE DIVISION paragraphs, external CALLs, COPY (copybook) includes,
file I/O (SELECT...ASSIGN TO), embedded SQL blocks, and a simple
cyclomatic-ish complexity estimate.

These facts are 100% deterministic (grep-style extraction from the real
source text) and are the ONLY thing fed to the LLM for narration - the same
"deterministic facts + AI narrative" pattern used for the XLSX-based agents.
"""

import re
from typing import Any, Dict, List


def parse_cobol_source(source: str, filename: str) -> Dict[str, Any]:
    lines = source.splitlines()
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('*')]

    def find_first(pattern: str):
        m = re.search(pattern, source, re.IGNORECASE)
        return m.group(1).strip().rstrip('.') if m else None

    program_id = find_first(r'PROGRAM-ID\.\s*([A-Za-z0-9_-]+)')
    author = find_first(r'AUTHOR\.\s*([^\n]+)')

    divisions = [
        div for div in ('IDENTIFICATION', 'ENVIRONMENT', 'DATA', 'PROCEDURE')
        if re.search(rf'{div}\s+DIVISION', source, re.IGNORECASE)
    ]

    data_items: List[Dict[str, Any]] = []
    for m in re.finditer(
        r'^\s*(0[1-9]|[1-4][0-9])\s+([A-Za-z0-9_-]+)\s*(?:PIC(?:TURE)?\s+([A-Za-z0-9\(\)V9XS.,+-]+))?',
        source, re.IGNORECASE | re.MULTILINE,
    ):
        data_items.append({"level": m.group(1), "name": m.group(2), "pic": m.group(3)})

    paragraphs: List[str] = []
    proc_match = re.search(r'PROCEDURE\s+DIVISION[^.]*\.\s*(.*)', source, re.IGNORECASE | re.DOTALL)
    proc_body = proc_match.group(1) if proc_match else ""
    # COBOL scope-terminators (END-IF, END-READ, ...) look identical to a paragraph
    # header (a lone word + period on its own line) - explicitly exclude them.
    _SCOPE_TERMINATORS = {
        'END', 'STOP', 'EXIT', 'CONTINUE', 'ELSE', 'END-IF', 'END-READ', 'END-WRITE',
        'END-REWRITE', 'END-DELETE', 'END-EVALUATE', 'END-PERFORM', 'END-CALL',
        'END-COMPUTE', 'END-STRING', 'END-UNSTRING', 'END-SEARCH', 'END-ADD',
        'END-SUBTRACT', 'END-MULTIPLY', 'END-DIVIDE', 'END-ACCEPT', 'END-DISPLAY',
        'END-EXEC', 'END-START', 'END-RETURN', 'WHEN-OTHER',
    }
    for m in re.finditer(r'^\s*([A-Za-z0-9][A-Za-z0-9_-]*)\s*\.\s*$', proc_body, re.MULTILINE):
        name = m.group(1)
        if name.upper() not in _SCOPE_TERMINATORS:
            paragraphs.append(name)

    calls = sorted(set(re.findall(r'CALL\s+["\']?([A-Za-z0-9_-]+)["\']?', source, re.IGNORECASE)))
    copybooks = sorted(set(re.findall(r'COPY\s+([A-Za-z0-9_-]+)', source, re.IGNORECASE)))

    file_selects = re.findall(r'SELECT\s+([A-Za-z0-9_-]+)\s+ASSIGN\s+TO\s+([A-Za-z0-9_."\'-]+)', source, re.IGNORECASE)
    files = [{"file_name": f[0], "assigned_to": f[1].strip('"\'')} for f in file_selects]

    sql_blocks = len(re.findall(r'EXEC\s+SQL', source, re.IGNORECASE))

    if_count = len(re.findall(r'\bIF\b', source, re.IGNORECASE))
    evaluate_count = len(re.findall(r'\bEVALUATE\b', source, re.IGNORECASE))
    perform_count = len(re.findall(r'\bPERFORM\b', source, re.IGNORECASE))
    goto_count = len(re.findall(r'\bGO\s+TO\b', source, re.IGNORECASE))
    # Simple cyclomatic-ish estimate: 1 (base path) + every branch/jump statement
    complexity_estimate = 1 + if_count + evaluate_count + goto_count

    return {
        "filename": filename,
        "program_id": program_id,
        "author": author,
        "divisions_found": divisions,
        "total_lines": len(lines),
        "code_lines": len(code_lines),
        "data_item_count": len(data_items),
        "data_items": data_items[:30],
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs[:30],
        "external_calls": calls,
        "copybooks": copybooks,
        "file_io": files,
        "embedded_sql_blocks": sql_blocks,
        "complexity_estimate": complexity_estimate,
        "control_flow": {
            "if_count": if_count, "evaluate_count": evaluate_count,
            "perform_count": perform_count, "goto_count": goto_count,
        },
    }
