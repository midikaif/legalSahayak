from fastapi import HTTPException
import base64
from typing import Optional
from app.core.database import get_db
from app.services.ai_service import get_ai_analysis
from app.services.document_service import extract_text_from_pdf, extract_text_from_image
from app.schemas.contract import ContractAnalysis

async def analyze_contract(
    user_id: str,
    document_name: str,
    document_type: str,
    text_content: Optional[str],
    file_content: Optional[str],
    language: str
):
    db = get_db()
    original_text = ""
    
    if document_type == "text":
        original_text = text_content
    elif document_type == "pdf" and file_content:
        pdf_bytes = base64.b64decode(file_content.split('base64,')[1] if 'base64,' in file_content else file_content)
        original_text = await extract_text_from_pdf(pdf_bytes)
    elif document_type == "image" and file_content:
        original_text = await extract_text_from_image(file_content)
    
    if not original_text or len(original_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Could not extract text from document")
    
    lang_instruction = "Respond in Hinglish (Hindi words written in English script mixed with English). Make it conversational and easy to understand for a common Indian person." if language == "hinglish" else "Respond in clear, simple English."

    simplification_prompt = f"""Analyze this legal contract/document and provide a structured JSON response. Focus on identifying red flags, key obligations, and explaining legal jargon. Use **bold** markdown for important terms within the text.

{lang_instruction}

Document:
{original_text[:15000]}

Respond ONLY with valid JSON (no markdown code blocks, no extra text) with these exact keys:
{{
  "simplified_text": "A comprehensive summary of the contract in the requested language.",
  "risks": ["Red flag 1 with **bold** terms", "Hidden fee or risk 2"],
  "key_points": ["Obligation 1", "Key right 2"],
  "legal_terms": {{
    "Term 1": "Simple explanation",
    "Term 2": "Simple explanation"
  }}
}}"""
    
    analysis_result = await get_ai_analysis(simplification_prompt)
    
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

async def get_contract_history(user_id: str):
    db = get_db()
    contracts = await db.contract_analyses.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    for contract in contracts:
        contract.pop('_id', None)
    return contracts
