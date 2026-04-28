from fastapi import APIRouter, Form
from typing import Optional
from app.controllers import case_controller

router = APIRouter(prefix="/case", tags=["case"])

@router.post("/analyze")
async def analyze_case(
    user_id: str = Form(...),
    case_title: str = Form(...),
    case_type: str = Form(...),
    case_description: str = Form(...),
    language: str = Form("english")
):
    return await case_controller.analyze_case(user_id, case_title, case_type, case_description, language)

@router.get("/history/{user_id}")
async def get_case_history(user_id: str):
    return await case_controller.get_case_history(user_id)

@router.get("/detail/{case_id}")
async def get_case_detail(case_id: str):
    return await case_controller.get_case_detail(case_id)

@router.post("/followup")
async def case_followup(case_id: str = Form(...), question: str = Form(...)):
    return await case_controller.case_followup(case_id, question)

@router.post("/analyze-document")
async def analyze_case_from_document(
    user_id: str = Form(...),
    document_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    file_content: Optional[str] = Form(None)
):
    return await case_controller.analyze_case_from_document(user_id, document_type, text_content, file_content)
