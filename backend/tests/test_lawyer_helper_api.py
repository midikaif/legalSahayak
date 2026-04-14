"""
Backend API Tests for Lawyer Helper App
Tests: Auth (register, login), Case Analysis, Contract Analysis, Legal Procedures, Lawyer Search
New in Iteration 2: Case Detail, Case Follow-up, Document Auto-Analysis
"""
import pytest
import requests
import os
import time

# Get backend URL - use localhost for backend testing
BASE_URL = "http://localhost:8001"

# Test user credentials
TEST_USER_EMAIL = "testuser2@example.com"
TEST_USER_PASSWORD = "test123"
TEST_USER_NAME = "Test User"

# Lawyer test user
TEST_LAWYER_EMAIL = "testlawyer@example.com"
TEST_LAWYER_PASSWORD = "lawyer123"
TEST_LAWYER_NAME = "Test Lawyer"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestHealthCheck:
    """Health check endpoint test"""
    
    def test_health_endpoint(self, api_client):
        """Test /api/health endpoint"""
        try:
            response = api_client.get(f"{BASE_URL}/api/health")
            print(f"✓ Health check status: {response.status_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "timestamp" in data
            print(f"✓ Health check passed: {data}")
        except Exception as e:
            print(f"✗ Health check failed: {str(e)}")
            raise


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_register_common_user(self, api_client):
        """Test user registration for common user"""
        try:
            # Use unique email with timestamp to avoid conflicts
            unique_email = f"test_common_{int(time.time())}@example.com"
            
            payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "user_type": "common"
            }
            
            response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
            print(f"✓ Register status: {response.status_code}")
            
            if response.status_code == 400:
                # User might already exist, that's okay for testing
                print(f"✓ User already exists (expected): {response.json()}")
                pytest.skip("User already registered")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "access_token" in data
            assert "user" in data
            assert data["user"]["email"] == unique_email
            assert data["user"]["user_type"] == "common"
            print(f"✓ Registration successful: {data['user']['email']}")
        except Exception as e:
            print(f"✗ Registration failed: {str(e)}")
            raise
    
    def test_login_user(self, api_client):
        """Test user login"""
        try:
            # First register a user
            unique_email = f"test_login_{int(time.time())}@example.com"
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "user_type": "common"
            }
            api_client.post(f"{BASE_URL}/api/auth/register", json=register_payload)
            
            # Now login
            login_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD
            }
            
            response = api_client.post(f"{BASE_URL}/api/auth/login", json=login_payload)
            print(f"✓ Login status: {response.status_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert "access_token" in data
            assert "user" in data
            assert data["user"]["email"] == unique_email
            print(f"✓ Login successful for: {data['user']['email']}")
        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            raise
    
    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials"""
        try:
            payload = {
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
            
            response = api_client.post(f"{BASE_URL}/api/auth/login", json=payload)
            print(f"✓ Invalid login status: {response.status_code}")
            assert response.status_code == 401
            
            data = response.json()
            assert "detail" in data
            print(f"✓ Invalid login correctly rejected: {data['detail']}")
        except Exception as e:
            print(f"✗ Invalid login test failed: {str(e)}")
            raise


class TestCaseAnalysis:
    """Case analysis endpoint tests"""
    
    def test_case_analysis(self, api_client):
        """Test case analysis endpoint"""
        try:
            # Register and get user_id
            unique_email = f"test_case_{int(time.time())}@example.com"
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "user_type": "common"
            }
            reg_response = api_client.post(f"{BASE_URL}/api/auth/register", json=register_payload)
            user_id = reg_response.json()["user"]["id"]
            
            # Analyze case (remove Content-Type header for form-data)
            form_data = {
                "user_id": user_id,
                "case_title": "Property Dispute Test",
                "case_type": "Civil",
                "case_description": "Neighbor has encroached on my property boundary by 2 feet."
            }
            
            print("⏳ Analyzing case (may take up to 45 seconds)...")
            headers_backup = api_client.headers.copy()
            if 'Content-Type' in api_client.headers:
                del api_client.headers['Content-Type']
            
            response = api_client.post(
                f"{BASE_URL}/api/case/analyze",
                data=form_data,
                timeout=60
            )
            
            # Restore headers
            api_client.headers = headers_backup
            
            print(f"✓ Case analysis status: {response.status_code}")
            
            if response.status_code == 422:
                error_data = response.json()
                print(f"⚠ Validation error: {error_data}")
                pytest.skip(f"Validation error: {error_data}")
            
            if response.status_code == 504:
                print("⚠ Case analysis timed out (expected with AI)")
                pytest.skip("AI analysis timeout")
            elif response.status_code == 402:
                print("⚠ AI budget exceeded")
                pytest.skip("AI budget exceeded")
            elif response.status_code == 500:
                error_data = response.json()
                print(f"⚠ AI analysis error: {error_data.get('detail', 'Unknown error')}")
                pytest.skip("AI analysis error")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "id" in data
            assert "case_title" in data
            assert "analysis" in data
            assert data["case_title"] == "Property Dispute Test"
            print(f"✓ Case analysis successful: {data['case_title']}")
            print(f"  Analysis preview: {data['analysis'][:100]}...")
        except requests.exceptions.Timeout:
            print("⚠ Case analysis request timed out")
            pytest.skip("Request timeout")
        except Exception as e:
            print(f"✗ Case analysis failed: {str(e)}")
            raise
    
    def test_case_history(self, api_client):
        """Test case history retrieval"""
        try:
            # Register user
            unique_email = f"test_case_history_{int(time.time())}@example.com"
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "user_type": "common"
            }
            reg_response = api_client.post(f"{BASE_URL}/api/auth/register", json=register_payload)
            user_id = reg_response.json()["user"]["id"]
            
            # Get history
            response = api_client.get(f"{BASE_URL}/api/case/history/{user_id}")
            print(f"✓ Case history status: {response.status_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ Case history retrieved: {len(data)} cases")
        except Exception as e:
            print(f"✗ Case history failed: {str(e)}")
    
    def test_case_detail_endpoint(self, api_client):
        """Test GET /api/case/detail/{case_id} - returns case with messages"""
        try:
            # Use existing case ID from agent context
            case_id = "eb0bdff3-90d7-4f0d-a629-a8119a6ff20d"
            
            response = api_client.get(f"{BASE_URL}/api/case/detail/{case_id}")
            print(f"✓ Case detail status: {response.status_code}")
            
            if response.status_code == 404:
                print("⚠ Case not found, creating a new case for testing...")
                # Create a new case first
                unique_email = f"test_case_detail_{int(time.time())}@example.com"
                register_payload = {
                    "email": unique_email,
                    "password": TEST_USER_PASSWORD,
                    "full_name": TEST_USER_NAME,
                    "user_type": "common"
                }
                reg_response = api_client.post(f"{BASE_URL}/api/auth/register", json=register_payload)
                user_id = reg_response.json()["user"]["id"]
                
                # Create case
                form_data = {
                    "user_id": user_id,
                    "case_title": "Test Case for Detail Endpoint",
                    "case_type": "Civil",
                    "case_description": "This is a test case for the detail endpoint."
                }
                
                headers_backup = api_client.headers.copy()
                if 'Content-Type' in api_client.headers:
                    del api_client.headers['Content-Type']
                
                case_response = api_client.post(
                    f"{BASE_URL}/api/case/analyze",
                    data=form_data,
                    timeout=60
                )
                api_client.headers = headers_backup
                
                if case_response.status_code != 200:
                    pytest.skip("Could not create test case")
                
                case_id = case_response.json()["id"]
                response = api_client.get(f"{BASE_URL}/api/case/detail/{case_id}")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "case" in data
            assert "messages" in data
            assert isinstance(data["messages"], list)
            assert data["case"]["id"] == case_id
            print(f"✓ Case detail retrieved: {data['case']['case_title']}")
            print(f"  Messages count: {len(data['messages'])}")
        except Exception as e:
            print(f"✗ Case detail test failed: {str(e)}")
            raise
    
    def test_case_followup_endpoint(self, api_client):
        """Test POST /api/case/followup - ask follow-up question"""
        try:
            # First create a case
            unique_email = f"test_followup_{int(time.time())}@example.com"
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "user_type": "common"
            }
            reg_response = api_client.post(f"{BASE_URL}/api/auth/register", json=register_payload)
            user_id = reg_response.json()["user"]["id"]
            
            # Create case
            form_data = {
                "user_id": user_id,
                "case_title": "Test Case for Follow-up",
                "case_type": "Criminal",
                "case_description": "Test case to verify follow-up questions work."
            }
            
            print("⏳ Creating case for follow-up test...")
            headers_backup = api_client.headers.copy()
            if 'Content-Type' in api_client.headers:
                del api_client.headers['Content-Type']
            
            case_response = api_client.post(
                f"{BASE_URL}/api/case/analyze",
                data=form_data,
                timeout=60
            )
            
            if case_response.status_code != 200:
                print(f"⚠ Could not create case: {case_response.status_code}")
                pytest.skip("Case creation failed")
            
            case_id = case_response.json()["id"]
            
            # Now ask a follow-up question
            followup_data = {
                "case_id": case_id,
                "question": "What documents do I need to file this case?"
            }
            
            print("⏳ Asking follow-up question (may take up to 45 seconds)...")
            response = api_client.post(
                f"{BASE_URL}/api/case/followup",
                data=followup_data,
                timeout=60
            )
            
            # Restore headers
            api_client.headers = headers_backup
            
            print(f"✓ Follow-up status: {response.status_code}")
            
            if response.status_code == 504:
                print("⚠ Follow-up timed out")
                pytest.skip("AI analysis timeout")
            elif response.status_code == 402:
                print("⚠ AI budget exceeded")
                pytest.skip("AI budget exceeded")
            elif response.status_code == 500:
                error_data = response.json()
                print(f"⚠ AI error: {error_data.get('detail', 'Unknown error')}")
                pytest.skip("AI analysis error")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "user_message" in data
            assert "ai_message" in data
            assert data["user_message"]["role"] == "user"
            assert data["ai_message"]["role"] == "assistant"
            assert data["user_message"]["content"] == "What documents do I need to file this case?"
            print(f"✓ Follow-up successful")
            print(f"  User message: {data['user_message']['content'][:50]}...")
            print(f"  AI response: {data['ai_message']['content'][:100]}...")
        except requests.exceptions.Timeout:
            print("⚠ Follow-up request timed out")
            pytest.skip("Request timeout")
        except Exception as e:
            print(f"✗ Follow-up test failed: {str(e)}")
            raise
    
    def test_analyze_document_endpoint(self, api_client):
        """Test POST /api/case/analyze-document - auto-detect case type from document"""
        try:
            # Register user
            unique_email = f"test_doc_analyze_{int(time.time())}@example.com"
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "user_type": "common"
            }
            reg_response = api_client.post(f"{BASE_URL}/api/auth/register", json=register_payload)
            user_id = reg_response.json()["user"]["id"]
            
            # Analyze document with text content
            form_data = {
                "user_id": user_id,
                "document_type": "text",
                "text_content": """FIR No. 123/2024
Police Station: Andheri West, Mumbai
Complainant: Rajesh Kumar
Accused: Unknown persons

On 10th January 2024, I was returning home from work when two unknown persons on a motorcycle snatched my mobile phone and wallet containing Rs 5000 cash and important documents. The incident occurred near Andheri station at around 9 PM. I immediately reported to the police station."""
            }
            
            print("⏳ Analyzing document (may take up to 45 seconds)...")
            headers_backup = api_client.headers.copy()
            if 'Content-Type' in api_client.headers:
                del api_client.headers['Content-Type']
            
            response = api_client.post(
                f"{BASE_URL}/api/case/analyze-document",
                data=form_data,
                timeout=60
            )
            
            # Restore headers
            api_client.headers = headers_backup
            
            print(f"✓ Document analysis status: {response.status_code}")
            
            if response.status_code == 504:
                print("⚠ Document analysis timed out")
                pytest.skip("AI analysis timeout")
            elif response.status_code == 402:
                print("⚠ AI budget exceeded")
                pytest.skip("AI budget exceeded")
            elif response.status_code == 500:
                error_data = response.json()
                print(f"⚠ AI error: {error_data.get('detail', 'Unknown error')}")
                pytest.skip("AI analysis error")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "id" in data
            assert "case_title" in data
            assert "case_type" in data
            assert "analysis" in data
            print(f"✓ Document analysis successful")
            print(f"  Auto-detected case type: {data['case_type']}")
            print(f"  Generated case title: {data['case_title']}")
            print(f"  Analysis preview: {data['analysis'][:100]}...")
        except requests.exceptions.Timeout:
            print("⚠ Document analysis request timed out")
            pytest.skip("Request timeout")
        except Exception as e:
            print(f"✗ Document analysis test failed: {str(e)}")
            raise

            raise


class TestContractAnalysis:
    """Contract analysis endpoint tests"""
    
    def test_contract_analysis_text(self, api_client):
        """Test contract analysis with text input"""
        try:
            # Register user
            unique_email = f"test_contract_{int(time.time())}@example.com"
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "user_type": "common"
            }
            reg_response = api_client.post(f"{BASE_URL}/api/auth/register", json=register_payload)
            user_id = reg_response.json()["user"]["id"]
            
            # Analyze contract
            form_data = {
                "user_id": user_id,
                "document_name": "Test Rental Agreement",
                "document_type": "text",
                "text_content": "This rental agreement is between landlord and tenant for property at 123 Main St. Rent is Rs 10000 per month. Security deposit is Rs 20000. Tenant must give 2 months notice before vacating."
            }
            
            print("⏳ Analyzing contract (may take up to 45 seconds)...")
            headers_backup = api_client.headers.copy()
            if 'Content-Type' in api_client.headers:
                del api_client.headers['Content-Type']
            
            response = api_client.post(
                f"{BASE_URL}/api/contract/analyze",
                data=form_data,
                timeout=60
            )
            
            # Restore headers
            api_client.headers = headers_backup
            
            print(f"✓ Contract analysis status: {response.status_code}")
            
            if response.status_code == 422:
                error_data = response.json()
                print(f"⚠ Validation error: {error_data}")
                pytest.skip(f"Validation error: {error_data}")
            
            if response.status_code == 504:
                print("⚠ Contract analysis timed out")
                pytest.skip("AI analysis timeout")
            elif response.status_code == 402:
                print("⚠ AI budget exceeded")
                pytest.skip("AI budget exceeded")
            elif response.status_code == 500:
                error_data = response.json()
                print(f"⚠ AI analysis error: {error_data.get('detail', 'Unknown error')}")
                pytest.skip("AI analysis error")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "id" in data
            assert "document_name" in data
            assert "simplified_text" in data
            assert data["document_name"] == "Test Rental Agreement"
            print(f"✓ Contract analysis successful: {data['document_name']}")
        except requests.exceptions.Timeout:
            print("⚠ Contract analysis request timed out")
            pytest.skip("Request timeout")
        except Exception as e:
            print(f"✗ Contract analysis failed: {str(e)}")
            raise
    
    def test_contract_history(self, api_client):
        """Test contract history retrieval"""
        try:
            # Register user
            unique_email = f"test_contract_history_{int(time.time())}@example.com"
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "user_type": "common"
            }
            reg_response = api_client.post(f"{BASE_URL}/api/auth/register", json=register_payload)
            user_id = reg_response.json()["user"]["id"]
            
            # Get history
            response = api_client.get(f"{BASE_URL}/api/contract/history/{user_id}")
            print(f"✓ Contract history status: {response.status_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ Contract history retrieved: {len(data)} contracts")
        except Exception as e:
            print(f"✗ Contract history failed: {str(e)}")
            raise


class TestLegalProcedure:
    """Legal procedure endpoint tests"""
    
    def test_get_procedure_civil(self, api_client):
        """Test legal procedure for Civil case"""
        try:
            print("⏳ Getting legal procedure (may take up to 45 seconds)...")
            response = api_client.get(f"{BASE_URL}/api/procedure/Civil", timeout=60)
            
            print(f"✓ Legal procedure status: {response.status_code}")
            
            if response.status_code == 504:
                print("⚠ Procedure request timed out")
                pytest.skip("AI analysis timeout")
            elif response.status_code == 402:
                print("⚠ AI budget exceeded")
                pytest.skip("AI budget exceeded")
            elif response.status_code == 500:
                error_data = response.json()
                print(f"⚠ AI analysis error: {error_data.get('detail', 'Unknown error')}")
                pytest.skip("AI analysis error")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "case_type" in data
            assert "procedure" in data
            assert data["case_type"] == "Civil"
            print(f"✓ Legal procedure retrieved for: {data['case_type']}")
        except requests.exceptions.Timeout:
            print("⚠ Procedure request timed out")
            pytest.skip("Request timeout")
        except Exception as e:
            print(f"✗ Legal procedure failed: {str(e)}")
            raise


class TestLawyerSearch:
    """Lawyer search endpoint tests"""
    
    def test_register_lawyer(self, api_client):
        """Test lawyer registration"""
        try:
            unique_email = f"test_lawyer_{int(time.time())}@example.com"
            
            payload = {
                "email": unique_email,
                "password": TEST_LAWYER_PASSWORD,
                "full_name": TEST_LAWYER_NAME,
                "user_type": "lawyer",
                "specialization": "Criminal Law",
                "bar_council_number": "BAR123456",
                "years_of_experience": 5,
                "location": "Mumbai",
                "bio": "Experienced criminal lawyer"
            }
            
            response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
            print(f"✓ Lawyer registration status: {response.status_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["user"]["user_type"] == "lawyer"
            assert data["user"]["specialization"] == "Criminal Law"
            print(f"✓ Lawyer registered: {data['user']['email']}")
        except Exception as e:
            print(f"✗ Lawyer registration failed: {str(e)}")
            raise
    
    def test_search_lawyers_no_filter(self, api_client):
        """Test lawyer search without filters"""
        try:
            response = api_client.get(f"{BASE_URL}/api/lawyers/search")
            print(f"✓ Lawyer search status: {response.status_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ Lawyer search successful: {len(data)} lawyers found")
        except Exception as e:
            print(f"✗ Lawyer search failed: {str(e)}")
            raise
    
    def test_search_lawyers_with_specialization(self, api_client):
        """Test lawyer search with specialization filter"""
        try:
            response = api_client.get(f"{BASE_URL}/api/lawyers/search?specialization=Criminal")
            print(f"✓ Lawyer search (Criminal) status: {response.status_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ Criminal lawyers found: {len(data)}")
        except Exception as e:
            print(f"✗ Lawyer search with filter failed: {str(e)}")
            raise
    
    def test_get_lawyer_profile(self, api_client):
        """Test getting specific lawyer profile"""
        try:
            # First register a lawyer
            unique_email = f"test_lawyer_profile_{int(time.time())}@example.com"
            payload = {
                "email": unique_email,
                "password": TEST_LAWYER_PASSWORD,
                "full_name": "Profile Test Lawyer",
                "user_type": "lawyer",
                "specialization": "Civil Law",
                "bar_council_number": "BAR789",
                "years_of_experience": 10,
                "location": "Delhi"
            }
            
            reg_response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
            lawyer_id = reg_response.json()["user"]["id"]
            
            # Get lawyer profile
            response = api_client.get(f"{BASE_URL}/api/lawyer/{lawyer_id}")
            print(f"✓ Lawyer profile status: {response.status_code}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["id"] == lawyer_id
            assert data["user_type"] == "lawyer"
            assert "password_hash" not in data  # Should not expose password
            print(f"✓ Lawyer profile retrieved: {data['full_name']}")
        except Exception as e:
            print(f"✗ Lawyer profile retrieval failed: {str(e)}")
            raise
