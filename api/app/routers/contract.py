from fastapi import APIRouter, Form
from typing import Optional
from app.controllers import contract_controller

router = APIRouter(prefix="/contract", tags=["contract"])

@router.post("/analyze")
async def analyze_contract(
    user_id: str = Form(...),
    document_name: str = Form(...),
    document_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    file_content: Optional[str] = Form(None),
    language: str = Form("english")
):
    return await contract_controller.analyze_contract(
        user_id, document_name, document_type, text_content, file_content, language
    )

@router.get("/history/{user_id}")
async def get_contract_history(user_id: str):
    return await contract_controller.get_contract_history(user_id)
