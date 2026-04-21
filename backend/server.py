from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import base64
from io import BytesIO
from PIL import Image
import PyPDF2
import pytesseract
import asyncio
from contextlib import asynccontextmanager
from google.genai import types
import google.genai as genai

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT and Password Config
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AI Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    yield
    # Shutdown logic
    client.close()

# Create the main app
app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class UserType(str):
    COMMON = "common"
    LAWYER = "lawyer"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    full_name: str
    user_type: str  # "common" or "lawyer"
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Lawyer-specific fields
    specialization: Optional[str] = None
    bar_council_number: Optional[str] = None
    years_of_experience: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    rating: Optional[float] = 0.0
    cases_handled: Optional[int] = 0

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    user_type: str
    phone: Optional[str] = None
    specialization: Optional[str] = None
    bar_council_number: Optional[str] = None
    years_of_experience: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class ContractAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    document_name: str
    document_type: str  # "text", "pdf", "image"
    original_text: str
    simplified_text: Optional[str] = None
    key_points: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    legal_terms: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CaseAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    case_title: str
    case_type: str  # Civil, Criminal, Family, Property, etc.
    case_description: str
    analysis: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    strategy: Optional[List[str]] = None
    questions_for_lawyer: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LegalProcedure(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_type: str
    title: str
    steps: List[dict]  # [{step_number, description, timeline}]
    required_documents: List[str]
    court_hierarchy: List[str]
    estimated_timeline: str

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==================== HELPER FUNCTIONS ====================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

async def get_ai_analysis(prompt: str, context: str = "") -> str:
    """Get AI analysis using Gemini Flash (fast + affordable)"""
    try:
        logger.debug(f"🔑 Google API Key configured: {bool(GOOGLE_API_KEY)}")
        logger.debug(f"📏 Prompt length: {len(prompt)} characters")
        
        client = genai.Client(api_key=GOOGLE_API_KEY)
        logger.debug("✅ Genai Client created")
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        logger.debug(f"🎯 Sending to Gemini 2.5 Flash model...")
        
        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a senior Indian attorney with 25+ years of experience in criminal, civil, and corporate law. You specialize in IPC, CrPC, Indian Contract Act 1872, and landmark Supreme Court & High Court judgements. Always cite exact sections and relevant case precedents. Be precise, structured, and formal in legal drafting. When simplifying, use plain Indian English without losing legal accuracy."
                )
            ),
            timeout=45
        )
        
        logger.info(f"✨ AI response received ({len(response.text)} characters)")
        logger.debug(f"📊 Response preview: {response.text[:150]}...")
        return response.text
        
    except asyncio.TimeoutError:
        logger.error("⏰ AI analysis timed out after 45 seconds")
        raise HTTPException(status_code=504, detail="AI analysis timed out. Please try again.")
    except Exception as e:
        error_str = str(e)
        logger.error(f"❌ AI analysis error: {error_str}", exc_info=True)
        
        if "Budget" in error_str or "quota" in error_str.lower():
            logger.error("💳 API quota/budget issue detected")
            raise HTTPException(status_code=402, detail="AI budget exceeded. Please check your API quota.")
        
        if "API key" in error_str or "authentication" in error_str.lower():
            logger.error("🔐 API key authentication failed")
            raise HTTPException(status_code=401, detail="Google API key configuration error. Check your credentials.")
        
        logger.error(f"🚨 Unexpected error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {error_str}")

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF"""
    try:
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        return ""

def extract_text_from_image(image_base64: str) -> str:
    """Extract text from image using OCR"""
    try:
        # Remove base64 prefix if present
        if 'base64,' in image_base64:
            image_base64 = image_base64.split('base64,')[1]
        
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error(f"Image OCR error: {str(e)}")
        return ""

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_dict = user_data.dict()
    password = user_dict.pop('password')
    user_dict['password_hash'] = get_password_hash(password)
    
    user = User(**user_dict)
    await db.users.insert_one(user.dict())
    
    # Create token
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    user_response = user.dict()
    user_response.pop('password_hash')
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user['email'], "user_id": user['id']})
    
    user.pop('password_hash')
    user.pop('_id', None)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# ==================== CONTRACT ANALYSIS ROUTES ====================

@api_router.post("/contract/analyze")
async def analyze_contract(
    user_id: str = Form(...),
    document_name: str = Form(...),
    document_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    file_content: Optional[str] = Form(None)
):
    """Analyze a legal contract/document"""
    
    # Extract text based on document type
    original_text = ""
    
    if document_type == "text":
        original_text = text_content
    elif document_type == "pdf" and file_content:
        # Assume file_content is base64 encoded PDF
        pdf_bytes = base64.b64decode(file_content.split('base64,')[1] if 'base64,' in file_content else file_content)
        original_text = extract_text_from_pdf(pdf_bytes)
    elif document_type == "image" and file_content:
        original_text = extract_text_from_image(file_content)
    
    if not original_text or len(original_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Could not extract text from document")
    
    # AI Analysis
    simplification_prompt = f"""Analyze this legal document and provide:
