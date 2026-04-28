from fastapi import APIRouter
from app.controllers import procedure_controller

router = APIRouter(prefix="/procedure", tags=["procedure"])

@router.get("/{case_type}")
async def get_legal_procedure(case_type: str):
    return await procedure_controller.get_legal_procedure(case_type)
