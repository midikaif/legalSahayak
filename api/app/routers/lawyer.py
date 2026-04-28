from fastapi import APIRouter
from typing import Optional
from app.controllers import lawyer_controller

router = APIRouter(prefix="/lawyer", tags=["lawyer"])

@router.get("/search")
async def search_lawyers(
    specialization: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[int] = None
):
    return await lawyer_controller.search_lawyers(specialization, location, min_experience)

@router.get("/{lawyer_id}")
async def get_lawyer_profile(lawyer_id: str):
    return await lawyer_controller.get_lawyer_profile(lawyer_id)
