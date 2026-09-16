#!/usr/bin/env python3
"""
Test script to verify backend fixes
"""
import requests
import json
import time
import os

BASE_URL = "http://localhost:8000/api"

def test_upload_and_analyze():
    """Test workflow: upload -> agent analysis"""
    
    # Test 1: Upload XLSX
    print("\n=== Test 1: Upload XLSX ===")
    xlsx_path = r"c:\Users\SQ010W3\OneDrive - Volkswagen AG\Desktop\E2EAMS\E2EAMS\Application\LegacyX\Legacy_Modernization_Synthetic_Dataset.xlsx"
    
    if not os.path.exists(xlsx_path):
        print(f"❌ XLSX file not found: {xlsx_path}")
        return
    
    with open(xlsx_path, 'rb') as f:
        files = {'file': ('Legacy_Modernization_Synthetic_Dataset.xlsx', f)}
        resp = requests.post(f"{BASE_URL}/workbook/upload", files=files)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        
        if resp.status_code != 200:
            print("❌ Upload failed!")
            return
        
        workbook_id = resp.json()['workbook_id']
        print(f"✓ Uploaded successfully. Workbook ID: {workbook_id}")
    
    # Wait a moment
    time.sleep(1)
    
    # Test 2: Check business rules
    print("\n=== Test 2: Get Business Rules ===")
    resp = requests.get(f"{BASE_URL}/workbook/{workbook_id}/business-rules")
    print(f"Status: {resp.status_code}")
    rules = resp.json().get('business_rules', [])
    print(f"Found {len(rules)} rules")
    if rules:
        print(f"Sample rule: {json.dumps(rules[0], indent=2, default=str)}")
        # Check if data fields are populated
        if rules[0].get('rule_name') or rules[0].get('description'):
            print("✓ Business rules data is populated!")
        else:
            print("❌ Business rules data is still null!")
    
    # Test 3: Test agent analysis
    print("\n=== Test 3: Agent Analysis (documentation_architect) ===")
    analysis_request = {
        "workbook_id": workbook_id,
        "agent_type": "documentation_architect",
        "context": {}
    }
    resp = requests.post(f"{BASE_URL}/agent/analyze", json=analysis_request)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print("✓ Agent analysis successful!")
        result = resp.json()
        print(f"Agent type: {result.get('agent_type')}")
        print(f"Status: {result.get('status')}")
        print(f"Confidence: {result.get('confidence')}")
        if result.get('findings'):
            print(f"Findings: {json.dumps(result['findings'], indent=2, default=str)}")
    else:
        print(f"❌ Agent analysis failed: {resp.text}")
    
    # Test 4: Test dependency graph
    print("\n=== Test 4: Dependency Graph Analysis ===")
    graph_request = {
        "workbook_id": workbook_id,
        "orphan_detection": True,
        "cycle_detection": True
    }
    resp = requests.post(f"{BASE_URL}/dependency-graph/analyze", json=graph_request)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Graph analysis successful!")
        print(f"Nodes: {len(result.get('nodes', []))}")
        print(f"Edges: {len(result.get('edges', []))}")
        print(f"Orphans: {len(result.get('orphan_nodes', []))}")
    else:
        print(f"❌ Graph analysis failed: {resp.text}")

if __name__ == "__main__":
    test_upload_and_analyze()