1. A simplified version in plain Hindi/English that a common person can understand
2. Key points and important clauses
3. Potential risks or unfavorable terms
4. Legal terms explained in simple language

Document:
{original_text}

Provide the response in JSON format with keys: simplified_text, key_points (array), risks (array), legal_terms (object with term as key and explanation as value)"""
    
    analysis_result = await get_ai_analysis(simplification_prompt)
    
    # Parse AI response (simplified - in production, use proper JSON parsing)
    contract_analysis = ContractAnalysis(
        user_id=user_id,
        document_name=document_name,
        document_type=document_type,
        original_text=original_text,
        simplified_text=analysis_result
    )
    
    await db.contract_analyses.insert_one(contract_analysis.dict())
    
    result = contract_analysis.dict()
    result.pop('_id', None)
    
    return result

@api_router.get("/contract/history/{user_id}")
async def get_contract_history(user_id: str):
    """Get contract analysis history for a user"""
    contracts = await db.contract_analyses.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    
    for contract in contracts:
        contract.pop('_id', None)
    
    return contracts

# ==================== CASE ANALYSIS ROUTES ====================

@api_router.post("/case/analyze")
async def analyze_case(
    user_id: str = Form(...),
    case_title: str = Form(...),
    case_type: str = Form(...),
    case_description: str = Form(...),
    language: str = Form("english")
):
    """Analyze a legal case and provide strategy"""
    
    # DEBUG: Log incoming request
    logger.info(f"📨 Received case analysis request - User: {user_id}, Case: {case_title}")
    
    lang_instruction = "Respond in Hinglish (Hindi words written in English script mixed with English). Make it conversational and easy to understand for a common Indian person." if language == "hinglish" else "Respond in clear, simple English."
    
    analysis_prompt = f"""As an expert in Indian law, analyze this case:

Case Type: {case_type}
Title: {case_title}
Description: {case_description}

{lang_instruction}

Provide a detailed, engaging analysis. Use bold (**text**) for important terms. Make it interesting to read, not boring legal jargon.

