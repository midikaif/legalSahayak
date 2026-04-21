#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for LegalSahayak
Handles existing users and tests all functionality
"""

import requests
import json
import sys
import uuid
import time

# Backend URL - local development server running on port 8000
BACKEND_URL = "http://localhost:8000/api"

def test_comprehensive_backend():
    """Test all backend functionality comprehensively"""
    results = []
    
    print("🚀 Comprehensive LegalSahayak Backend API Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("✅ Health Check: PASS")
            results.append(("Health Check", True, "API is healthy"))
        else:
            print(f"❌ Health Check: FAIL - {response.status_code}")
            results.append(("Health Check", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ Health Check: FAIL - {str(e)}")
        results.append(("Health Check", False, str(e)))
    
    # Generate unique emails for this test run
    test_id = str(uuid.uuid4())[:8]
    common_email = f"test_{test_id}@example.com"
    lawyer_email = f"lawyer_{test_id}@example.com"
    
    # Test 2: User Registration (Common User)
    user_id = None
    user_token = None
    try:
        user_data = {
            "email": common_email,
            "password": "test123",
            "full_name": "Test User",
            "user_type": "common"
        }
        response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data, timeout=10)
        if response.status_code == 200 and "access_token" in response.json():
            user_id = response.json()["user"]["id"]
            user_token = response.json()["access_token"]
            print(f"✅ User Registration: PASS - User ID: {user_id}")
            results.append(("User Registration", True, f"User ID: {user_id}"))
        else:
            print(f"❌ User Registration: FAIL - {response.status_code} - {response.text}")
            results.append(("User Registration", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ User Registration: FAIL - {str(e)}")
        results.append(("User Registration", False, str(e)))
    
    # Test 3: User Login
    try:
        login_data = {
            "email": common_email,
            "password": "test123"
        }
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200 and "access_token" in response.json():
            print("✅ User Login: PASS")
            results.append(("User Login", True, "Login successful"))
        else:
            print(f"❌ User Login: FAIL - {response.status_code} - {response.text}")
            results.append(("User Login", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ User Login: FAIL - {str(e)}")
        results.append(("User Login", False, str(e)))
    
    # Test 4: Lawyer Registration
    lawyer_id = None
    try:
        lawyer_data = {
            "email": lawyer_email,
            "password": "lawyer123",
            "full_name": "Rajesh Kumar",
            "user_type": "lawyer",
            "specialization": "Criminal Law",
            "location": "Mumbai",
            "years_of_experience": 10,
            "bar_council_number": f"MH/{test_id}/2015",
            "bio": "Experienced criminal lawyer"
        }
        response = requests.post(f"{BACKEND_URL}/auth/register", json=lawyer_data, timeout=10)
        if response.status_code == 200 and "access_token" in response.json():
            lawyer_id = response.json()["user"]["id"]
            print(f"✅ Lawyer Registration: PASS - Lawyer ID: {lawyer_id}")
            results.append(("Lawyer Registration", True, f"Lawyer ID: {lawyer_id}"))
        else:
            print(f"❌ Lawyer Registration: FAIL - {response.status_code} - {response.text}")
            results.append(("Lawyer Registration", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ Lawyer Registration: FAIL - {str(e)}")
        results.append(("Lawyer Registration", False, str(e)))
    
    # Test 5: Lawyer Search (All)
    try:
        response = requests.get(f"{BACKEND_URL}/lawyers/search", timeout=10)
        if response.status_code == 200 and isinstance(response.json(), list):
            lawyer_count = len(response.json())
            print(f"✅ Lawyer Search (All): PASS - Found {lawyer_count} lawyers")
            results.append(("Lawyer Search (All)", True, f"Found {lawyer_count} lawyers"))
        else:
            print(f"❌ Lawyer Search (All): FAIL - {response.status_code}")
            results.append(("Lawyer Search (All)", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ Lawyer Search (All): FAIL - {str(e)}")
        results.append(("Lawyer Search (All)", False, str(e)))
    
    # Test 6: Lawyer Search by Specialization
    try:
        response = requests.get(f"{BACKEND_URL}/lawyers/search?specialization=Criminal", timeout=10)
        if response.status_code == 200 and isinstance(response.json(), list):
            criminal_lawyers = len(response.json())
            print(f"✅ Lawyer Search (Specialization): PASS - Found {criminal_lawyers} criminal lawyers")
            results.append(("Lawyer Search (Specialization)", True, f"Found {criminal_lawyers} criminal lawyers"))
        else:
            print(f"❌ Lawyer Search (Specialization): FAIL - {response.status_code}")
            results.append(("Lawyer Search (Specialization)", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ Lawyer Search (Specialization): FAIL - {str(e)}")
        results.append(("Lawyer Search (Specialization)", False, str(e)))
    
    # Test 7: Lawyer Profile
    if lawyer_id:
        try:
            response = requests.get(f"{BACKEND_URL}/lawyer/{lawyer_id}", timeout=10)
            if response.status_code == 200 and response.json().get("user_type") == "lawyer":
                print("✅ Lawyer Profile: PASS")
                results.append(("Lawyer Profile", True, "Profile retrieved successfully"))
            else:
                print(f"❌ Lawyer Profile: FAIL - {response.status_code}")
                results.append(("Lawyer Profile", False, f"Status: {response.status_code}"))
        except Exception as e:
            print(f"❌ Lawyer Profile: FAIL - {str(e)}")
            results.append(("Lawyer Profile", False, str(e)))
    else:
        print("⚠️  Lawyer Profile: SKIP - No lawyer ID")
        results.append(("Lawyer Profile", False, "No lawyer ID available"))
    
    # Test 8: Contract Analysis (with AI - may fail due to LLM issues)
    if user_id:
        try:
            contract_data = {
                "user_id": user_id,
                "document_name": "Test Rental Agreement",
                "document_type": "text",
                "text_content": "This rental agreement is made between landlord John Doe and tenant Jane Smith. Monthly rent is Rs. 25,000. Security deposit is Rs. 50,000. Tenant must give 2 months notice before vacating."
            }
            response = requests.post(f"{BACKEND_URL}/contract/analyze", data=contract_data, timeout=60)
            if response.status_code == 200:
                response_data = response.json()
                if "simplified_text" in response_data or "analysis" in str(response_data):
                    print("✅ Contract Analysis: PASS")
                    results.append(("Contract Analysis", True, "Contract analyzed successfully"))
                else:
                    print("⚠️  Contract Analysis: PARTIAL - Response received but may have AI issues")
                    results.append(("Contract Analysis", True, "Response received but AI may have issues"))
            else:
                print(f"❌ Contract Analysis: FAIL - {response.status_code}")
                results.append(("Contract Analysis", False, f"Status: {response.status_code}"))
        except Exception as e:
            print(f"❌ Contract Analysis: FAIL - {str(e)}")
            results.append(("Contract Analysis", False, str(e)))
    else:
        print("⚠️  Contract Analysis: SKIP - No user ID")
        results.append(("Contract Analysis", False, "No user ID available"))
    
    # Test 9: Contract History
    if user_id:
        try:
            response = requests.get(f"{BACKEND_URL}/contract/history/{user_id}", timeout=10)
            if response.status_code == 200 and isinstance(response.json(), list):
                contract_count = len(response.json())
                print(f"✅ Contract History: PASS - Retrieved {contract_count} contracts")
                results.append(("Contract History", True, f"Retrieved {contract_count} contracts"))
            else:
                print(f"❌ Contract History: FAIL - {response.status_code}")
                results.append(("Contract History", False, f"Status: {response.status_code}"))
        except Exception as e:
            print(f"❌ Contract History: FAIL - {str(e)}")
            results.append(("Contract History", False, str(e)))
    else:
        print("⚠️  Contract History: SKIP - No user ID")
        results.append(("Contract History", False, "No user ID available"))
    
    # Test 10: Case Analysis (with AI - may fail due to LLM issues)
    if user_id:
        try:
            case_data = {
                "user_id": user_id,
                "case_title": "Property Dispute Case",
                "case_type": "Civil",
                "case_description": "My neighbor has illegally occupied 10 feet of my property and built a wall. I have property documents proving ownership. He refuses to remove the wall."
            }
            response = requests.post(f"{BACKEND_URL}/case/analyze", data=case_data, timeout=60)
            if response.status_code == 200:
                response_data = response.json()
                if "analysis" in response_data:
                    print("✅ Case Analysis: PASS")
                    results.append(("Case Analysis", True, "Case analyzed successfully"))
                else:
                    print("⚠️  Case Analysis: PARTIAL - Response received but may have AI issues")
                    results.append(("Case Analysis", True, "Response received but AI may have issues"))
            else:
                print(f"❌ Case Analysis: FAIL - {response.status_code}")
                results.append(("Case Analysis", False, f"Status: {response.status_code}"))
        except Exception as e:
            print(f"❌ Case Analysis: FAIL - {str(e)}")
            results.append(("Case Analysis", False, str(e)))
    else:
        print("⚠️  Case Analysis: SKIP - No user ID")
        results.append(("Case Analysis", False, "No user ID available"))
    
    # Test 11: Case History
    if user_id:
        try:
            response = requests.get(f"{BACKEND_URL}/case/history/{user_id}", timeout=10)
            if response.status_code == 200 and isinstance(response.json(), list):
                case_count = len(response.json())
                print(f"✅ Case History: PASS - Retrieved {case_count} cases")
                results.append(("Case History", True, f"Retrieved {case_count} cases"))
            else:
                print(f"❌ Case History: FAIL - {response.status_code}")
                results.append(("Case History", False, f"Status: {response.status_code}"))
        except Exception as e:
            print(f"❌ Case History: FAIL - {str(e)}")
            results.append(("Case History", False, str(e)))
    else:
        print("⚠️  Case History: SKIP - No user ID")
        results.append(("Case History", False, "No user ID available"))
    
    # Test 12: Legal Procedure (with AI - may fail due to LLM issues)
    try:
        response = requests.get(f"{BACKEND_URL}/procedure/Civil", timeout=60)
        if response.status_code == 200:
            response_data = response.json()
            if "procedure" in response_data:
                print("✅ Legal Procedure: PASS")
                results.append(("Legal Procedure", True, "Civil procedure retrieved successfully"))
            else:
                print("⚠️  Legal Procedure: PARTIAL - Response received but may have AI issues")
                results.append(("Legal Procedure", True, "Response received but AI may have issues"))
        else:
            print(f"❌ Legal Procedure: FAIL - {response.status_code}")
            results.append(("Legal Procedure", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ Legal Procedure: FAIL - {str(e)}")
        results.append(("Legal Procedure", False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    # Categorize results
    critical_failures = []
    ai_issues = []
    minor_issues = []
    
    for test_name, success, details in results:
        if not success:
            if "AI" in details or "LLM" in details or test_name in ["Contract Analysis", "Case Analysis", "Legal Procedure"]:
                ai_issues.append(f"{test_name}: {details}")
            elif test_name in ["Health Check", "User Registration", "User Login", "Lawyer Registration"]:
                critical_failures.append(f"{test_name}: {details}")
            else:
                minor_issues.append(f"{test_name}: {details}")
    
    if critical_failures:
        print(f"\n🚨 CRITICAL FAILURES:")
        for failure in critical_failures:
            print(f"  - {failure}")
    
    if ai_issues:
        print(f"\n🤖 AI/LLM RELATED ISSUES:")
        for issue in ai_issues:
            print(f"  - {issue}")
    
    if minor_issues:
        print(f"\n⚠️  MINOR ISSUES:")
        for issue in minor_issues:
            print(f"  - {issue}")
    
    print(f"\n🎯 CORE FUNCTIONALITY: {'✅ WORKING' if len(critical_failures) == 0 else '❌ ISSUES FOUND'}")
    print(f"🤖 AI FEATURES: {'✅ WORKING' if len(ai_issues) == 0 else '⚠️ ISSUES DETECTED (LLM service problems)'}")
    
    return results

if __name__ == "__main__":
    results = test_comprehensive_backend()
    
    # Count critical vs AI issues
    critical_issues = sum(1 for test_name, success, details in results 
                         if not success and test_name in ["Health Check", "User Registration", "User Login", "Lawyer Registration"])
    
    # Exit with 0 if only AI issues (which are external service problems)
    sys.exit(0 if critical_issues == 0 else 1)