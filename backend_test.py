#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for LegalSahayak
Tests all endpoints as specified in the review request
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BACKEND_URL = "https://lawyer-helper-3.preview.emergentagent.com/api"

class LegalSahayakTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.user_tokens = {}
        self.user_ids = {}
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> tuple[bool, Any]:
        """Make HTTP request and return success status and response"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, timeout=30, **kwargs)
            
            # Try to parse JSON response
            try:
                data = response.json()
            except:
                data = response.text
            
            success = 200 <= response.status_code < 300
            return success, {
                "status_code": response.status_code,
                "data": data,
                "headers": dict(response.headers)
            }
        except Exception as e:
            return False, {"error": str(e)}
    
    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.make_request("GET", "/health")
        
        if success and response["data"].get("status") == "healthy":
            self.log_test("Health Check", True, "API is healthy")
        else:
            self.log_test("Health Check", False, "Health check failed", response)
    
    def test_user_registration(self):
        """Test user registration for both common user and lawyer"""
        
        # Test common user registration
        common_user_data = {
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User",
            "user_type": "common"
        }
        
        success, response = self.make_request("POST", "/auth/register", json=common_user_data)
        
        if success and "access_token" in response["data"]:
            user_data = response["data"]["user"]
            self.user_tokens["common"] = response["data"]["access_token"]
            self.user_ids["common"] = user_data["id"]
            self.log_test("Common User Registration", True, f"User ID: {user_data['id']}")
        else:
            self.log_test("Common User Registration", False, "Registration failed", response)
        
        # Test lawyer registration
        lawyer_data = {
            "email": "lawyer@example.com",
            "password": "lawyer123",
            "full_name": "Rajesh Kumar",
            "user_type": "lawyer",
            "specialization": "Criminal Law",
            "location": "Mumbai",
            "years_of_experience": 10,
            "bar_council_number": "MH/12345/2015",
            "bio": "Experienced criminal lawyer with 10 years of practice"
        }
        
        success, response = self.make_request("POST", "/auth/register", json=lawyer_data)
        
        if success and "access_token" in response["data"]:
            user_data = response["data"]["user"]
            self.user_tokens["lawyer"] = response["data"]["access_token"]
            self.user_ids["lawyer"] = user_data["id"]
            self.log_test("Lawyer Registration", True, f"Lawyer ID: {user_data['id']}")
        else:
            self.log_test("Lawyer Registration", False, "Lawyer registration failed", response)
    
    def test_user_login(self):
        """Test user login for both users"""
        
        # Test common user login
        login_data = {
            "email": "test@example.com",
            "password": "test123"
        }
        
        success, response = self.make_request("POST", "/auth/login", json=login_data)
        
        if success and "access_token" in response["data"]:
            self.log_test("Common User Login", True, "Login successful")
        else:
            self.log_test("Common User Login", False, "Login failed", response)
        
        # Test lawyer login
        lawyer_login_data = {
            "email": "lawyer@example.com",
            "password": "lawyer123"
        }
        
        success, response = self.make_request("POST", "/auth/login", json=lawyer_login_data)
        
        if success and "access_token" in response["data"]:
            self.log_test("Lawyer Login", True, "Lawyer login successful")
        else:
            self.log_test("Lawyer Login", False, "Lawyer login failed", response)
    
    def test_contract_analysis(self):
        """Test contract analysis functionality"""
        if "common" not in self.user_ids:
            self.log_test("Contract Analysis", False, "No common user ID available")
            return
        
        # Test contract analysis with text content
        contract_data = {
            "user_id": self.user_ids["common"],
            "document_name": "Test Rental Agreement",
            "document_type": "text",
            "text_content": "This rental agreement is made between landlord John Doe and tenant Jane Smith. The monthly rent is Rs. 25,000. The security deposit is Rs. 50,000. The tenant must give 2 months notice before vacating."
        }
        
        success, response = self.make_request("POST", "/contract/analyze", data=contract_data)
        
        if success and "simplified_text" in response["data"]:
            self.log_test("Contract Analysis", True, "Contract analyzed successfully")
        else:
            self.log_test("Contract Analysis", False, "Contract analysis failed", response)
    
    def test_contract_history(self):
        """Test contract history retrieval"""
        if "common" not in self.user_ids:
            self.log_test("Contract History", False, "No common user ID available")
            return
        
        user_id = self.user_ids["common"]
        success, response = self.make_request("GET", f"/contract/history/{user_id}")
        
        if success and isinstance(response["data"], list):
            self.log_test("Contract History", True, f"Retrieved {len(response['data'])} contracts")
        else:
            self.log_test("Contract History", False, "Failed to retrieve contract history", response)
    
    def test_case_analysis(self):
        """Test case analysis functionality"""
        if "common" not in self.user_ids:
            self.log_test("Case Analysis", False, "No common user ID available")
            return
        
        case_data = {
            "user_id": self.user_ids["common"],
            "case_title": "Property Dispute Case",
            "case_type": "Civil",
            "case_description": "My neighbor has illegally occupied 10 feet of my property and built a wall. I have property documents proving ownership. He refuses to remove the wall."
        }
        
        success, response = self.make_request("POST", "/case/analyze", data=case_data)
        
        if success and "analysis" in response["data"]:
            self.log_test("Case Analysis", True, "Case analyzed successfully")
        else:
            self.log_test("Case Analysis", False, "Case analysis failed", response)
    
    def test_case_history(self):
        """Test case history retrieval"""
        if "common" not in self.user_ids:
            self.log_test("Case History", False, "No common user ID available")
            return
        
        user_id = self.user_ids["common"]
        success, response = self.make_request("GET", f"/case/history/{user_id}")
        
        if success and isinstance(response["data"], list):
            self.log_test("Case History", True, f"Retrieved {len(response['data'])} cases")
        else:
            self.log_test("Case History", False, "Failed to retrieve case history", response)
    
    def test_legal_procedure(self):
        """Test legal procedure retrieval"""
        success, response = self.make_request("GET", "/procedure/Civil")
        
        if success and "procedure" in response["data"]:
            self.log_test("Legal Procedure", True, "Civil procedure retrieved successfully")
        else:
            self.log_test("Legal Procedure", False, "Failed to retrieve legal procedure", response)
    
    def test_lawyer_search(self):
        """Test lawyer search functionality"""
        
        # Test search all lawyers
        success, response = self.make_request("GET", "/lawyers/search")
        
        if success and isinstance(response["data"], list):
            lawyer_count = len(response["data"])
            self.log_test("Lawyer Search (All)", True, f"Found {lawyer_count} lawyers")
            
            # Test search by specialization if lawyers exist
            if lawyer_count > 0:
                success2, response2 = self.make_request("GET", "/lawyers/search?specialization=Criminal")
                if success2:
                    self.log_test("Lawyer Search (Specialization)", True, f"Found {len(response2['data'])} criminal lawyers")
                else:
                    self.log_test("Lawyer Search (Specialization)", False, "Specialization search failed", response2)
        else:
            self.log_test("Lawyer Search (All)", False, "Failed to search lawyers", response)
    
    def test_lawyer_profile(self):
        """Test lawyer profile retrieval"""
        if "lawyer" not in self.user_ids:
            self.log_test("Lawyer Profile", False, "No lawyer ID available")
            return
        
        lawyer_id = self.user_ids["lawyer"]
        success, response = self.make_request("GET", f"/lawyer/{lawyer_id}")
        
        if success and response["data"].get("user_type") == "lawyer":
            self.log_test("Lawyer Profile", True, "Lawyer profile retrieved successfully")
        else:
            self.log_test("Lawyer Profile", False, "Failed to retrieve lawyer profile", response)
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting LegalSahayak Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in order
        self.test_health_check()
        self.test_user_registration()
        self.test_user_login()
        self.test_contract_analysis()
        self.test_contract_history()
        self.test_case_analysis()
        self.test_case_history()
        self.test_legal_procedure()
        self.test_lawyer_search()
        self.test_lawyer_profile()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # List failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("\n" + "=" * 60)
        return passed == total

if __name__ == "__main__":
    tester = LegalSahayakTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)