Respond ONLY with valid JSON (no markdown code blocks) with these exact keys:
{{
  "analysis": "detailed analysis text with **bold** for key terms",
  "strengths": ["point1", "point2"],
  "weaknesses": ["point1", "point2"],
  "strategy": ["step1", "step2"],
  "questions_for_lawyer": ["q1", "q2"],
  "loopholes": ["point1", "point2"]
}}"""
    
    logger.debug(f"📝 Analysis prompt created (length: {len(analysis_prompt)})")
    
    try:
        # DEBUG: Log before calling AI
        logger.info("🤖 Calling AI analysis...")
        analysis_result = await get_ai_analysis(analysis_prompt)
        logger.info(f"✅ AI analysis successful (response length: {len(analysis_result)})")
        logger.debug(f"📄 AI response preview: {analysis_result[:200]}...")
        
        # DEBUG: Log before creating case object
        logger.info("📋 Creating case analysis object...")
        case_analysis = CaseAnalysis(
            user_id=user_id,
            case_title=case_title,
            case_type=case_type,
            case_description=case_description,
            analysis=analysis_result
        )
        logger.info(f"✅ Case object created: {case_analysis.id}")
        
        # DEBUG: Log before database insert
        logger.info("💾 Inserting case into database...")
        await db.case_analyses.insert_one(case_analysis.dict())
        logger.info(f"✅ Case saved to database: {case_analysis.id}")
        
        result = case_analysis.dict()
        result.pop('_id', None)
        
        logger.info(f"✨ Case analysis complete and returned")
        return result
    
    except Exception as e:
        logger.error(f"❌ Error in case analysis: {str(e)}", exc_info=True)
        raise

@api_router.get("/case/history/{user_id}")
async def get_case_history(user_id: str):
    """Get case analysis history for a user"""
    cases = await db.case_analyses.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    
    for case in cases:
        case.pop('_id', None)
    
    return cases

@api_router.get("/case/detail/{case_id}")
async def get_case_detail(case_id: str):
    """Get a single case with its chat messages"""
    case = await db.case_analyses.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.pop('_id', None)
    
    messages = await db.case_messages.find({"case_id": case_id}).sort("created_at", 1).to_list(200)
    for msg in messages:
        msg.pop('_id', None)
    
    return {"case": case, "messages": messages}

@api_router.post("/case/followup")
async def case_followup(case_id: str = Form(...), question: str = Form(...)):
    """Ask a follow-up question about an existing case"""
    case = await db.case_analyses.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Save user message
    user_msg = ChatMessage(case_id=case_id, role="user", content=question)
    await db.case_messages.insert_one(user_msg.dict())
    
    # Build context from case
    context = f"""Previous case analysis:
Case Title: {case.get('case_title', '')}
Case Type: {case.get('case_type', '')}
Description: {case.get('case_description', '')}

Previous AI Analysis (summary): {str(case.get('analysis', ''))[:2000]}"""
    
    # Get previous messages for context
    prev_messages = await db.case_messages.find({"case_id": case_id}).sort("created_at", -1).to_list(10)
    chat_context = "\n".join([f"{'User' if m['role']=='user' else 'AI'}: {m['content'][:500]}" for m in reversed(prev_messages[-6:])])
    
    prompt = f"""Based on the case context and previous conversation, answer this follow-up question clearly and helpfully.

{context}

Recent conversation:
{chat_context}

User's question: {question}

Provide a clear, helpful answer focused on Indian law. Be specific and actionable."""
    
    ai_response = await get_ai_analysis(prompt)
    
    # Save AI message
    ai_msg = ChatMessage(case_id=case_id, role="assistant", content=ai_response)
    await db.case_messages.insert_one(ai_msg.dict())
    
    return {
        "user_message": user_msg.dict(),
        "ai_message": ai_msg.dict()
    }

@api_router.post("/case/analyze-document")
async def analyze_case_from_document(
    user_id: str = Form(...),
    document_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    file_content: Optional[str] = Form(None)
):
    """Analyze a case from uploaded legal documents (FIR, court reports, etc.)"""
    
    # Extract text from document
    extracted_text = ""
    if document_type == "text" and text_content:
        extracted_text = text_content
    elif document_type == "pdf" and file_content:
        pdf_bytes = base64.b64decode(file_content.split('base64,')[1] if 'base64,' in file_content else file_content)
        extracted_text = extract_text_from_pdf(pdf_bytes)
    elif document_type == "image" and file_content:
        extracted_text = extract_text_from_image(file_content)
    
    if not extracted_text or len(extracted_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Could not extract text from the document. Try pasting the text directly.")
    
    # AI auto-detect case type and analyze
    detect_prompt = f"""You are an expert Indian legal assistant. A user has uploaded a legal document. 
Analyze this document and:

