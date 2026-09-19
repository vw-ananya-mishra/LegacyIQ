#!/usr/bin/env python3
"""
Comprehensive test for all backend fixes
"""
import requests
import json
import time
import os

BASE_URL = "http://localhost:8000/api"

def test_all_fixes():
    """Test all fixes comprehensively"""
    
    # Test 1: Upload XLSX
    print("\n" + "="*60)
    print("TEST 1: Upload XLSX File")
    print("="*60)
    xlsx_path = r"c:\Users\SQ010W3\OneDrive - Volkswagen AG\Desktop\E2EAMS\E2EAMS\Application\LegacyIQ\Legacy_Modernization_Synthetic_Dataset.xlsx"
    
    if not os.path.exists(xlsx_path):
        print(f"❌ XLSX file not found: {xlsx_path}")
        return
    
    with open(xlsx_path, 'rb') as f:
        files = {'file': ('Legacy_Modernization_Synthetic_Dataset.xlsx', f)}
        resp = requests.post(f"{BASE_URL}/workbook/upload", files=files)
        
        if resp.status_code != 200:
            print(f"❌ Upload failed! Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            return
        
        workbook_id = resp.json()['workbook_id']
        print(f"✓ Uploaded successfully. Workbook ID: {workbook_id}")
        sheet_counts = resp.json()['sheets']
        print(f"  Sheets extracted: {sheet_counts}")
    
    time.sleep(1)
    
    # Test 2: Business Rules Data
    print("\n" + "="*60)
    print("TEST 2: Business Rules - Data Should Be Populated")
    print("="*60)
    resp = requests.get(f"{BASE_URL}/workbook/{workbook_id}/business-rules")
    rules = resp.json().get('business_rules', [])
    print(f"Found {len(rules)} business rules")
    if rules:
        rule = rules[0]
        print(f"\nFirst rule sample:")
        print(f"  ID: {rule.get('id')}")
        print(f"  Name: {rule.get('rule_name')}")
        print(f"  Description: {rule.get('description')}")
        print(f"  Type: {rule.get('rule_type')}")
        print(f"  Condition: {rule.get('condition')}")
        print(f"  Action: {rule.get('action')}")
        print(f"  Criticality: {rule.get('criticality')}")
        
        # Check if data is populated
        if rule.get('rule_name') and rule.get('description'):
            print("✓ Business rules data is POPULATED with actual values!")
        else:
            print("❌ Business rules data is still NULL!")
    
    # Test 3: Dependency Graph (should not have None errors)
    print("\n" + "="*60)
    print("TEST 3: Dependency Graph - Should Filter None Nodes")
    print("="*60)
    graph_req = {
        "workbook_id": workbook_id,
        "orphan_detection": True,
        "cycle_detection": True
    }
    resp = requests.post(f"{BASE_URL}/dependency-graph/analyze", json=graph_req)
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Dependency graph built successfully!")
        print(f"  Nodes: {len(result.get('nodes', []))}")
        print(f"  Edges: {len(result.get('edges', []))}")
        print(f"  Orphans: {len(result.get('orphan_nodes', []))}")
        print(f"  Cycles: {len(result.get('cycles', []))}")
    else:
        print(f"❌ Dependency graph failed! Status: {resp.status_code}")
        print(f"Error: {resp.text}")
    
    # Test 4: Parity Engineer (should show test names)
    print("\n" + "="*60)
    print("TEST 4: Parity Engineer - Should Show Test Names")
    print("="*60)
    parity_req = {
        "workbook_id": workbook_id,
        "agent_type": "parity_engineer",
        "context": {}
    }
    resp = requests.post(f"{BASE_URL}/agent/analyze", json=parity_req)
    if resp.status_code == 200:
        result = resp.json()
        tests = result.get('findings', {}).get('tests', [])
        print(f"✓ Parity tests generated! Found {len(tests)} tests")
        if tests:
            test = tests[0]
            print(f"\nFirst test sample:")
            print(f"  Test ID: {test.get('test_id')}")
            print(f"  Test Name: {test.get('test_name')}")
            print(f"  Rule ID: {test.get('rule_id')}")
            print(f"  Module ID: {test.get('module_id')}")
            print(f"  Type: {test.get('test_type')}")
            print(f"  Status: {test.get('status')}")
            
            if test.get('test_name'):
                print("✓ Test names are properly populated!")
            else:
                print("❌ Test names are missing!")
    else:
        print(f"❌ Parity engineer failed! Status: {resp.status_code}")
        print(f"Error: {resp.text}")
    
    # Test 5: Modernization Strategist (should show recommendations from backlog)
    print("\n" + "="*60)
    print("TEST 5: Modernization Strategist - Should Show Actual Recommendations")
    print("="*60)
    modernize_req = {
        "workbook_id": workbook_id,
        "agent_type": "modernization_strategist",
        "context": {}
    }
    resp = requests.post(f"{BASE_URL}/agent/analyze", json=modernize_req)
    if resp.status_code == 200:
        result = resp.json()
        recs = result.get('findings', {}).get('recommendations', [])
        print(f"✓ Recommendations generated! Found {len(recs)} recommendations")
        if recs:
            rec = recs[0]
            print(f"\nFirst recommendation sample:")
            print(f"  ID: {rec.get('id')}")
            print(f"  Recommendation: {rec.get('recommendation')}")
            print(f"  Priority: {rec.get('priority')}")
            print(f"  Effort: {rec.get('effort')}")
            print(f"  Risk Level: {rec.get('risk_level')}")
            print(f"  Status: {rec.get('status')}")
            
            if rec.get('recommendation'):
                print("✓ Recommendations are properly populated from backlog!")
            else:
                print("❌ Recommendations data is missing!")
    else:
        print(f"❌ Modernization strategist failed! Status: {resp.status_code}")
        print(f"Error: {resp.text}")
    
    # Test 6: Modules data
    print("\n" + "="*60)
    print("TEST 6: Code Modules - Verify Data Structure")
    print("="*60)
    resp = requests.get(f"{BASE_URL}/workbook/{workbook_id}/modules")
    modules = resp.json().get('code_modules', [])
    print(f"Found {len(modules)} modules")
    if modules:
        mod = modules[0]
        print(f"\nFirst module sample:")
        print(f"  ID: {mod.get('id')}")
        print(f"  Name: {mod.get('name')}")
        print(f"  Language: {mod.get('language')}")
        print(f"  LOC: {mod.get('lines_of_code')}")
        print(f"  Complexity: {mod.get('complexity_score')}")
        print(f"  Test Coverage: {mod.get('test_coverage')}")
        
        if mod.get('name'):
            print("✓ Module data is properly populated!")
    
    # Test 7: Applications data
    print("\n" + "="*60)
    print("TEST 7: Applications - Verify Data Structure")
    print("="*60)
    resp = requests.get(f"{BASE_URL}/workbook/{workbook_id}/applications")
    apps = resp.json().get('applications', [])
    print(f"Found {len(apps)} applications")
    if apps:
        app = apps[0]
        print(f"\nFirst application sample:")
        print(f"  ID: {app.get('id')}")
        print(f"  Name: {app.get('name')}")
        print(f"  Technology: {app.get('technology_stack')}")
        print(f"  Status: {app.get('status')}")
        print(f"  Criticality: {app.get('criticality')}")
        
        if app.get('name'):
            print("✓ Application data is properly populated!")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    test_all_fixes()
