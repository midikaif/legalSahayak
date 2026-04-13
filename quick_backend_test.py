#!/usr/bin/env python3
"""
Quick Backend API Tests for LegalSahayak - Basic functionality only
"""

import requests
import json
import sys

# Backend URL - using local URL since external is timing out
BACKEND_URL = "http://localhost:8001/api"

def test_basic_endpoints():
    """Test basic endpoints without AI analysis"""
    results = []
    
    print("🚀 Testing LegalSahayak Backend API")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 50)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("✅ Health Check: PASS")
            results.append(("Health Check", True))
        else:
            print(f"❌ Health Check: FAIL - {response.status_code}")
            results.append(("Health Check", False))
    except Exception as e:
        print(f"❌ Health Check: FAIL - {str(e)}")
        results.append(("Health Check", False))
    
    # Test 2: User Registration (Common User)
    user_id = None
    try:
        user_data = {
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User",
            "user_type": "common"
        }
        response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data, timeout=10)
        if response.status_code == 200 and "access_token" in response.json():
            user_id = response.json()["user"]["id"]
            print(f"✅ User Registration: PASS - User ID: {user_id}")
            results.append(("User Registration", True))
        else:
            print(f"❌ User Registration: FAIL - {response.status_code} - {response.text}")
            results.append(("User Registration", False))
    except Exception as e:
        print(f"❌ User Registration: FAIL - {str(e)}")
        results.append(("User Registration", False))
    
    # Test 3: User Login
    try:
        login_data = {
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200 and "access_token" in response.json():
            print("✅ User Login: PASS")
            results.append(("User Login", True))
        else:
            print(f"❌ User Login: FAIL - {response.status_code} - {response.text}")
            results.append(("User Login", False))
    except Exception as e:
        print(f"❌ User Login: FAIL - {str(e)}")
        results.append(("User Login", False))
    
    # Test 4: Lawyer Registration
    lawyer_id = None
    try:
        lawyer_data = {
            "email": "lawyer@example.com",
            "password": "lawyer123",
            "full_name": "Rajesh Kumar",
            "user_type": "lawyer",
            "specialization": "Criminal Law",
            "location": "Mumbai",
            "years_of_experience": 10,
            "bar_council_number": "MH/12345/2015",
            "bio": "Experienced criminal lawyer"
        }
        response = requests.post(f"{BACKEND_URL}/auth/register", json=lawyer_data, timeout=10)
        if response.status_code == 200 and "access_token" in response.json():
            lawyer_id = response.json()["user"]["id"]
            print(f"✅ Lawyer Registration: PASS - Lawyer ID: {lawyer_id}")
            results.append(("Lawyer Registration", True))
        else:
            print(f"❌ Lawyer Registration: FAIL - {response.status_code} - {response.text}")
            results.append(("Lawyer Registration", False))
    except Exception as e:
        print(f"❌ Lawyer Registration: FAIL - {str(e)}")
        results.append(("Lawyer Registration", False))
    
    # Test 5: Lawyer Search (Basic)
    try:
        response = requests.get(f"{BACKEND_URL}/lawyers/search", timeout=10)
        if response.status_code == 200 and isinstance(response.json(), list):
            lawyer_count = len(response.json())
            print(f"✅ Lawyer Search: PASS - Found {lawyer_count} lawyers")
            results.append(("Lawyer Search", True))
        else:
            print(f"❌ Lawyer Search: FAIL - {response.status_code} - {response.text}")
            results.append(("Lawyer Search", False))
    except Exception as e:
        print(f"❌ Lawyer Search: FAIL - {str(e)}")
        results.append(("Lawyer Search", False))
    
    # Test 6: Lawyer Profile (if we have lawyer_id)
    if lawyer_id:
        try:
            response = requests.get(f"{BACKEND_URL}/lawyer/{lawyer_id}", timeout=10)
            if response.status_code == 200 and response.json().get("user_type") == "lawyer":
                print("✅ Lawyer Profile: PASS")
                results.append(("Lawyer Profile", True))
            else:
                print(f"❌ Lawyer Profile: FAIL - {response.status_code} - {response.text}")
                results.append(("Lawyer Profile", False))
        except Exception as e:
            print(f"❌ Lawyer Profile: FAIL - {str(e)}")
            results.append(("Lawyer Profile", False))
    else:
        print("⚠️  Lawyer Profile: SKIP - No lawyer ID")
        results.append(("Lawyer Profile", False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 BASIC TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    # List failed tests
    failed_tests = [name for name, success in results if not success]
    if failed_tests:
        print(f"\n❌ FAILED TESTS: {', '.join(failed_tests)}")
    
    return passed, total, user_id, lawyer_id

def test_ai_endpoints(user_id):
    """Test AI-powered endpoints separately with longer timeout"""
    if not user_id:
        print("\n⚠️  Skipping AI tests - No user ID available")
        return 0, 3
    
    print("\n🤖 Testing AI-Powered Endpoints (may take longer)")
    print("=" * 50)
    
    ai_results = []
    
    # Test Contract Analysis
    try:
        contract_data = {
            "user_id": user_id,
            "document_name": "Test Rental Agreement",
            "document_type": "text",
            "text_content": "This rental agreement is made between landlord John Doe and tenant Jane Smith. Monthly rent is Rs. 25,000."
        }
        response = requests.post(f"{BACKEND_URL}/contract/analyze", data=contract_data, timeout=60)
        if response.status_code == 200 and "simplified_text" in response.json():
            print("✅ Contract Analysis: PASS")
            ai_results.append(("Contract Analysis", True))
        else:
            print(f"❌ Contract Analysis: FAIL - {response.status_code}")
            ai_results.append(("Contract Analysis", False))
    except Exception as e:
        print(f"❌ Contract Analysis: FAIL - {str(e)}")
        ai_results.append(("Contract Analysis", False))
    
    # Test Case Analysis
    try:
        case_data = {
            "user_id": user_id,
            "case_title": "Property Dispute",
            "case_type": "Civil",
            "case_description": "Neighbor occupied my property illegally."
        }
        response = requests.post(f"{BACKEND_URL}/case/analyze", data=case_data, timeout=60)
        if response.status_code == 200 and "analysis" in response.json():
            print("✅ Case Analysis: PASS")
            ai_results.append(("Case Analysis", True))
        else:
            print(f"❌ Case Analysis: FAIL - {response.status_code}")
            ai_results.append(("Case Analysis", False))
    except Exception as e:
        print(f"❌ Case Analysis: FAIL - {str(e)}")
        ai_results.append(("Case Analysis", False))
    
    # Test Legal Procedure
    try:
        response = requests.get(f"{BACKEND_URL}/procedure/Civil", timeout=60)
        if response.status_code == 200 and "procedure" in response.json():
            print("✅ Legal Procedure: PASS")
            ai_results.append(("Legal Procedure", True))
        else:
            print(f"❌ Legal Procedure: FAIL - {response.status_code}")
            ai_results.append(("Legal Procedure", False))
    except Exception as e:
        print(f"❌ Legal Procedure: FAIL - {str(e)}")
        ai_results.append(("Legal Procedure", False))
    
    passed = sum(1 for _, success in ai_results if success)
    total = len(ai_results)
    
    print(f"\n🤖 AI Tests: {passed}/{total} passed")
    return passed, total

if __name__ == "__main__":
    basic_passed, basic_total, user_id, lawyer_id = test_basic_endpoints()
    ai_passed, ai_total = test_ai_endpoints(user_id)
    
    total_passed = basic_passed + ai_passed
    total_tests = basic_total + ai_total
    
    print(f"\n🎯 OVERALL SUMMARY: {total_passed}/{total_tests} tests passed ({(total_passed/total_tests)*100:.1f}%)")
    
    sys.exit(0 if total_passed == total_tests else 1)