1. Detect what type of document this is (FIR, Court Order, Legal Notice, Agreement, etc.)
2. Auto-detect the case type (Civil, Criminal, Family, Property, Consumer, Labor, Tax, Corporate, Other)
3. Generate a suitable case title
4. Provide a full case analysis

Document text:
{extracted_text[:5000]}

Respond ONLY with valid JSON (no markdown, no code blocks) with these exact keys:
{{
  "detected_document_type": "...",
  "case_type": "...",
  "case_title": "...",
  "analysis": "detailed analysis text",
  "strengths": ["point1", "point2"],
  "weaknesses": ["point1", "point2"],
  "strategy": ["step1", "step2"],
  "questions_for_lawyer": ["q1", "q2"],
  "loopholes": ["point1", "point2"]
}}"""
    
    analysis_result = await get_ai_analysis(detect_prompt)
    
    # Try to parse JSON from response
    import json
    parsed = None
    try:
        cleaned = analysis_result.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.split('\n', 1)[1] if '\n' in cleaned else cleaned[3:]
            cleaned = cleaned.rsplit('```', 1)[0]
        parsed = json.loads(cleaned)
    except Exception:
        parsed = None
    
    case_title = parsed.get("case_title", "Document Analysis") if parsed else "Document Analysis"
    case_type = parsed.get("case_type", "Other") if parsed else "Other"
    
    case_analysis = CaseAnalysis(
        user_id=user_id,
        case_title=case_title,
        case_type=case_type,
        case_description=f"[Auto-analyzed from uploaded {document_type} document]",
        analysis=analysis_result
    )
    
    await db.case_analyses.insert_one(case_analysis.dict())
    
    result = case_analysis.dict()
    result.pop('_id', None)
    
    return result

# ==================== LEGAL PROCEDURE ROUTES ====================

@api_router.get("/procedure/{case_type}")
async def get_legal_procedure(case_type: str):
    """Get step-by-step legal procedure for a case type"""
    
    procedure_prompt = f"""Provide a detailed step-by-step legal procedure for a {case_type} case in India.

Write in an engaging, easy-to-understand way. Use **bold** for important terms.

Respond ONLY with valid JSON (no markdown code blocks) with these exact keys:
{{
  "steps": [
    {{"step_number": 1, "description": "Step description with **bold** key terms", "timeline": "1-2 weeks"}},
    {{"step_number": 2, "description": "Next step...", "timeline": "2-4 weeks"}}
  ],
  "required_documents": ["Document 1", "Document 2"],
  "court_hierarchy": ["Court 1 handles X", "Court 2 handles Y"],
  "estimated_timeline": "6 months to 2 years overall",
  "important_acts": ["Act 1 - what it covers", "Act 2"]
}}"""
    
    procedure_result = await get_ai_analysis(procedure_prompt)
    
    return {
        "case_type": case_type,
        "procedure": procedure_result
    }

# ==================== LAWYER ROUTES ====================

@api_router.get("/lawyers/search")
async def search_lawyers(
    specialization: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[int] = None
):
    """Search for lawyers based on criteria"""
    
    query = {"user_type": "lawyer"}
    
    if specialization:
        query["specialization"] = {"$regex": specialization, "$options": "i"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if min_experience:
        query["years_of_experience"] = {"$gte": min_experience}
    
    lawyers = await db.users.find(query).sort("rating", -1).to_list(100)
    
    for lawyer in lawyers:
        lawyer.pop('_id', None)
        lawyer.pop('password_hash', None)
    
    return lawyers

@api_router.get("/lawyer/{lawyer_id}")
async def get_lawyer_profile(lawyer_id: str):
    """Get detailed lawyer profile"""
    
    lawyer = await db.users.find_one({"id": lawyer_id, "user_type": "lawyer"})
    
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    lawyer.pop('_id', None)
    lawyer.pop('password_hash', None)
    
    return lawyer

# ==================== GENERAL ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "LegalSahayak API - Your Legal Assistant"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)