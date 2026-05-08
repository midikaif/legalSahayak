from fastapi import HTTPException
import base64
import json
import logging
from typing import Optional
from app.core.database import get_db
from app.services.ai_service import get_ai_analysis
from app.services.document_service import extract_text_from_pdf, extract_text_from_image
from app.schemas.case import CaseAnalysis, ChatMessage

logger = logging.getLogger(__name__)

async def analyze_case(user_id: str, case_title: str, case_type: str, case_description: str, language: str):
    db = get_db()
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
    
    analysis_result = await get_ai_analysis(analysis_prompt)
    
    case_analysis = CaseAnalysis(
        user_id=user_id,
        case_title=case_title,
        case_type=case_type,
        case_description=case_description,
        analysis=analysis_result
    )
    await db.case_analyses.insert_one(case_analysis.dict())
    
    result = case_analysis.dict()
    result.pop('_id', None)
    return result

async def get_case_history(user_id: str):
    db = get_db()
    cases = await db.case_analyses.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    for case in cases:
        case.pop('_id', None)
    return cases

async def get_case_detail(case_id: str):
    db = get_db()
    case = await db.case_analyses.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.pop('_id', None)
    
    messages = await db.case_messages.find({"case_id": case_id}).sort("created_at", 1).to_list(200)
    for msg in messages:
        msg.pop('_id', None)
    
    return {"case": case, "messages": messages}

async def case_followup(case_id: str, question: str):
    db = get_db()
    case = await db.case_analyses.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    user_msg = ChatMessage(case_id=case_id, role="user", content=question)
    await db.case_messages.insert_one(user_msg.dict())
    
    context = f"""Previous case analysis:
Case Title: {case.get('case_title', '')}
Case Type: {case.get('case_type', '')}
Description: {case.get('case_description', '')}

Previous AI Analysis (summary): {str(case.get('analysis', ''))[:2000]}"""
    
    prev_messages = await db.case_messages.find({"case_id": case_id}).sort("created_at", -1).to_list(10)
    chat_context = "\n".join([f"{m['role']}: {m['content'][:500]}" for m in reversed(prev_messages[-6:])])
    
    prompt = f"""Based on the case context and previous conversation, answer this follow-up question clearly and helpfully.

{context}

Recent conversation:
{chat_context}

User's question: {question}

Provide a clear, helpful answer focused on Indian law. Be specific and actionable."""
    
    ai_response = await get_ai_analysis(prompt)
    
    ai_msg = ChatMessage(case_id=case_id, role="assistant", content=ai_response)
    await db.case_messages.insert_one(ai_msg.dict())
    
    return {
        "user_message": user_msg.dict(),
        "ai_message": ai_msg.dict()
    }

async def analyze_case_from_document(user_id: str, document_type: str, text_content: Optional[str], file_content: Optional[str]):
    db = get_db()
    extracted_text = ""
    if document_type == "text" and text_content:
        extracted_text = text_content
    elif document_type == "pdf" and file_content:
        pdf_bytes = base64.b64decode(file_content.split('base64,')[1] if 'base64,' in file_content else file_content)
        extracted_text = await extract_text_from_pdf(pdf_bytes)
    elif document_type == "image" and file_content:
        extracted_text = await extract_text_from_image(file_content)
    
    if not extracted_text or len(extracted_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Could not extract text from the document. Try pasting the text directly.")
    
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
